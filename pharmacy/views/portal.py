"""Customer portal. Every query is scoped to the signed-in customer."""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from ..auth import customer_required
from ..extensions import db
from ..models import Prescription, PrescriptionItem, Product, Sale, local_today
from . import FormError, a_date, text

bp = Blueprint("portal", __name__, url_prefix="/portal")


@bp.route("/")
@customer_required
def home():
    prescriptions = (Prescription.query.filter_by(c_id=g.user.c_id)
                     .order_by(Prescription.date.desc()).all())
    purchases = (Sale.query.filter_by(c_id=g.user.c_id, status="completed")
                 .order_by(Sale.sold_at.desc()).limit(20).all())
    return render_template("portal/home.html", prescriptions=prescriptions, purchases=purchases)


@bp.route("/prescriptions/<int:pres_id>")
@customer_required
def prescription(pres_id):
    pres = Prescription.query.filter_by(pres_id=pres_id, c_id=g.user.c_id).first_or_404()
    return render_template("shared/prescription.html", pres=pres, staff_view=False)


@bp.route("/purchases/<int:sb_id>")
@customer_required
def purchase(sb_id):
    sale = Sale.query.filter_by(sb_id=sb_id, c_id=g.user.c_id).first_or_404()
    return render_template("sales/invoice.html", sale=sale, autoprint=False, customer_view=True)


@bp.route("/prescriptions/new", methods=["GET", "POST"])
@customer_required
def prescription_new():
    products = Product.query.filter(Product.is_active.is_(True)).order_by(Product.brand_name).all()
    if request.method == "POST":
        try:
            pres = Prescription(
                c_id=g.user.c_id,
                doctor_name=text("doctor_name", "Doctor's name", max_len=100),
                doctor_reg_no=text("doctor_reg_no", "Doctor's registration no.", max_len=50),
                doctor_address=text("doctor_address", "Doctor's address", max_len=500),
                hospital_name=text("hospital_name", "Hospital or clinic", required=False, max_len=120),
                date=a_date("date", "Prescription date"),
                notes=text("notes", required=False, max_len=1000),
            )
            if pres.date > local_today():
                raise FormError("The prescription date cannot be in the future.")
            ids = request.form.getlist("p_id[]")
            fields = {k: request.form.getlist(k + "[]") for k in ("dosage", "duration", "qty", "instructions")}
            line = 0
            for i, pid in enumerate(ids):
                if not pid.isdigit():
                    continue
                product = db.session.get(Product, int(pid))
                qty = fields["qty"][i] if i < len(fields["qty"]) else ""
                if product is None or not qty.isdigit() or int(qty) < 1:
                    raise FormError(f"Medicine {i + 1}: choose a medicine and a quantity.")
                line += 1
                pres.items.append(PrescriptionItem(
                    line_no=line, p_id=product.p_id, qty=int(qty),
                    dosage=(fields["dosage"][i] if i < len(fields["dosage"]) else "")[:50] or "As directed",
                    duration=(fields["duration"][i] if i < len(fields["duration"]) else "")[:50] or "-",
                    instructions=(fields["instructions"][i] if i < len(fields["instructions"]) else "")[:500]))
            if not pres.items:
                raise FormError("Add at least one medicine.")
            db.session.add(pres)
            db.session.commit()
            flash("Prescription sent. Bring the original to the counter when you collect the medicines.",
                  "success")
            return redirect(url_for("portal.prescription", pres_id=pres.pres_id))
        except FormError as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template("portal/prescription_form.html", products=products)
