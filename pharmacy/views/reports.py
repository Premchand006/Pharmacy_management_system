"""Reports, statutory registers and GST summaries. Each table has a CSV export."""
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

from flask import Blueprint, render_template, request

from ..auth import admin_required, staff_required
from ..extensions import db
from ..models import (PRESCRIPTION_SCHEDULES, AuditLog, Batch, Product, Purchase, Sale, SaleItem,
                      Supplier, day_start_utc, local_today, to_local)
from . import arg_date, csv_response, month_bounds

bp = Blueprint("reports", __name__, url_prefix="/staff/reports")


def _range(default_days=30):
    today = local_today()
    start = arg_date("from", today - timedelta(days=default_days))
    end = arg_date("to", today)
    return start, end, day_start_utc(start), day_start_utc(end + timedelta(days=1))


def _wants_csv():
    return request.args.get("format") == "csv"


@bp.route("/")
@staff_required
def overview():
    today = local_today()
    stock = (db.session.query(Product.brand_name, Product.strength, Product.medicine_name,
                              db.func.coalesce(db.func.sum(Batch.qty_available), 0).label("qty"),
                              db.func.min(Batch.expiry_date).label("nearest"))
             .outerjoin(Batch, db.and_(Batch.p_id == Product.p_id, Batch.qty_available > 0,
                                       Batch.expiry_date >= today))
             .filter(Product.is_active.is_(True)).group_by(Product.p_id).order_by(Product.brand_name).all())
    near = (Batch.query.join(Product).filter(Batch.qty_available > 0, Batch.expiry_date >= today,
                                             Batch.expiry_date <= today + timedelta(days=30))
            .order_by(Batch.expiry_date).all())
    since = day_start_utc(today - timedelta(days=90))
    top = (db.session.query(SaleItem.item_name, db.func.sum(SaleItem.qty).label("qty"),
                            db.func.sum(SaleItem.line_total).label("value"))
           .join(Sale).filter(Sale.status == "completed", Sale.sold_at >= since)
           .group_by(SaleItem.p_id, SaleItem.item_name).order_by(db.desc("qty")).limit(10).all())
    if _wants_csv():
        return csv_response("stock.csv", ["Product", "Strength", "Generic", "Units in stock", "Nearest expiry"],
                            [(r.brand_name, r.strength, r.medicine_name, r.qty, r.nearest or "") for r in stock])
    return render_template("reports/overview.html", stock=stock, near=near, top=top)


@bp.route("/trace")
@staff_required
def trace():
    batch_no = request.args.get("batch", "").strip()
    batches = []
    if batch_no:
        batches = Batch.query.filter(Batch.batch_no.ilike(batch_no)).all()
    return render_template("reports/trace.html", batch_no=batch_no, batches=batches)


@bp.route("/register")
@staff_required
def register():
    """Prescription register (Rule 65(3)) and the separate H1 register."""
    start, end, lo, hi = _range()
    schedule = request.args.get("schedule", "H1")
    wanted = PRESCRIPTION_SCHEDULES if schedule == "ALL" else {schedule}
    rows = (db.session.query(SaleItem, Sale).join(Sale)
            .filter(Sale.status == "completed", Sale.sold_at >= lo, Sale.sold_at < hi,
                    SaleItem.schedule.in_(wanted))
            .order_by(Sale.sold_at, SaleItem.line_no).all())
    if _wants_csv():
        return csv_response(
            f"register-{schedule}-{start}-{end}.csv",
            ["Date", "Invoice", "Patient", "Patient address", "Prescriber", "Prescriber reg. no.",
             "Prescriber address", "Drug", "Schedule", "Qty", "Batch", "Expiry", "Manufacturer", "Pharmacist"],
            [(to_local(s.sold_at).strftime("%Y-%m-%d"), s.invoice_no, s.patient_name, s.patient_address,
              s.prescriber_name, s.prescriber_reg_no, s.prescriber_address, i.item_name, i.schedule, i.qty,
              i.batch.batch_no, i.batch.expiry_date, i.batch.manufacturer_name,
              s.pharmacist.name if s.pharmacist else "") for i, s in rows])
    return render_template("reports/register.html", rows=rows, start=start, end=end, schedule=schedule)


@bp.route("/schedule-x")
@staff_required
def schedule_x():
    """Per-drug Schedule X register with receipts, supplies and running balance (Rule 65(21))."""
    start, end, lo, hi = _range(90)
    pages = []
    for product in Product.query.filter(Product.schedule == "X").order_by(Product.brand_name):
        events = []
        for b in Batch.query.filter(Batch.p_id == product.p_id):
            events.append(dict(day=b.received_on, kind="Received", qty=b.qty_received, batch=b,
                               who=f"{b.supplier.firm_name} (licence {b.supplier.drug_licence})", ref=""))
        for item, sale in (db.session.query(SaleItem, Sale).join(Sale)
                           .filter(SaleItem.p_id == product.p_id, Sale.status == "completed")):
            events.append(dict(day=to_local(sale.sold_at).date(), kind="Supplied", qty=-item.qty,
                               batch=item.batch, who=f"{sale.patient_name}, {sale.patient_address}",
                               ref=f"{sale.invoice_no} / Rx {sale.pres_id or '-'} / {sale.prescriber_name}"))
        events.sort(key=lambda e: (e["day"], e["kind"] != "Received"))
        balance = sum(e["qty"] for e in events if e["day"] < start)
        opening, shown = balance, []
        for e in events:
            if start <= e["day"] <= end:
                balance += e["qty"]
                shown.append(dict(e, balance=balance))
        pages.append(dict(product=product, opening=opening, rows=shown, closing=balance))
    return render_template("reports/schedule_x.html", pages=pages, start=start, end=end)


