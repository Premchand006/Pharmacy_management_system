from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import func


# Customers
def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_c = models.Customer(
        name=customer.name,
        phone=customer.phone,
        address=customer.address,
        age=customer.age,
        gender=customer.gender,
    )
    db.add(db_c)
    db.commit()
    db.refresh(db_c)
    return db_c


def get_customer(db: Session, c_id: int):
    return db.query(models.Customer).filter(models.Customer.c_id == c_id).first()


def list_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()


def update_customer(db: Session, c_id: int, data: dict):
    db_c = get_customer(db, c_id)
    if not db_c:
        return None
    for k, v in data.items():
        setattr(db_c, k, v)
    db.commit()
    db.refresh(db_c)
    return db_c


def delete_customer(db: Session, c_id: int):
    db_c = get_customer(db, c_id)
    if not db_c:
        return False
    db.delete(db_c)
    db.commit()
    return True


# Products
def create_product(db: Session, prod: schemas.ProductCreate):
    db_p = models.Product(
        brand_name=prod.brand_name,
        medicine_name=prod.medicine_name,
        form=prod.form,
        strength=prod.strength,
        packing=prod.packing,
        prescription_type=prod.prescription_type,
        mrp=prod.mrp,
        unit_price=prod.unit_price,
    )
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p


def get_product(db: Session, p_id: int):
    return db.query(models.Product).filter(models.Product.p_id == p_id).first()


def list_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()


def update_product(db: Session, p_id: int, data: dict):
    db_p = get_product(db, p_id)
    if not db_p:
        return None
    for k, v in data.items():
        setattr(db_p, k, v)
    db.commit()
    db.refresh(db_p)
    return db_p


def delete_product(db: Session, p_id: int):
    db_p = get_product(db, p_id)
    if not db_p:
        return False
    db.delete(db_p)
    db.commit()
    return True


# Batches
def create_batch(db: Session, batch: schemas.BatchCreate):
    db_b = models.Batch(
        p_id=batch.p_id,
        s_id=batch.s_id,
        batch_no=batch.batch_no,
        manufacture_date=batch.manufacture_date,
        expiry_date=batch.expiry_date,
        cost_price=batch.cost_price,
        qty_received=batch.qty_received,
        qty_available=batch.qty_available,
        received_on=batch.received_on,
        manufacture_name=batch.manufacture_name,
        marketer_name=batch.marketer_name,
    )
    db.add(db_b)
    db.commit()
    db.refresh(db_b)
    return db_b


def get_batch(db: Session, b_id: int):
    return db.query(models.Batch).filter(models.Batch.b_id == b_id).first()


def list_batches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Batch).offset(skip).limit(limit).all()


# Purchases
def create_purchase(db: Session, purchase: dict):
    db_p = models.Purchase(
        b_id=purchase.get("b_id"),
        s_id=purchase.get("s_id"),
        p_id=purchase.get("p_id"),
        date=purchase.get("date"),
        cost=purchase.get("cost"),
        status=purchase.get("status"),
    )
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p


def list_purchases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Purchase).offset(skip).limit(limit).all()


# Prescriptions and items
def create_prescription(db: Session, pres: schemas.PrescriptionCreate):
    db_pres = models.Prescription(
        c_id=pres.c_id,
        dr_id=pres.dr_id,
        doctor_license_no=pres.doctor_license_no,
        date=pres.date,
        validity=pres.validity,
        hospital_name=pres.hospital_name,
    )
    db.add(db_pres)
    db.commit()
    db.refresh(db_pres)
    return db_pres


def create_prescription_item(db: Session, item: schemas.PrescriptionItemCreate):
    db_item = models.PrescriptionItem(
        pres_id=item.pres_id,
        line_no=item.line_no,
        product_id=item.product_id,
        dosage=item.dosage,
        duration=item.duration,
        qty=item.qty,
        instructions=item.instructions,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def list_prescriptions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Prescription).offset(skip).limit(limit).all()


# Sales and sale items
def create_sale(db: Session, sale: schemas.SaleCreate):
    db_sale = models.Sale(
        c_id=sale.c_id,
        e_id=sale.e_id,
        pres_id=sale.pres_id,
        sale_date=sale.sale_date,
        payment_mode=sale.payment_mode,
        amount=sale.amount,
        tax=sale.tax,
        discount=sale.discount,
        total=sale.total,
        status=sale.status,
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


def create_sale_item(db: Session, item: schemas.SaleItemCreate):
    db_item = models.SaleItem(
        sale_id=item.sale_id,
        line_no=item.line_no,
        p_id=item.p_id,
        b_id=item.b_id,
        qty=item.qty,
        price=item.price,
        line_total=item.line_total,
        line_discount=item.line_discount,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def list_sales(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sale).offset(skip).limit(limit).all()


# Suppliers
def create_supplier(db: Session, supplier: schemas.SupplierCreate):
    db_s = models.Supplier(
        firm_name=supplier.firm_name,
        owner_name=supplier.owner_name,
        gst_no=supplier.gst_no,
        phone=supplier.phone,
        address=supplier.address,
        drug_license=supplier.drug_license,
        ifsc=supplier.ifsc,
        bank_acc_no=supplier.bank_acc_no,
    )
    db.add(db_s)
    db.commit()
    db.refresh(db_s)
    return db_s


def list_suppliers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Supplier).offset(skip).limit(limit).all()


# Employees
def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_e = models.Employee(
        name=employee.name,
        salary=employee.salary,
        work_shift=employee.work_shift,
        role=employee.role,
        experience=employee.experience,
    )
    db.add(db_e)
    db.commit()
    db.refresh(db_e)
    return db_e


def list_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()


# Prescriptions helper by customer
def list_prescriptions_by_customer(db: Session, c_id: int):
    return db.query(models.Prescription).filter(models.Prescription.c_id == c_id).all()


# Sale items helper
def get_sale(db: Session, sb_id: int):
    return db.query(models.Sale).filter(models.Sale.sb_id == sb_id).first()


def list_sale_items(db: Session, sale_id: int):
    return db.query(models.SaleItem).filter(models.SaleItem.sale_id == sale_id).all()


# Reports / queries (examples covering common DBMS concepts)
def report_total_sales_by_date(db: Session):
    return db.query(models.Sale.sale_date, func.sum(models.Sale.total).label("total_sales"))


def report_stock_by_product(db: Session):
    return db.query(models.Product.p_id, models.Product.medicine_name, func.sum(models.Batch.qty_available).label("available_qty")).join(models.Batch, models.Batch.p_id == models.Product.p_id).group_by(models.Product.p_id).all()


def search_products_by_name(db: Session, name_substr: str):
    return db.query(models.Product).filter(models.Product.medicine_name.ilike(f"%{name_substr}%")).all()

