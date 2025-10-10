from sqlalchemy.orm import Session
import models
import schemas
from datetime import date
from typing import Optional
from fastapi import HTTPException

# Customer
def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.c_id == customer_id).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(models.Customer)
    if search:
        search = f"%{search}%"
        query = query.filter(
            models.Customer.name.ilike(search) |
            models.Customer.phone.ilike(search) |
            models.Customer.address.ilike(search)
        )
    return query.offset(skip).limit(limit).all()

def update_customer(db: Session, customer_id: int, customer_update: schemas.CustomerUpdate):
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    
    update_data = customer_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)
    
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# Employee
def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.e_id == employee_id).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

# Supplier
def create_supplier(db: Session, supplier: schemas.SupplierCreate):
    db_supplier = models.Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def get_supplier(db: Session, supplier_id: int):
    return db.query(models.Supplier).filter(models.Supplier.s_id == supplier_id).first()

def get_suppliers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Supplier).offset(skip).limit(limit).all()

# Product
def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.p_id == product_id).first()

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None
):
    query = db.query(models.Product)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            models.Product.medicine_name.ilike(search) |
            models.Product.brand_name.ilike(search)
        )
    
    if category:
        query = query.filter(models.Product.form == category)
    
    if min_price is not None:
        query = query.filter(models.Product.unit_price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Product.unit_price <= max_price)
        
    return query.offset(skip).limit(limit).all()

def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
    
