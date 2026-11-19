"""Stock: batches, goods receipts from suppliers, adjustments, reorder list."""
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from .. import audit
from ..auth import staff_required
from ..extensions import db
from ..models import Batch, Product, Purchase, Supplier, local_today
from . import FormError, a_date, text

bp = Blueprint("inventory", __name__, url_prefix="/staff/stock")

ADJUST_REASONS = ("Expired - removed from shelf", "Damaged", "Returned to supplier",
                  "Stock count correction")


@bp.route("/")
@staff_required
def stock():
    show = request.args.get("show", "all")
    q = request.args.get("q", "").strip()
    today = local_today()
    query = Batch.query.join(Product).filter(Batch.qty_available > 0)
    if show == "expiring":
        query = query.filter(Batch.expiry_date >= today, Batch.expiry_date <= today + timedelta(days=90))
    elif show == "expired":
        query = query.filter(Batch.expiry_date < today)
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Product.brand_name.ilike(like), Product.medicine_name.ilike(like),
                                    Batch.batch_no.ilike(like)))
    batches = query.order_by(Batch.expiry_date).limit(500).all()
    return render_template("inventory/stock.html", batches=batches, show=show, q=q,
                           reasons=ADJUST_REASONS)


@bp.route("/<int:b_id>/adjust", methods=["POST"])
@staff_required
def adjust(b_id):
    batch = db.get_or_404(Batch, b_id)
    reason = request.form.get("reason", "")
    try:
        qty = int(request.form.get("qty", "0"))
    except ValueError:
        qty = 0
    if reason not in ADJUST_REASONS or qty <= 0 or qty > batch.qty_available:
        flash("Choose a reason and a quantity no larger than the stock in that batch.", "error")
    else:
        batch.qty_available -= qty
        audit.record(db.session, "adjust", "Batch", batch.b_id, {"removed": qty, "reason": reason})
        db.session.commit()
        flash(f"Removed {qty} from batch {batch.batch_no}.", "success")
    return redirect(request.referrer or url_for("inventory.stock"))


@bp.route("/purchases")
@staff_required
def purchases():
    rows = Purchase.query.order_by(Purchase.received_on.desc(), Purchase.purchase_id.desc()).limit(200).all()
    return render_template("inventory/purchases.html", purchases=rows)


@bp.route("/purchases/<int:purchase_id>")
@staff_required
def purchase(purchase_id):
    return render_template("inventory/purchase.html", purchase=db.get_or_404(Purchase, purchase_id))


def _lines_from_form(today):
    fields = ("p_id", "batch_no", "expiry", "qty", "cost", "mrp", "manufacturer")
    columns = {f: request.form.getlist(f + "[]") for f in fields}
    lines = []
    for i in range(len(columns["p_id"])):
        row = {f: (columns[f][i].strip() if i < len(columns[f]) else "") for f in fields}
        if not row["p_id"]:
            continue
        product = db.session.get(Product, int(row["p_id"])) if row["p_id"].isdigit() else None
        if product is None:
            raise FormError(f"Line {i + 1}: choose a product.")
        if not row["batch_no"]:
            raise FormError(f"Line {i + 1}: batch number is required.")
        try:
            expiry = datetime.strptime(row["expiry"], "%Y-%m-%d").date()
            qty = int(row["qty"])
            cost = Decimal(row["cost"]).quantize(Decimal("0.01"))
            mrp = Decimal(row["mrp"] or product.mrp).quantize(Decimal("0.01"))
        except (ValueError, InvalidOperation):
            raise FormError(f"Line {i + 1}: check the expiry date, quantity, cost and MRP.") from None
        if expiry <= today:
            raise FormError(f"Line {i + 1}: batch {row['batch_no']} has already expired.")
        if qty <= 0 or cost < 0 or mrp <= 0:
            raise FormError(f"Line {i + 1}: quantity and MRP must be above zero.")
        lines.append(dict(product=product, batch_no=row["batch_no"][:50], expiry=expiry, qty=qty,
                          cost=cost, mrp=mrp, manufacturer=row["manufacturer"][:100]))
    if not lines:
        raise FormError("Add at least one line.")
    return lines


@bp.route("/purchases/new", methods=["GET", "POST"])
@staff_required
def purchase_new():
    today = local_today()
    suppliers = Supplier.query.filter(Supplier.is_active.is_(True)).order_by(Supplier.firm_name).all()
    products = Product.query.filter(Product.is_active.is_(True)).order_by(Product.brand_name).all()
    if request.method == "POST":
        try:
            sup = db.session.get(Supplier, int(request.form.get("s_id") or 0))
            if sup is None or not sup.is_active:
                raise FormError("Choose a supplier.")
            if not sup.drug_licence:
                raise FormError("Record the supplier's drug licence number before buying from them.")
            if sup.licence_valid_until and sup.licence_valid_until < today:
                raise FormError("The supplier's drug licence on file has run out.")
            invoice_no = text("supplier_invoice_no", "Supplier invoice no.", max_len=40)
            purchase = Purchase(s_id=sup.s_id, supplier_invoice_no=invoice_no,
                                invoice_date=a_date("invoice_date", "Invoice date"),
                                received_on=today, e_id=g.user.e_id)
            lines = _lines_from_form(today)
            total = Decimal(0)
            for line in lines:
                purchase.batches.append(Batch(
                    p_id=line["product"].p_id, s_id=sup.s_id, batch_no=line["batch_no"],
                    expiry_date=line["expiry"], cost_price=line["cost"], mrp=line["mrp"],
                    qty_received=line["qty"], qty_available=line["qty"], received_on=today,
                    manufacturer_name=line["manufacturer"]))
                total += line["cost"] * line["qty"]
            purchase.total_cost = total
            db.session.add(purchase)
            db.session.commit()
            flash(f"Received {len(lines)} batch(es) from {sup.firm_name}.", "success")
            return redirect(url_for("inventory.purchase", purchase_id=purchase.purchase_id))
        except FormError as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template("inventory/purchase_form.html", suppliers=suppliers, products=products)


@bp.route("/reorder")
@staff_required
def reorder():
    today = local_today()
    rows = (db.session.query(Product, db.func.coalesce(db.func.sum(Batch.qty_available), 0).label("qty"))
            .outerjoin(Batch, db.and_(Batch.p_id == Product.p_id, Batch.expiry_date >= today))
            .filter(Product.is_active.is_(True)).group_by(Product.p_id).all())
    short = sorted([(p, int(qty)) for p, qty in rows if qty <= p.reorder_level], key=lambda r: r[1])
    return render_template("inventory/reorder.html", rows=short)
