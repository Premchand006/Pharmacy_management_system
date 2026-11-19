"""Billing counter, invoices and voids."""
import json
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, g, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from ..auth import staff_required
from ..billing import BillingError, SaleRequest, create_sale, sellable_batches, void_sale
from ..extensions import db
from ..models import (PAYMENT_MODES, Customer, Employee, Prescription, Product, Sale,
                      day_start_utc, local_today)
from ..views import arg_date

bp = Blueprint("sales", __name__, url_prefix="/staff/sales")


def _product_json(product, today):
    batches = sellable_batches(product.p_id, today)
    return {
        "id": product.p_id,
        "label": product.label,
        "generic": product.medicine_name,
        "packing": product.packing,
        "schedule": product.schedule,
        "needs_rx": product.needs_prescription,
        "gst": str(product.gst_rate),
        "mrp": str(batches[0].mrp if batches else product.mrp),
        "stock": sum(b.qty_available for b in batches),
        "expiry": batches[0].expiry_date.strftime("%m/%Y") if batches else "",
    }


@bp.route("/products.json")
@staff_required
def product_search():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    today = local_today()
    exact = Product.query.filter(Product.barcode == q, Product.is_active.is_(True)).first()
    if exact:
        return jsonify([_product_json(exact, today)])
    like = f"%{q}%"
    rows = (Product.query.filter(Product.is_active.is_(True),
                                 db.or_(Product.brand_name.ilike(like), Product.medicine_name.ilike(like)))
            .order_by(Product.brand_name).limit(15).all())
    return jsonify([_product_json(p, today) for p in rows])


@bp.route("/customers.json")
@staff_required
def customer_search():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    filters = [Customer.name.ilike(f"%{q}%"), Customer.phone.ilike(f"%{q}%")]
    if q.isdigit():
        filters.append(Customer.c_id == int(q))
    rows = Customer.query.filter(Customer.is_active.is_(True), db.or_(*filters)).limit(10).all()
    return jsonify([{"id": c.c_id, "name": c.name, "phone": c.phone, "address": c.address} for c in rows])


def _pharmacists():
    return (Employee.query.filter(Employee.is_active.is_(True), Employee.pharmacist_reg_no.isnot(None))
            .order_by(Employee.name).all())


def _render_counter(form=None, cart=None, status=200):
    return render_template("sales/counter.html", modes=PAYMENT_MODES, pharmacists=_pharmacists(),
                           form=form or {}, cart_json=json.dumps(cart or [])), status


@bp.route("/new", methods=["GET"])
@staff_required
def counter():
    form = {}
    pres_id = request.args.get("pres_id", "")
    if pres_id.isdigit():
        pres = db.session.get(Prescription, int(pres_id))
        if pres:
            form = {"pres_id": pres.pres_id, "c_id": pres.c_id, "customer_label": pres.customer.name}
            cart = [{"id": i.p_id, "qty": i.qty} for i in pres.items]
            today = local_today()
            cart = [dict(_product_json(db.session.get(Product, c["id"]), today), qty=c["qty"]) for c in cart]
            return _render_counter(form, cart)
    return _render_counter(form)


@bp.route("/new", methods=["POST"])
@staff_required
def checkout():
    f = request.form
    ids, qtys = f.getlist("item_id[]"), f.getlist("item_qty[]")
    today = local_today()
    cart = []
    try:
        lines = []
        for pid, qty in zip(ids, qtys):
            if not pid.isdigit():
                continue
            qty_n = int(qty) if qty.strip().lstrip("-").isdigit() else 0
            lines.append((int(pid), qty_n))
            product = db.session.get(Product, int(pid))
            if product:
                cart.append(dict(_product_json(product, today), qty=qty_n))
        try:
            discount = Decimal(f.get("discount_pct") or "0")
        except InvalidOperation:
            raise BillingError("Discount must be a number.") from None
        customer = db.session.get(Customer, int(f["c_id"])) if f.get("c_id", "").isdigit() else None
        pres = db.session.get(Prescription, int(f["pres_id"])) if f.get("pres_id", "").isdigit() else None
        if f.get("pres_id") and pres is None:
            raise BillingError("No prescription with that number.")
        pharmacist = (db.session.get(Employee, int(f["pharmacist_id"]))
                      if f.get("pharmacist_id", "").isdigit() else None)
        req = SaleRequest(
            lines=lines, billed_by=g.user, payment_mode=f.get("payment_mode", ""),
            discount_pct=discount, customer=customer, prescription=pres, pharmacist=pharmacist,
            patient_name=f.get("patient_name", "")[:100], patient_address=f.get("patient_address", "")[:500],
            prescriber_name=f.get("prescriber_name", "")[:100],
            prescriber_reg_no=f.get("prescriber_reg_no", "")[:50],
            prescriber_address=f.get("prescriber_address", "")[:500],
            buyer_gstin=f.get("buyer_gstin", "")[:15], today=today)
        sale = create_sale(req)
        db.session.commit()
    except BillingError as e:
        db.session.rollback()
        flash(str(e), "error")
        return _render_counter(f.to_dict(), cart, 422)
    except IntegrityError:
        db.session.rollback()
        flash("Another bill was saved at the same moment. Press Save again.", "error")
        return _render_counter(f.to_dict(), cart, 409)
    return redirect(url_for("sales.invoice", sb_id=sale.sb_id, print=1))


@bp.route("/<int:sb_id>")
@staff_required
def invoice(sb_id):
    return render_template("sales/invoice.html", sale=db.get_or_404(Sale, sb_id),
                           autoprint=request.args.get("print") == "1")


@bp.route("/<int:sb_id>/void", methods=["POST"])
@staff_required
def void(sb_id):
    sale = db.get_or_404(Sale, sb_id)
    if not g.user.is_admin and sale.sold_at < day_start_utc(local_today()):
        flash("Only an admin can void an invoice from an earlier day.", "error")
        return redirect(url_for("sales.invoice", sb_id=sb_id))
    try:
        void_sale(sale, request.form.get("reason", ""), g.user)
        db.session.commit()
        flash(f"Invoice {sale.invoice_no} voided and stock returned.", "success")
    except BillingError as e:
        db.session.rollback()
        flash(str(e), "error")
    return redirect(url_for("sales.invoice", sb_id=sb_id))


@bp.route("/")
@staff_required
def history():
    today = local_today()
    start = arg_date("from", today - timedelta(days=6))
    end = arg_date("to", today)
    rows = (Sale.query.filter(Sale.sold_at >= day_start_utc(start),
                              Sale.sold_at < day_start_utc(end + timedelta(days=1)))
            .order_by(Sale.sold_at.desc()).limit(1000).all())
    done = [s for s in rows if s.status == "completed"]
    summary = {
        "count": len(done),
        "total": sum((s.total for s in done), Decimal(0)),
        "by_mode": {m: sum((s.total for s in done if s.payment_mode == m), Decimal(0)) for m in PAYMENT_MODES},
    }
    return render_template("sales/history.html", sales=rows, start=start, end=end, summary=summary)
