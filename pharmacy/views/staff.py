"""Back-office pages: dashboard and master data."""
from datetime import timedelta

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .. import audit
from ..auth import admin_required, hash_password, password_problem, staff_required
from ..extensions import db
from ..models import (SCHEDULES, Batch, Customer, Employee, PharmacySettings, Prescription,
                      Product, Sale, Supplier, day_start_utc, local_today)
from . import FormError, a_date, integer, money, text

bp = Blueprint("staff", __name__, url_prefix="/staff")


@bp.route("/")
@staff_required
def dashboard():
    today = local_today()
    soon = today + timedelta(days=30)
    start_of_day = day_start_utc(today)
    todays = Sale.query.filter(Sale.status == "completed", Sale.sold_at >= start_of_day)
    stock = (db.session.query(Product, db.func.coalesce(db.func.sum(Batch.qty_available), 0))
             .outerjoin(Batch, db.and_(Batch.p_id == Product.p_id, Batch.expiry_date >= today))
             .filter(Product.is_active.is_(True)).group_by(Product.p_id).all())
    settings = PharmacySettings.get()
    stats = {
        "sales_today": todays.count(),
        "revenue_today": db.session.query(db.func.coalesce(db.func.sum(Sale.total), 0))
        .filter(Sale.status == "completed", Sale.sold_at >= start_of_day).scalar(),
        "near_expiry": Batch.query.filter(Batch.qty_available > 0, Batch.expiry_date >= today,
                                          Batch.expiry_date <= soon).count(),
        "expired": Batch.query.filter(Batch.qty_available > 0, Batch.expiry_date < today).count(),
        "reorder": sum(1 for product, qty in stock if qty <= product.reorder_level),
        "products": len(stock),
    }
    warnings = []
    if not settings.gstin or not settings.licence_20:
        warnings.append("Add the pharmacy's GSTIN and drug licence numbers in Settings. "
                        "They are printed on every invoice.")
    if settings.licence_fee_due and settings.licence_fee_due <= today + timedelta(days=60):
        warnings.append(f"Drug licence retention fee is due on {settings.licence_fee_due:%d %b %Y}.")
    expiring_suppliers = Supplier.query.filter(Supplier.is_active.is_(True),
                                               Supplier.licence_valid_until.isnot(None),
                                               Supplier.licence_valid_until <= today + timedelta(days=30)).all()
    for s in expiring_suppliers:
        warnings.append(f"{s.firm_name}'s drug licence on file runs out on {s.licence_valid_until:%d %b %Y}.")
    recent = Sale.query.order_by(Sale.sold_at.desc()).limit(8).all()
    return render_template("staff/dashboard.html", stats=stats, warnings=warnings, recent=recent)


# ---------------------------------------------------------------- employees

@bp.route("/employees")
@admin_required
def employees():
    rows = Employee.query.order_by(Employee.is_active.desc(), Employee.name).all()
    return render_template("staff/employees.html", employees=rows)


def _employee_from_form(emp):
    emp.name = text("name", "Name", max_len=100)
    emp.role = text("role", "Job title", max_len=50)
    emp.work_shift = text("work_shift", "Shift", max_len=20)
    emp.salary = money("salary", "Salary")
    emp.experience = integer("experience", "Experience", minimum=0, maximum=60)
    emp.phone = text("phone", required=False, max_len=20)
    emp.pharmacist_reg_no = text("pharmacist_reg_no", required=False, max_len=50) or None
    access = request.form.get("access", "staff")
    if access not in ("staff", "admin"):
        raise FormError("Choose an access level.")
    if emp.e_id == g.user.e_id and access != "admin":
        raise FormError("You cannot remove your own admin access.")
    emp.access = access
    username = text("username", required=False, max_len=50).lower() or None
    if username:
        clash = Employee.query.filter(db.func.lower(Employee.username) == username,
                                      Employee.e_id != (emp.e_id or 0)).first()
        if clash:
            raise FormError("That username is already taken.")
    emp.username = username
    password = request.form.get("password", "")
    if password:
        if (problem := password_problem(password)):
            raise FormError(problem)
        emp.password_hash = hash_password(password)
        emp.session_version = (emp.session_version or 0) + 1
    if emp.username and not emp.password_hash:
        raise FormError("Set a password for this login.")


@bp.route("/employees/new", methods=["GET", "POST"])
@bp.route("/employees/<int:e_id>", methods=["GET", "POST"])
@admin_required
def employee_form(e_id=None):
    emp = db.session.get(Employee, e_id) if e_id else Employee(session_version=1)
    if emp is None:
        abort(404)
    if request.method == "POST":
        try:
            _employee_from_form(emp)
            db.session.add(emp)
            db.session.commit()
            flash(f"Saved {emp.name}.", "success")
            return redirect(url_for("staff.employees"))
        except FormError as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template("staff/employee_form.html", emp=emp)