def delete_customer(db: Session, customer_id: int):
    customer = db.query(models.Customer).filter(models.Customer.c_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return True

def delete_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.p_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return True

def delete_employee(db: Session, employee_id: int):
    employee = db.query(models.Employee).filter(models.Employee.e_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return True

# Prescription
def create_prescription(db: Session, prescription: schemas.PrescriptionCreate):
    db_prescription = models.Prescription(
        c_id=prescription.c_id,
        dr_id=prescription.dr_id,
        doctor_license_no=prescription.doctor_license_no,
        date=prescription.date,
        validity=prescription.validity,
        hospital_name=prescription.hospital_name
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)

    for idx, item in enumerate(prescription.items, 1):
        db_item = models.PrescriptionItem(
            pres_id=db_prescription.pres_id,
            line_no=idx,
            **item.dict()
        )
        db.add(db_item)
    
    db.commit()
    return db_prescription

def get_prescription(db: Session, prescription_id: int):
    return db.query(models.Prescription).filter(models.Prescription.pres_id == prescription_id).first()

def get_customer_prescriptions(db: Session, customer_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Prescription).filter(models.Prescription.c_id == customer_id).offset(skip).limit(limit).all()

# Batch
def create_batch(db: Session, batch: schemas.BatchCreate):
    db_batch = models.Batch(**batch.dict())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

def get_batch(db: Session, batch_id: int):
    return db.query(models.Batch).filter(models.Batch.b_id == batch_id).first()

def get_product_batches(db: Session, product_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Batch).filter(models.Batch.p_id == product_id).offset(skip).limit(limit).all()

# Sale
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
        status=sale.status
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    for idx, item in enumerate(sale.items, 1):
        db_item = models.SaleItem(
            sale_id=db_sale.sb_id,
            line_no=idx,
            **item.dict()
        )
        db.add(db_item)
        
        # Update batch quantity
        batch = get_batch(db, item.b_id)
        if batch:
            if batch.qty_available < item.qty:
                raise HTTPException(status_code=400, detail=f"Insufficient quantity available for batch {batch.batch_no}")
            batch.qty_available -= item.qty
            db.add(batch)
    
    db.commit()
    return db_sale

def get_sale(db: Session, sale_id: int):
    return db.query(models.Sale).filter(models.Sale.sb_id == sale_id).first()

def get_sales(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sale).offset(skip).limit(limit).all()

def get_customer_sales(db: Session, customer_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Sale).filter(models.Sale.c_id == customer_id).offset(skip).limit(limit).all()

def get_filtered_sales(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None,
                      employee_id: Optional[int] = None, customer_id: Optional[int] = None):
    query = db.query(models.Sale)
    
    if start_date:
        query = query.filter(models.Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(models.Sale.sale_date <= end_date)
    if employee_id:
        query = query.filter(models.Sale.e_id == employee_id)
    if customer_id:
        query = query.filter(models.Sale.c_id == customer_id)
        
    return query.all()

# Purchases
def create_purchase(db: Session, purchase: schemas.PurchaseCreate):
    # Create purchase record
    db_purchase = models.Purchase(
        b_id=purchase.b_id,
        s_id=purchase.s_id,
        p_id=purchase.p_id,
        date=purchase.date,
        cost=purchase.cost,
        status=purchase.status,
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)

    # Create a batch for this purchase (if needed) and update product stock
    # Here we create a Batch record using purchase info. In a more complex system,
    # purchases would contain multiple line items; this simplified model assumes
    # each purchase maps to a single batch.
    db_batch = models.Batch(
        p_id=purchase.p_id,
        s_id=purchase.s_id,
        batch_no=str(db_purchase.purchase_id),
        manufacture_date=purchase.date,
        expiry_date=purchase.date,
        cost_price=purchase.cost,
        qty_received=0,
        qty_available=0,
        received_on=purchase.date,
        manufacture_name="",
        marketer_name="",
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)

    return db_purchase

def list_purchases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Purchase).offset(skip).limit(limit).all()

# Reports
def get_near_expiry_batches(db: Session, days: int):
    """
    Returns batches that will expire within the given number of days.
    """
    from datetime import date, timedelta
    expiry_threshold = date.today() + timedelta(days=days)
    return db.query(models.Batch).filter(
        models.Batch.expiry_date <= expiry_threshold,
        models.Batch.expiry_date > date.today()
    ).all()

def get_stock_report(db: Session):
    """
    Returns a report of the current stock levels for all products.
    """
    from sqlalchemy import func
    return db.query(
        models.Product.p_id,
        models.Product.medicine_name,
        func.sum(models.Batch.qty_available).label('total_quantity')
    ).join(models.Batch, models.Product.p_id == models.Batch.p_id, isouter=True).group_by(models.Product.p_id).all()

def get_top_selling_products(db: Session, limit: int = 10):
    """
    Returns the top-selling products based on the quantity sold.
    """
    from sqlalchemy import func
    return db.query(
        models.Product.p_id,
        models.Product.medicine_name,
        func.sum(models.SaleItem.qty).label('total_sold')
    ).join(models.SaleItem, models.Product.p_id == models.SaleItem.p_id).group_by(models.Product.p_id).order_by(func.sum(models.SaleItem.qty).desc()).limit(limit).all()

# --- Additional helpers used by API v1 and reports ---

def get_batches(db: Session, skip: int = 0, limit: int = 100, product_id: Optional[int] = None,
                expiring_before: Optional[date] = None, min_quantity: Optional[int] = None):
    """
    Flexible batch listing used by API v1: supports filtering by product, expiry date and minimum quantity.
    """
    query = db.query(models.Batch)
    if product_id is not None:
        query = query.filter(models.Batch.p_id == product_id)
    if expiring_before is not None:
        query = query.filter(models.Batch.expiry_date <= expiring_before)
    if min_quantity is not None:
        query = query.filter(models.Batch.qty_available >= min_quantity)
    return query.offset(skip).limit(limit).all()


def get_sales_summary(db: Session, start_date: date, end_date: date):
    """
    Return a simple sales summary between two dates: total_sales_amount and total_transactions.
    """
    from sqlalchemy import func
    result = db.query(
        func.count(models.Sale.sb_id).label('transactions'),
        func.coalesce(func.sum(models.Sale.total), 0).label('total_sales')
    ).filter(models.Sale.sale_date >= start_date, models.Sale.sale_date <= end_date).one()

    return {
        'transactions': int(result.transactions or 0),
        'total_sales': float(result.total_sales or 0.0),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }


def get_inventory_status(db: Session):
    """
    Return inventory status per product: product id, name, total quantity available and number of batches.
    """
    from sqlalchemy import func
    rows = db.query(
        models.Product.p_id,
        models.Product.medicine_name,
        func.coalesce(func.sum(models.Batch.qty_available), 0).label('total_quantity'),
        func.count(models.Batch.b_id).label('batch_count')
    ).outerjoin(models.Batch, models.Product.p_id == models.Batch.p_id).group_by(models.Product.p_id).all()

    return [
        {
            'p_id': r.p_id,
            'medicine_name': r.medicine_name,
            'total_quantity': int(r.total_quantity or 0),
            'batch_count': int(r.batch_count or 0)
        }
        for r in rows
    ]


def get_expiring_products(db: Session, days: int = 30):
    """
    Return batches/products that will expire within the next `days` days.
    Similar to get_near_expiry_batches but kept for API v1 naming.
    """
    from datetime import date, timedelta
    threshold = date.today() + timedelta(days=days)
    rows = db.query(models.Batch).filter(models.Batch.expiry_date <= threshold, models.Batch.expiry_date > date.today()).all()
    return rows

# Additional CRUD functions for enhanced features
def get_batch_traceability(db: Session):
    """
    Get batch-level inventory and regulatory traceability data.
    """
    from sqlalchemy import func
    result = db.query(
        models.Batch.b_id,
        models.Batch.p_id,
        models.Product.medicine_name,
        models.Supplier.firm_name.label('supplier_name'),
        models.Batch.received_on.label('purchase_date'),
        models.Batch.expiry_date,
        models.Batch.qty_available.label('quantity'),
        func.count(models.SaleItem.sale_id).label('sales_count')
    ).join(models.Product, models.Batch.p_id == models.Product.p_id)\
     .join(models.Supplier, models.Batch.s_id == models.Supplier.s_id)\
     .outerjoin(models.SaleItem, models.Batch.b_id == models.SaleItem.b_id)\
     .group_by(models.Batch.b_id).all()
    
    return [
        {
            'b_id': r.b_id,
            'p_id': r.p_id,
            'medicine_name': r.medicine_name,
            'supplier_name': r.supplier_name,
            'purchase_date': r.purchase_date,
            'expiry_date': r.expiry_date,
            'quantity': r.quantity,
            'sales_count': r.sales_count or 0
        }
        for r in result
    ]

def search_products(db: Session, search: str = None, expiry_date: str = None, quantity: str = None):
    """
    Search products with advanced filtering.
    """
    query = db.query(models.Product)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            models.Product.medicine_name.ilike(search_term) |
            models.Product.brand_name.ilike(search_term)
        )
    
    if expiry_date:
        query = query.join(models.Batch).filter(models.Batch.expiry_date == expiry_date)
    
    if quantity:
        try:
            qty = int(quantity)
            query = query.join(models.Batch).filter(models.Batch.qty_available >= qty)
        except ValueError:
            pass
    
    return query.all()

def search_customers(db: Session, search: str = None, bill_amount: str = None):
    """
    Search customers with analytics filtering.
    """
    from sqlalchemy import func
    
    query = db.query(
        models.Customer.c_id,
        models.Customer.name,
        models.Customer.phone,
        func.count(models.Sale.sb_id).label('total_purchases'),
        func.avg(models.Sale.total).label('avg_bill_amount')
    ).outerjoin(models.Sale, models.Customer.c_id == models.Sale.c_id)\
     .group_by(models.Customer.c_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            models.Customer.name.ilike(search_term) |
            models.Customer.phone.ilike(search_term)
        )
    
    if bill_amount:
        try:
            amount = float(bill_amount)
            query = query.having(func.avg(models.Sale.total) >= amount)
        except ValueError:
            pass
    
    return query.all()

def get_sale_items(db: Session, sale_id: int):
    """
    Get all items for a specific sale.
    """
    return db.query(models.SaleItem).filter(models.SaleItem.sale_id == sale_id).all()

# --- end added helpers ---