from datetime import date, datetime
from extensions import db

class Customer(db.Model):
    __tablename__ = 'customers'

    c_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    password_hash = db.Column(db.String(128))  # For secure login

    # Relationships
    prescriptions = db.relationship(
        'Prescription', backref='customer', lazy=True)
    sales = db.relationship('Sale', backref='customer', lazy=True)

class Employee(db.Model):
    __tablename__ = 'employees'

    e_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)  # For admin/staff login
    password_hash = db.Column(db.String(128))  # For secure login
    name = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    work_shift = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)

    # Relationships
    sales = db.relationship('Sale', backref='employee', lazy=True)

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    s_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firm_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    gst_no = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    drug_license = db.Column(db.String(50), unique=True, nullable=False)
    ifsc = db.Column(db.String(20), nullable=False)
    bank_acc_no = db.Column(db.String(30), nullable=False)

    # Relationships
    batches = db.relationship('Batch', backref='supplier', lazy=True)
    purchases = db.relationship('Purchase', backref='supplier', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'

    p_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brand_name = db.Column(db.String(100), nullable=False)
    medicine_name = db.Column(db.String(100), nullable=False)
    # tablet, syrup, injection, etc.
    form = db.Column(db.String(50), nullable=False)
    # 500mg, 10ml, etc.
    strength = db.Column(db.String(50), nullable=False)
    # strip of 10, bottle of 100ml
    packing = db.Column(db.String(50), nullable=False)
    prescription_type = db.Column(
        db.String(20), nullable=False)  # OTC, Prescription
    mrp = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    # Relationships
    batches = db.relationship('Batch', backref='product', lazy=True)
    purchases = db.relationship('Purchase', backref='product', lazy=True)
    sale_items = db.relationship('SaleItem', backref='product', lazy=True)
    prescription_items = db.relationship(
        'PrescriptionItem', backref='product', lazy=True)

class Batch(db.Model):
    __tablename__ = 'batches'

    b_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_id = db.Column(db.Integer, db.ForeignKey(
        'products.p_id'), nullable=False)
    s_id = db.Column(db.Integer, db.ForeignKey(
        'suppliers.s_id'), nullable=False)
    batch_no = db.Column(db.String(50), nullable=False)
    manufacture_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    qty_received = db.Column(db.Integer, nullable=False)
    qty_available = db.Column(db.Integer, nullable=False)
    received_on = db.Column(db.Date, nullable=False)
    manufacture_name = db.Column(db.String(100), nullable=False)
    marketer_name = db.Column(db.String(100), nullable=False)

    # Relationships
    purchases = db.relationship('Purchase', backref='batch', lazy=True)
    sale_items = db.relationship('SaleItem', backref='batch', lazy=True)

class Purchase(db.Model):
    __tablename__ = 'purchases'

    purchase_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    b_id = db.Column(db.Integer, db.ForeignKey(
        'batches.b_id'), nullable=False)
    s_id = db.Column(db.Integer, db.ForeignKey(
        'suppliers.s_id'), nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey(
        'products.p_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')

class Sale(db.Model):
    __tablename__ = 'sales'

    sb_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_id = db.Column(db.Integer, db.ForeignKey(
        'customers.c_id'), nullable=False)
    e_id = db.Column(db.Integer, db.ForeignKey(
        'employees.e_id'), nullable=False)
    pres_id = db.Column(db.Integer, db.ForeignKey(
        'prescriptions.pres_id'), nullable=True)
    sale_date = db.Column(db.Date, nullable=False)
    payment_mode = db.Column(
        db.String(20), nullable=False)  # Cash, Card, UPI
    amount = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False, default=0.0)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Completed')

    # Relationships
    sale_items = db.relationship(
        'SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')

class SaleItem(db.Model):
    __tablename__ = 'sale_items'

    sale_id = db.Column(db.Integer, db.ForeignKey(
        'sales.sb_id'), primary_key=True)
    line_no = db.Column(db.Integer, primary_key=True)
    p_id = db.Column(db.Integer, db.ForeignKey(
        'products.p_id'), nullable=False)
    b_id = db.Column(db.Integer, db.ForeignKey(
        'batches.b_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    line_total = db.Column(db.Float, nullable=False)
    line_discount = db.Column(db.Float, nullable=False, default=0.0)

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    pres_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_id = db.Column(db.Integer, db.ForeignKey(
        'customers.c_id'), nullable=False)
    dr_id = db.Column(db.String(50), nullable=False)
    doctor_license_no = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    validity = db.Column(db.Date, nullable=False)
    hospital_name = db.Column(db.String(100), nullable=False)

    # Relationships
    prescription_items = db.relationship(
        'PrescriptionItem', backref='prescription', lazy=True, cascade='all, delete-orphan')
    sales = db.relationship('Sale', backref='prescription', lazy=True)

class PrescriptionItem(db.Model):
    __tablename__ = 'prescription_items'

    pres_id = db.Column(db.Integer, db.ForeignKey(
        'prescriptions.pres_id'), primary_key=True)
    line_no = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.p_id'), nullable=False)
    # 1 tablet, 2 times, etc.
    dosage = db.Column(db.String(50), nullable=False)
    # 7 days, 1 week, etc.
    duration = db.Column(db.String(50), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    # Take after meals, etc.
    instructions = db.Column(db.Text, nullable=True)

