"""Counter billing: batch allocation, GST and invoice numbering.

Prices on an Indian medicine strip are MRP, inclusive of GST. The taxable
value is backed out of the discounted MRP:

    net      = MRP x qty - discount
    taxable  = net / (1 + rate / 100)
    CGST     = SGST = (net - taxable) / 2

Stock is taken from the batch that expires first (FEFO). Expired batches
are never sold (Drugs Rules, Rule 65(17)).
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from . import audit
from .extensions import db
from .models import (PAYMENT_MODES, Batch, Employee, PharmacySettings, Product, Sale,
                     SaleItem, local_today, utcnow)

CENT = Decimal("0.01")


class BillingError(ValueError):
    pass


def q2(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def financial_year(day):
    """Indian financial year label, April to March: 2026-11-20 -> '2026-27'."""
    start = day.year if day.month >= 4 else day.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def split_tax(net, rate, composition=False):
    """Return (taxable, cgst, sgst) for an MRP-inclusive amount."""
    net = q2(net)
    if composition or not rate:
        return net, Decimal("0.00"), Decimal("0.00")
    taxable = q2(net / (1 + Decimal(rate) / 100))
    tax = net - taxable
    cgst = q2(tax / 2)
    return taxable, cgst, tax - cgst


def sellable_batches(product_id, today=None, lock=False):
    today = today or local_today()
    q = (Batch.query.filter(Batch.p_id == product_id, Batch.qty_available > 0,
                            Batch.expiry_date >= today)
         .order_by(Batch.expiry_date, Batch.b_id))
    if lock:
        q = q.with_for_update()
    return q.all()


def allocate(product, qty, today=None):
    """Pick batches for qty units, earliest expiry first."""
    picks, need = [], qty
    for batch in sellable_batches(product.p_id, today, lock=True):
        take = min(need, batch.qty_available)
        picks.append((batch, take))
        need -= take
        if need == 0:
            return picks
    have = qty - need
    raise BillingError(f"Only {have} unexpired unit(s) of {product.label} in stock.")


@dataclass
class SaleRequest:
    lines: list                      # [(product_id, qty), ...]
    billed_by: Employee
    payment_mode: str = "Cash"
    discount_pct: Decimal = Decimal("0")
    customer: object = None
    prescription: object = None
    pharmacist: object = None
    patient_name: str = ""
    patient_address: str = ""
    prescriber_name: str = ""
    prescriber_reg_no: str = ""
    prescriber_address: str = ""
    buyer_gstin: str = ""
    today: date = field(default_factory=local_today)


def _fill_from_records(req):
    if req.prescription is not None:
        p = req.prescription
        if req.customer is not None and p.c_id != req.customer.c_id:
            raise BillingError("That prescription belongs to a different customer.")
        req.customer = req.customer or p.customer
        req.prescriber_name = req.prescriber_name or p.doctor_name
        req.prescriber_reg_no = req.prescriber_reg_no or p.doctor_reg_no
        req.prescriber_address = req.prescriber_address or p.doctor_address
        if p.times_dispensed > p.repeats_allowed:
            raise BillingError("This prescription has already been dispensed the number of "
                               "times the doctor allowed.")
    if req.customer is not None:
        req.patient_name = req.patient_name or req.customer.name
        req.patient_address = req.patient_address or req.customer.address


def _check_prescription_rules(req, products, settings):
    scheduled = [p for p in products if p.needs_prescription]
    if not scheduled:
        return
    missing = [label for label, value in (
        ("patient name", req.patient_name), ("patient address", req.patient_address),
        ("prescriber name", req.prescriber_name), ("prescriber registration no.", req.prescriber_reg_no),
        ("prescriber address", req.prescriber_address)) if not value.strip()]
    if missing:
        names = ", ".join(p.label for p in scheduled)
        raise BillingError(f"{names} need a prescription. Missing: {', '.join(missing)}.")
    if any(p.schedule == "X" for p in scheduled) and not settings.licence_20f:
        raise BillingError("Schedule X drugs need a Form 20F licence. Add it in Settings first.")
    if req.pharmacist is None and req.billed_by.is_pharmacist:
        req.pharmacist = req.billed_by
    if req.pharmacist is None or not req.pharmacist.is_pharmacist:
        raise BillingError("A registered pharmacist must be recorded for prescription drugs.")


def create_sale(req):
    """Validate, allocate stock and write the invoice. Caller commits."""
    if req.payment_mode not in PAYMENT_MODES:
        raise BillingError("Choose a payment mode.")
    pct = Decimal(req.discount_pct or 0)
    if pct < 0 or pct > 100:
        raise BillingError("Discount must be between 0 and 100 percent.")

    merged = {}
    for pid, qty in req.lines:
        if qty <= 0:
            raise BillingError("Quantities must be at least 1.")
        merged[pid] = merged.get(pid, 0) + qty
    if not merged:
        raise BillingError("Add at least one item.")

    products = []
    for pid in merged:
        product = db.session.get(Product, pid)
        if product is None or not product.is_active:
            raise BillingError("One of the items is no longer sold.")
        products.append(product)

    settings = PharmacySettings.get()
    _fill_from_records(req)
    _check_prescription_rules(req, products, settings)

    fy = financial_year(req.today)
    seq = (db.session.query(db.func.max(Sale.seq)).filter(Sale.financial_year == fy).scalar() or 0) + 1
    sale = Sale(
        invoice_no=f"{settings.invoice_prefix}/{fy}/{seq:05d}", financial_year=fy, seq=seq,
        sold_at=utcnow(), e_id=req.billed_by.e_id,
        pharmacist_id=req.pharmacist.e_id if req.pharmacist else None,
        c_id=req.customer.c_id if req.customer else None,
        pres_id=req.prescription.pres_id if req.prescription else None,
        patient_name=req.patient_name.strip(), patient_address=req.patient_address.strip(),
        prescriber_name=req.prescriber_name.strip(), prescriber_reg_no=req.prescriber_reg_no.strip(),
        prescriber_address=req.prescriber_address.strip(), buyer_gstin=req.buyer_gstin.strip().upper(),
        payment_mode=req.payment_mode,
    )
    db.session.add(sale)

    totals = dict(gross=Decimal(0), disc=Decimal(0), taxable=Decimal(0), cgst=Decimal(0), sgst=Decimal(0))
    line_no = 0
    for product in products:
        for batch, qty in allocate(product, merged[product.p_id], req.today):
            line_no += 1
            gross = q2(Decimal(batch.mrp) * qty)
            disc = q2(gross * pct / 100)
            taxable, cgst, sgst = split_tax(gross - disc, product.gst_rate, settings.composition_scheme)
            sale.items.append(SaleItem(
                line_no=line_no, p_id=product.p_id, b_id=batch.b_id, item_name=product.label,
                schedule=product.schedule, hsn_code=product.hsn_code, qty=qty, mrp=batch.mrp,
                discount=disc, gst_rate=0 if settings.composition_scheme else product.gst_rate,
                taxable_value=taxable, cgst=cgst, sgst=sgst, line_total=gross - disc))
            batch.qty_available -= qty
            totals["gross"] += gross
            totals["disc"] += disc
            totals["taxable"] += taxable
            totals["cgst"] += cgst
            totals["sgst"] += sgst

    net = totals["gross"] - totals["disc"]
    rounded = net.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    sale.gross_total, sale.discount_total = totals["gross"], totals["disc"]
    sale.taxable_total, sale.cgst_total, sale.sgst_total = totals["taxable"], totals["cgst"], totals["sgst"]
    sale.round_off, sale.total = rounded - net, rounded
    db.session.flush()
    return sale


def void_sale(sale, reason, user):
    """Cancel an invoice and put its stock back. The invoice stays on file."""
    if sale.status != "completed":
        raise BillingError("This invoice is already void.")
    if not reason.strip():
        raise BillingError("Give a reason for voiding the invoice.")
    for item in sale.items:
        item.batch.qty_available += item.qty
    sale.status = "void"
    sale.void_reason = reason.strip()
    sale.voided_at = utcnow()
    sale.voided_by_id = user.e_id
    audit.record(db.session, "void", "Sale", sale.sb_id, {"reason": sale.void_reason})
