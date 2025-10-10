from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import crud
import schemas
from database import get_db
from auth import check_admin_access

router = APIRouter()

# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": date.today().isoformat()}

# Enhanced Customer endpoints
@router.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, customer=customer)

@router.get("/customers/", response_model=List[schemas.Customer])
def read_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    customers = crud.get_customers(db, skip=skip, limit=limit, search=search)
    return customers

@router.get("/customers/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(
    customer_id: int,
    customer: schemas.CustomerUpdate,
    db: Session = Depends(get_db)
):
    db_customer = crud.update_customer(db, customer_id, customer)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    success = crud.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

# Enhanced Product endpoints
@router.post("/products/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _=Depends(check_admin_access)
):
    return crud.create_product(db=db, product=product)

@router.get("/products/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    return crud.get_products(
        db,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price
    )

@router.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_admin_access)
):
    db_product = crud.update_product(db, product_id, product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_admin_access)
):
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Enhanced Batch endpoints
@router.post("/batches/", response_model=schemas.Batch)
def create_batch(
    batch: schemas.BatchCreate,
    db: Session = Depends(get_db),
    _=Depends(check_admin_access)
):
    return crud.create_batch(db=db, batch=batch)

@router.get("/batches/", response_model=List[schemas.Batch])
def read_batches(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    expiring_before: Optional[date] = None,
    min_quantity: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return crud.get_batches(
        db,
        skip=skip,
        limit=limit,
        product_id=product_id,
        expiring_before=expiring_before,
        min_quantity=min_quantity
    )

# Enhanced Sale endpoints
@router.post("/sales/", response_model=schemas.Sale)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    return crud.create_sale(db=db, sale=sale)

@router.get("/sales/", response_model=List[schemas.Sale])
def read_sales(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    customer_id: Optional[int] = None,
    min_total: Optional[float] = None,
    db: Session = Depends(get_db)
):
    return crud.get_sales(
        db,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id,
        min_total=min_total
    )

# Analytics endpoints
@router.get("/analytics/sales-summary")
def get_sales_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    _=Depends(check_admin_access)
):
    return crud.get_sales_summary(db, start_date, end_date)

@router.get("/analytics/inventory-status")
def get_inventory_status(
    db: Session = Depends(get_db),
    _=Depends(check_admin_access)
):
    return crud.get_inventory_status(db)

@router.get("/analytics/expiring-products")
def get_expiring_products(
    days: int = Query(30, description="Number of days to check for expiry"),
    db: Session = Depends(get_db),
    _=Depends(check_admin_access)
):
    return crud.get_expiring_products(db, days)