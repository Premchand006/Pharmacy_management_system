from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    
    c_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    address = Column(String)
    age = Column(Integer)
    gender = Column(String)
    prescriptions = relationship("Prescription", back_populates="customer")
    sales = relationship("Sale", back_populates="customer")

class Employee(Base):
    __tablename__ = "employees"
    
    e_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    salary = Column(Float)
    work_shift = Column(String)
    role = Column(String)
    experience = Column(Integer)
    sales = relationship("Sale", back_populates="employee")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    s_id = Column(Integer, primary_key=True, index=True)
    firm_name = Column(String)
    owner_name = Column(String)
    gst_no = Column(String)
    phone = Column(String)
    address = Column(String)
    drug_license = Column(String)
    ifsc = Column(String)
    bank_acc_no = Column(String)
    batches = relationship("Batch", back_populates="supplier")
    purchases = relationship("Purchase", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"
    
    p_id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String)
    medicine_name = Column(String)
    form = Column(String)
    strength = Column(String)
    packing = Column(String)
    prescription_type = Column(String)
    mrp = Column(Float)
    unit_price = Column(Float)
    batches = relationship("Batch", back_populates="product")

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    pres_id = Column(Integer, primary_key=True, index=True)
    c_id = Column(Integer, ForeignKey("customers.c_id"))
    dr_id = Column(String)
    doctor_license_no = Column(String)
    date = Column(Date)
    validity = Column(Integer)
    hospital_name = Column(String)
    customer = relationship("Customer", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription")
    sales = relationship("Sale", back_populates="prescription")

class PrescriptionItem(Base):
    __tablename__ = "prescription_items"
    
    pres_id = Column(Integer, ForeignKey("prescriptions.pres_id"), primary_key=True)
    line_no = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.p_id"))
    dosage = Column(String)
    duration = Column(String)
    qty = Column(Integer)
    instructions = Column(String)
    prescription = relationship("Prescription", back_populates="items")

class Batch(Base):
    __tablename__ = "batches"
    
    b_id = Column(Integer, primary_key=True, index=True)
    p_id = Column(Integer, ForeignKey("products.p_id"))
    s_id = Column(Integer, ForeignKey("suppliers.s_id"))
    batch_no = Column(String)
    manufacture_date = Column(Date)
    expiry_date = Column(Date)
    cost_price = Column(Float)
    qty_received = Column(Integer)
    qty_available = Column(Integer)
    received_on = Column(Date)
    manufacture_name = Column(String)
    marketer_name = Column(String)
    product = relationship("Product", back_populates="batches")
    supplier = relationship("Supplier", back_populates="batches")
    purchases = relationship("Purchase", back_populates="batch")
    sale_items = relationship("SaleItem", back_populates="batch")

class Purchase(Base):
    __tablename__ = "purchases"
    
    purchase_id = Column(Integer, primary_key=True, index=True)
    b_id = Column(Integer, ForeignKey("batches.b_id"))
    s_id = Column(Integer, ForeignKey("suppliers.s_id"))
    p_id = Column(Integer, ForeignKey("products.p_id"))
    date = Column(Date)
    cost = Column(Float)
    status = Column(String)
    batch = relationship("Batch", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")

class Sale(Base):
    __tablename__ = "sales"
    
    sb_id = Column(Integer, primary_key=True, index=True)
    c_id = Column(Integer, ForeignKey("customers.c_id"))
    e_id = Column(Integer, ForeignKey("employees.e_id"))
    pres_id = Column(Integer, ForeignKey("prescriptions.pres_id"))
    sale_date = Column(Date)
    payment_mode = Column(String)
    amount = Column(Float)
    tax = Column(Float)
    discount = Column(Float)
    total = Column(Float)
    status = Column(String)
    customer = relationship("Customer", back_populates="sales")
    employee = relationship("Employee", back_populates="sales")
    prescription = relationship("Prescription", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sale_items"
    
    sale_id = Column(Integer, ForeignKey("sales.sb_id"), primary_key=True)
    line_no = Column(Integer, primary_key=True)
    p_id = Column(Integer, ForeignKey("products.p_id"))
    b_id = Column(Integer, ForeignKey("batches.b_id"))
    qty = Column(Integer)
    price = Column(Float)
    line_total = Column(Float)
    line_discount = Column(Float)
    sale = relationship("Sale", back_populates="items")
    batch = relationship("Batch", back_populates="sale_items")