@bp.route("/employees/<int:e_id>/toggle", methods=["POST"])
@admin_required
def employee_toggle(e_id):
    emp = db.get_or_404(Employee, e_id)
    if emp.e_id == g.user.e_id:
        flash("You cannot deactivate your own account.", "error")
    else:
        emp.is_active = not emp.is_active
        emp.session_version += 1  # signs them out
        db.session.commit()
        flash(f"{emp.name} is now {'active' if emp.is_active else 'inactive'}.", "success")
    return redirect(url_for("staff.employees"))


# ---------------------------------------------------------------- products

@bp.route("/products")
@staff_required
def products():
    q = request.args.get("q", "").strip()
    query = Product.query
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Product.brand_name.ilike(like), Product.medicine_name.ilike(like),
                                    Product.barcode == q))
    rows = query.order_by(Product.is_active.desc(), Product.brand_name).all()
    today = local_today()
    stock = dict(db.session.query(Batch.p_id, db.func.sum(Batch.qty_available))
                 .filter(Batch.expiry_date >= today).group_by(Batch.p_id).all())
    return render_template("staff/products.html", products=rows, stock=stock, q=q)


def _product_from_form(p):
    p.brand_name = text("brand_name", "Brand name", max_len=100)
    p.medicine_name = text("medicine_name", "Generic name", max_len=150)
    p.form = text("form", "Form", max_len=50)
    p.strength = text("strength", "Strength", max_len=50)
    p.packing = text("packing", "Packing", max_len=50)
    schedule = request.form.get("schedule", "")
    if schedule not in SCHEDULES:
        raise FormError("Choose a drug schedule.")
    p.schedule = schedule
    hsn = text("hsn_code", "HSN code", max_len=8)
    if not hsn.isdigit() or len(hsn) not in (4, 6, 8):
        raise FormError("HSN code must be 4, 6 or 8 digits.")
    p.hsn_code = hsn
    rate = money("gst_rate", "GST rate")
    if rate not in (0, 5, 12, 18, 28):
        raise FormError("GST rate must be 0, 5, 12, 18 or 28 percent.")
    p.gst_rate = rate
    p.mrp = money("mrp", "MRP")
    p.reorder_level = integer("reorder_level", "Reorder level", minimum=0)
    barcode = text("barcode", required=False, max_len=64) or None
    if barcode and Product.query.filter(Product.barcode == barcode, Product.p_id != (p.p_id or 0)).first():
        raise FormError("Another product already has that barcode.")
    p.barcode = barcode


@bp.route("/products/new", methods=["GET", "POST"])
@bp.route("/products/<int:p_id>", methods=["GET", "POST"])
@staff_required
def product_form(p_id=None):
    product = db.session.get(Product, p_id) if p_id else Product(schedule="OTC", hsn_code="3004",
                                                                 gst_rate=5, reorder_level=10)
    if product is None:
        abort(404)
    if request.method == "POST":
        try:
            _product_from_form(product)
            db.session.add(product)
            db.session.commit()
            flash(f"Saved {product.brand_name}.", "success")
            return redirect(url_for("staff.products"))
        except FormError as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template("staff/product_form.html", product=product)


@bp.route("/products/<int:p_id>/toggle", methods=["POST"])
@admin_required
def product_toggle(p_id):
    product = db.get_or_404(Product, p_id)
    product.is_active = not product.is_active
    db.session.commit()
    flash(f"{product.brand_name} is now {'on sale' if product.is_active else 'discontinued'}.", "success")
    return redirect(url_for("staff.products"))


# ---------------------------------------------------------------- customers

@bp.route("/customers")
@staff_required
def customers():
    q = request.args.get("q", "").strip()
    query = Customer.query.filter(Customer.is_active.is_(True))
    if q:
        filters = [Customer.name.ilike(f"%{q}%"), Customer.phone.ilike(f"%{q}%")]
        if q.isdigit():
            filters.append(Customer.c_id == int(q))
        query = query.filter(db.or_(*filters))
    rows = query.order_by(Customer.name).limit(200).all()
    return render_template("staff/customers.html", customers=rows, q=q)


@bp.route("/customers/new", methods=["GET", "POST"])
@bp.route("/customers/<int:c_id>", methods=["GET", "POST"])
@staff_required
def customer_form(c_id=None):
    cust = db.session.get(Customer, c_id) if c_id else Customer()
    if cust is None or (c_id and not cust.is_active):
        abort(404)
    if request.method == "POST":
        try:
            cust.name = text("name", "Name", max_len=100)
            cust.phone = text("phone", "Phone", max_len=20)
            cust.address = text("address", "Address", required=False, max_len=500)
            cust.age = integer("age", "Age", required=False, minimum=0, maximum=130)
            gender = request.form.get("gender", "")
            cust.gender = gender if gender in ("Female", "Male", "Other") else None
            password = request.form.get("password", "")
            if password:
                if (problem := password_problem(password)):
                    raise FormError(problem)
                cust.password_hash = hash_password(password)
                cust.session_version = (cust.session_version or 0) + 1
            db.session.add(cust)
            db.session.commit()
            flash(f"Saved customer #{cust.c_id}.", "success")
            return redirect(url_for("staff.customers"))
        except FormError as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template("staff/customer_form.html", cust=cust)


