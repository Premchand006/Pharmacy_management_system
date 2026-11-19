"""Database models.

Records that the drug and GST rules require to be kept (sales, purchases,
batches, prescriptions) are never deleted from the app. Sales are voided,
master data is deactivated, and every change lands in the audit log.
"""
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal

from .extensions import db

Money = db.Numeric(12, 2)


# Timestamps are stored as naive UTC. Shop days, expiry checks and the
# financial year follow Indian Standard Time, which has no DST.
IST = timezone(timedelta(hours=5, minutes=30))


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def local_today():
    return datetime.now(IST).date()


def day_start_utc(day):
    """UTC instant at which an IST calendar day starts."""
    return datetime.combine(day, time.min) - timedelta(hours=5, minutes=30)


def to_local(dt):
    return dt.replace(tzinfo=timezone.utc).astimezone(IST) if dt else dt


# Drug classes under the Drugs Rules, 1945 that the counter cares about.
SCHEDULES = {
    "OTC": "Not scheduled",
    "G": "Schedule G",
    "H": "Schedule H",
    "H1": "Schedule H1",
    "X": "Schedule X",
    "NDPS": "Narcotic / psychotropic (NDPS)",
}
PRESCRIPTION_SCHEDULES = {"H", "H1", "X", "NDPS"}
PAYMENT_MODES = ("Cash", "UPI", "Card", "Credit")


class PharmacySettings(db.Model):
    """The pharmacy's own details, printed on every invoice. One row."""

    __tablename__ = "pharmacy_settings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, default="Your Pharmacy")
    address = db.Column(db.Text, nullable=False, default="")
    phone = db.Column(db.String(30), nullable=False, default="")
    email = db.Column(db.String(120), nullable=False, default="")
    gstin = db.Column(db.String(15), nullable=False, default="")
    state_code = db.Column(db.String(2), nullable=False, default="")
    licence_20 = db.Column(db.String(60), nullable=False, default="")
    licence_21 = db.Column(db.String(60), nullable=False, default="")
    licence_20f = db.Column(db.String(60), nullable=False, default="")
    licence_fee_due = db.Column(db.Date)
    invoice_prefix = db.Column(db.String(8), nullable=False, default="INV")
    composition_scheme = db.Column(db.Boolean, nullable=False, default=False)

    @classmethod
    def get(cls):
        settings = db.session.get(cls, 1)
        if settings is None:
            settings = cls(id=1)
            db.session.add(settings)
            db.session.flush()
        return settings


class Employee(db.Model):
    __tablename__ = "employees"

    e_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(255))
    # "admin" can manage staff and settings; "staff" runs the counter.
    access = db.Column(db.String(10), nullable=False, default="staff")
    role = db.Column(db.String(50), nullable=False)
    work_shift = db.Column(db.String(20), nullable=False, default="General")
    salary = db.Column(Money, nullable=False, default=0)
    experience = db.Column(db.Integer, nullable=False, default=0)
    pharmacist_reg_no = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    session_version = db.Column(db.Integer, nullable=False, default=1)

    @property
    def is_pharmacist(self):
        return bool(self.pharmacist_reg_no)

    @property
    def is_admin(self):
        return self.access == "admin"


class Customer(db.Model):
    __tablename__ = "customers"

    c_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, default="")
    address = db.Column(db.Text, nullable=False, default="")
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    password_hash = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    session_version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    prescriptions = db.relationship("Prescription", backref="customer", lazy=True)
    sales = db.relationship("Sale", backref="customer", lazy=True)


class Supplier(db.Model):
    __tablename__ = "suppliers"

    s_id = db.Column(db.Integer, primary_key=True)
    firm_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False, default="")
    gstin = db.Column(db.String(15), nullable=False, default="")
    drug_licence = db.Column(db.String(60), nullable=False, default="")
    licence_valid_until = db.Column(db.Date)
    phone = db.Column(db.String(20), nullable=False, default="")
    address = db.Column(db.Text, nullable=False, default="")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    purchases = db.relationship("Purchase", backref="supplier", lazy=True)