@bp.route("/purchases")
@staff_required
def purchase_register():
    """Purchase record (Rule 65(4)(4)): supplier, licence, drug, batch, qty."""
    start, end, _, _ = _range()
    rows = (db.session.query(Batch, Purchase, Supplier, Product)
            .join(Purchase, Batch.purchase_id == Purchase.purchase_id)
            .join(Supplier, Purchase.s_id == Supplier.s_id).join(Product, Batch.p_id == Product.p_id)
            .filter(Purchase.received_on >= start, Purchase.received_on <= end)
            .order_by(Purchase.received_on, Purchase.purchase_id).all())
    if _wants_csv():
        return csv_response(f"purchases-{start}-{end}.csv",
                            ["Received", "Supplier", "Supplier licence", "Supplier GSTIN", "Invoice no.",
                             "Invoice date", "Drug", "Batch", "Expiry", "Manufacturer", "Qty", "Cost"],
                            [(p.received_on, s.firm_name, s.drug_licence, s.gstin, p.supplier_invoice_no,
                              p.invoice_date, pr.label, b.batch_no, b.expiry_date, b.manufacturer_name,
                              b.qty_received, b.cost_price) for b, p, s, pr in rows])
    return render_template("reports/purchase_register.html", rows=rows, start=start, end=end)


@bp.route("/gst")
@staff_required
def gst():
    """Monthly figures for GSTR-1: rate-wise B2C, B2B invoices, HSN summary, documents issued."""
    try:
        month = datetime.strptime(request.args.get("month", ""), "%Y-%m").date()
    except ValueError:
        month = local_today().replace(day=1)
    first, nxt = month_bounds(month)
    lo, hi = day_start_utc(first), day_start_utc(nxt)
    sales = Sale.query.filter(Sale.sold_at >= lo, Sale.sold_at < hi).order_by(Sale.seq).all()
    done = [s for s in sales if s.status == "completed"]

    zero = lambda: dict(taxable=Decimal(0), cgst=Decimal(0), sgst=Decimal(0), qty=0, value=Decimal(0))
    by_rate, by_hsn = defaultdict(zero), defaultdict(zero)
    for s in done:
        if s.buyer_gstin:
            continue  # B2B invoices are reported one by one below
        for i in s.items:
            for bucket in (by_rate[i.gst_rate], by_hsn[(i.hsn_code, i.gst_rate)]):
                bucket["taxable"] += i.taxable_value
                bucket["cgst"] += i.cgst
                bucket["sgst"] += i.sgst
                bucket["qty"] += i.qty
                bucket["value"] += i.line_total
    for s in done:
        if s.buyer_gstin:
            for i in s.items:
                b = by_hsn[(i.hsn_code, i.gst_rate)]
                b["taxable"] += i.taxable_value
                b["cgst"] += i.cgst
                b["sgst"] += i.sgst
                b["qty"] += i.qty
                b["value"] += i.line_total
    b2b = [s for s in done if s.buyer_gstin]
    docs = dict(first=sales[0].invoice_no if sales else "", last=sales[-1].invoice_no if sales else "",
                total=len(sales), cancelled=sum(1 for s in sales if s.status == "void"))

    kind = request.args.get("export")
    if kind == "hsn":
        return csv_response(f"gstr1-hsn-{month:%Y-%m}.csv",
                            ["HSN", "UQC", "Total quantity", "Total value", "Rate", "Taxable value",
                             "Integrated tax", "Central tax", "State/UT tax", "Cess"],
                            [(h, "NOS", v["qty"], v["value"], r, v["taxable"], 0, v["cgst"], v["sgst"], 0)
                             for (h, r), v in sorted(by_hsn.items())])
    if kind == "b2cs":
        return csv_response(f"gstr1-b2cs-{month:%Y-%m}.csv",
                            ["Type", "Rate", "Taxable value", "Central tax", "State/UT tax", "Cess"],
                            [("OE", r, v["taxable"], v["cgst"], v["sgst"], 0) for r, v in sorted(by_rate.items())])
    if kind == "b2b":
        return csv_response(f"gstr1-b2b-{month:%Y-%m}.csv",
                            ["Buyer GSTIN", "Invoice no.", "Date", "Invoice value", "Taxable value",
                             "Central tax", "State/UT tax"],
                            [(s.buyer_gstin, s.invoice_no, to_local(s.sold_at).strftime("%d-%m-%Y"), s.total,
                              s.taxable_total, s.cgst_total, s.sgst_total) for s in b2b])
    return render_template("reports/gst.html", month=month, by_rate=sorted(by_rate.items()),
                           by_hsn=sorted(by_hsn.items()), b2b=b2b, docs=docs)


@bp.route("/audit")
@admin_required
def audit_log():
    page = max(request.args.get("page", 1, type=int) or 1, 1)
    entity = request.args.get("entity", "")
    query = AuditLog.query
    if entity:
        query = query.filter(AuditLog.entity == entity)
    rows = query.order_by(AuditLog.id.desc()).offset((page - 1) * 100).limit(101).all()
    entities = [e for (e,) in db.session.query(AuditLog.entity).distinct().order_by(AuditLog.entity)]
    return render_template("reports/audit.html", rows=rows[:100], has_more=len(rows) > 100,
                           page=page, entity=entity, entities=entities)