@bp.route("/customers/<int:c_id>/anonymise", methods=["POST"])
@admin_required
def customer_anonymise(c_id):
    """Erase a customer's profile on request (DPDP Act).

    Invoices and drug registers keep the patient details copied at sale
    time, because the Drugs Rules and GST law require those records.
    """
    cust = db.get_or_404(Customer, c_id)
    cust.name = f"Erased customer #{cust.c_id}"
    cust.phone = cust.address = ""
    cust.age = cust.gender = cust.password_hash = None
    cust.is_active = False
    cust.session_version += 1
    audit.record(db.session, "erase", "Customer", cust.c_id)
    db.session.commit()
    flash("Customer profile erased. Legally required sale records were kept.", "success")
    return redirect(url_for("staff.customers"))


# ---------------------------------------------------------------- suppliers

@bp.route("/suppliers")
@staff_required
def suppliers():
    rows = Supplier.query.order_by(Supplier.is_active.desc(), Supplier.firm_name).all()
    return render_template("staff/suppliers.html", suppliers=rows)


@bp.route("/suppliers/new", methods=["GET", "POST"])
@bp.route("/suppliers/<int:s_id>", methods=["GET", "POST"])
@staff_required
def supplier_form(s_id=None):
    sup = db.session.get(Supplier, s_id) if s_id else Supplier()
    if sup is None:
        abort(404)
    if request.method == "POST":
        try:
            sup.firm_name = text("firm_name", "Firm name", max_len=100)
            sup.owner_name = text("owner_name", "Contact person", required=False, max_len=100)
            sup.gstin = text("gstin", "GSTIN", required=False, max_len=15).upper()
            sup.drug_licence = text("drug_licence", "Drug licence no.", max_len=60)
            sup.licence_valid_until = a_date("licence_valid_until", "Licence valid until", required=False)
            sup.phone = text("phone", "Phone", required=False, max_len=20)
            sup.address = text("address", "Address", required=False, max_len=500)
            if sup.gstin and len(sup.gstin) != 15:
                raise FormError("GSTIN must be 15 characters.")
            db.session.add(sup)
            db.session.commit()
            flash(f"Saved {sup.firm_name}.", "success")
            return redirect(url_for("staff.suppliers"))
        except FormError as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template("staff/supplier_form.html", sup=sup)


@bp.route("/suppliers/<int:s_id>/toggle", methods=["POST"])
@admin_required
def supplier_toggle(s_id):
    sup = db.get_or_404(Supplier, s_id)
    sup.is_active = not sup.is_active
    db.session.commit()
    return redirect(url_for("staff.suppliers"))


# ---------------------------------------------------------------- settings

@bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    s = PharmacySettings.get()
    if request.method == "POST":
        try:
            s.name = text("name", "Pharmacy name", max_len=120)
            s.address = text("address", "Address", max_len=500)
            s.phone = text("phone", "Phone", required=False, max_len=30)
            s.email = text("email", "Email", required=False, max_len=120)
            s.gstin = text("gstin", "GSTIN", required=False, max_len=15).upper()
            if s.gstin and len(s.gstin) != 15:
                raise FormError("GSTIN must be 15 characters.")
            s.state_code = s.gstin[:2] if s.gstin else text("state_code", required=False, max_len=2)
            s.licence_20 = text("licence_20", "Form 20 licence", required=False, max_len=60)
            s.licence_21 = text("licence_21", "Form 21 licence", required=False, max_len=60)
            s.licence_20f = text("licence_20f", "Form 20F licence", required=False, max_len=60)
            s.licence_fee_due = a_date("licence_fee_due", "Retention fee due", required=False)
            prefix = text("invoice_prefix", "Invoice prefix", max_len=8).upper()
            if not prefix.isalnum():
                raise FormError("Invoice prefix can only use letters and digits.")
            s.invoice_prefix = prefix
            s.composition_scheme = request.form.get("composition_scheme") == "on"
            db.session.commit()
            flash("Settings saved.", "success")
            return redirect(url_for("staff.settings"))
        except FormError as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template("staff/settings.html", s=s)


# ---------------------------------------------------------------- prescriptions

@bp.route("/prescriptions")
@staff_required
def prescriptions():
    rows = Prescription.query.order_by(Prescription.created_at.desc()).limit(200).all()
    return render_template("staff/prescriptions.html", prescriptions=rows)


@bp.route("/prescriptions/<int:pres_id>")
@staff_required
def prescription(pres_id):
    pres = db.get_or_404(Prescription, pres_id)
    return render_template("shared/prescription.html", pres=pres, staff_view=True)