class Product(db.Model):
    __tablename__ = "products"

    p_id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(100), nullable=False)
    medicine_name = db.Column(db.String(150), nullable=False)  # generic / salt
    form = db.Column(db.String(50), nullable=False)
    strength = db.Column(db.String(50), nullable=False)
    packing = db.Column(db.String(50), nullable=False)
    schedule = db.Column(db.String(5), nullable=False, default="OTC")
    hsn_code = db.Column(db.String(8), nullable=False, default="3004")
    gst_rate = db.Column(db.Numeric(5, 2), nullable=False, default=Decimal("5"))
    mrp = db.Column(Money, nullable=False)  # default MRP for new batches
    barcode = db.Column(db.String(64), unique=True)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    batches = db.relationship("Batch", backref="product", lazy=True,
                              order_by="Batch.expiry_date")

    @property
    def needs_prescription(self):
        return self.schedule in PRESCRIPTION_SCHEDULES

    @property
    def label(self):
        return f"{self.brand_name} {self.strength} ({self.form})"


class Purchase(db.Model):
    """A supplier invoice received at the store (goods receipt)."""

    __tablename__ = "purchases"

    purchase_id = db.Column(db.Integer, primary_key=True)
    s_id = db.Column(db.Integer, db.ForeignKey("suppliers.s_id"), nullable=False)
    supplier_invoice_no = db.Column(db.String(40), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    received_on = db.Column(db.Date, nullable=False, default=local_today)
    e_id = db.Column(db.Integer, db.ForeignKey("employees.e_id"))
    total_cost = db.Column(Money, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    batches = db.relationship("Batch", backref="purchase", lazy=True)
    received_by = db.relationship("Employee")


class Batch(db.Model):
    __tablename__ = "batches"

    b_id = db.Column(db.Integer, primary_key=True)
    p_id = db.Column(db.Integer, db.ForeignKey("products.p_id"), nullable=False, index=True)
    s_id = db.Column(db.Integer, db.ForeignKey("suppliers.s_id"), nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.purchase_id"))
    batch_no = db.Column(db.String(50), nullable=False)
    manufacture_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    cost_price = db.Column(Money, nullable=False)
    mrp = db.Column(Money, nullable=False)
    qty_received = db.Column(db.Integer, nullable=False)
    qty_available = db.Column(db.Integer, nullable=False)
    received_on = db.Column(db.Date, nullable=False, default=local_today)
    manufacturer_name = db.Column(db.String(100), nullable=False, default="")
    marketer_name = db.Column(db.String(100), nullable=False, default="")

    supplier = db.relationship("Supplier")
    sale_items = db.relationship("SaleItem", backref="batch", lazy=True)

    @property
    def is_expired(self):
        return self.expiry_date < local_today()


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    pres_id = db.Column(db.Integer, primary_key=True)
    c_id = db.Column(db.Integer, db.ForeignKey("customers.c_id"), nullable=False, index=True)
    doctor_name = db.Column(db.String(100), nullable=False)
    doctor_reg_no = db.Column(db.String(50), nullable=False)
    doctor_address = db.Column(db.Text, nullable=False, default="")
    hospital_name = db.Column(db.String(120), nullable=False, default="")
    date = db.Column(db.Date, nullable=False)
    repeats_allowed = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    items = db.relationship("PrescriptionItem", backref="prescription", lazy=True,
                            order_by="PrescriptionItem.line_no")
    sales = db.relationship("Sale", backref="prescription", lazy=True)

    @property
    def times_dispensed(self):
        return sum(1 for s in self.sales if s.status == "completed")


class PrescriptionItem(db.Model):
    __tablename__ = "prescription_items"

    id = db.Column(db.Integer, primary_key=True)
    pres_id = db.Column(db.Integer, db.ForeignKey("prescriptions.pres_id"), nullable=False)
    line_no = db.Column(db.Integer, nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey("products.p_id"), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    instructions = db.Column(db.Text, nullable=False, default="")

    product = db.relationship("Product")


class Sale(db.Model):
    """A tax invoice. Never deleted; cancelled invoices are voided."""

    __tablename__ = "sales"
    __table_args__ = (db.UniqueConstraint("financial_year", "seq", name="uq_invoice_seq"),)

    sb_id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(32), unique=True, nullable=False)
    financial_year = db.Column(db.String(7), nullable=False)  # e.g. 2026-27
    seq = db.Column(db.Integer, nullable=False)
    sold_at = db.Column(db.DateTime, nullable=False, default=utcnow, index=True)
    e_id = db.Column(db.Integer, db.ForeignKey("employees.e_id"), nullable=False)
    pharmacist_id = db.Column(db.Integer, db.ForeignKey("employees.e_id"))
    c_id = db.Column(db.Integer, db.ForeignKey("customers.c_id"))
    pres_id = db.Column(db.Integer, db.ForeignKey("prescriptions.pres_id"))
    # Copied at sale time so registers stay correct if a profile changes.
    patient_name = db.Column(db.String(100), nullable=False, default="")
    patient_address = db.Column(db.Text, nullable=False, default="")
    prescriber_name = db.Column(db.String(100), nullable=False, default="")
    prescriber_reg_no = db.Column(db.String(50), nullable=False, default="")
    prescriber_address = db.Column(db.Text, nullable=False, default="")
    buyer_gstin = db.Column(db.String(15), nullable=False, default="")
    payment_mode = db.Column(db.String(10), nullable=False, default="Cash")
    gross_total = db.Column(Money, nullable=False, default=0)
    discount_total = db.Column(Money, nullable=False, default=0)
    taxable_total = db.Column(Money, nullable=False, default=0)
    cgst_total = db.Column(Money, nullable=False, default=0)
    sgst_total = db.Column(Money, nullable=False, default=0)
    round_off = db.Column(Money, nullable=False, default=0)
    total = db.Column(Money, nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default="completed")
    void_reason = db.Column(db.Text)
    voided_at = db.Column(db.DateTime)
    voided_by_id = db.Column(db.Integer, db.ForeignKey("employees.e_id"))

    items = db.relationship("SaleItem", backref="sale", lazy=True, order_by="SaleItem.line_no")
    billed_by = db.relationship("Employee", foreign_keys=[e_id])
    pharmacist = db.relationship("Employee", foreign_keys=[pharmacist_id])
    voided_by = db.relationship("Employee", foreign_keys=[voided_by_id])

    @property
    def tax_total(self):
        return (self.cgst_total or 0) + (self.sgst_total or 0)


class SaleItem(db.Model):
    __tablename__ = "sale_items"

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.sb_id"), nullable=False, index=True)
    line_no = db.Column(db.Integer, nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey("products.p_id"), nullable=False, index=True)
    b_id = db.Column(db.Integer, db.ForeignKey("batches.b_id"), nullable=False, index=True)
    item_name = db.Column(db.String(200), nullable=False)
    schedule = db.Column(db.String(5), nullable=False)
    hsn_code = db.Column(db.String(8), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    mrp = db.Column(Money, nullable=False)
    discount = db.Column(Money, nullable=False, default=0)
    gst_rate = db.Column(db.Numeric(5, 2), nullable=False)
    taxable_value = db.Column(Money, nullable=False)
    cgst = db.Column(Money, nullable=False)
    sgst = db.Column(Money, nullable=False)
    line_total = db.Column(Money, nullable=False)

    product = db.relationship("Product")


class AuditLog(db.Model):
    """Append-only record of who changed what. The app never edits it."""

    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    at = db.Column(db.DateTime, nullable=False, default=utcnow, index=True)
    actor = db.Column(db.String(120), nullable=False, default="system")
    action = db.Column(db.String(20), nullable=False)
    entity = db.Column(db.String(40), nullable=False)
    entity_id = db.Column(db.String(40), nullable=False, default="")
    changes = db.Column(db.Text, nullable=False, default="")
    ip = db.Column(db.String(64), nullable=False, default="")


class LoginAttempt(db.Model):
    __tablename__ = "login_attempts"

    id = db.Column(db.Integer, primary_key=True)
    at = db.Column(db.DateTime, nullable=False, default=utcnow, index=True)
    portal = db.Column(db.String(10), nullable=False)
    identifier = db.Column(db.String(100), nullable=False, index=True)
    ip = db.Column(db.String(64), nullable=False, default="")
    success = db.Column(db.Boolean, nullable=False, default=False)
