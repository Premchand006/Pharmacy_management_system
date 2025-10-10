from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from database import get_db
import crud
import schemas

router = APIRouter()

@router.post("/sales/", response_model=schemas.Sale)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    return crud.create_sale(db=db, sale=sale)

@router.get("/sales/", response_model=List[schemas.Sale])
def read_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sales = crud.get_sales(db, skip=skip, limit=limit)
    return sales

@router.get("/sales/customer/{customer_id}", response_model=List[schemas.Sale])
def read_customer_sales(customer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sales = crud.get_customer_sales(db, customer_id=customer_id, skip=skip, limit=limit)
    if not sales:
        raise HTTPException(status_code=404, detail="No sales found for this customer")
    return sales

@router.get("/sales/filter/", response_model=List[schemas.Sale])
def read_filtered_sales(
    start_date: date = None,
    end_date: date = None,
    employee_id: int = None,
    customer_id: int = None,
    db: Session = Depends(get_db)
):
    sales = crud.get_filtered_sales(
        db,
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id,
        customer_id=customer_id
    )
    return sales