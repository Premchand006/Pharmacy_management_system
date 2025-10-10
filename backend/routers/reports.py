from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import crud
import schemas

router = APIRouter()

@router.get("/reports/near-expiry", response_model=List[schemas.Batch])
def get_near_expiry_report(days: int = 30, db: Session = Depends(get_db)):
    """
    Get a report of batches that are nearing their expiry date.
    """
    return crud.get_near_expiry_batches(db=db, days=days)

@router.get("/reports/stock", response_model=List[schemas.StockReport])
def get_stock_report(db: Session = Depends(get_db)):
    """
    Get a report of the current stock levels for all products.
    """
    return crud.get_stock_report(db=db)

@router.get("/reports/top-selling", response_model=List[schemas.TopSellingProduct])
def get_top_selling_products_report(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get a report of the top-selling products.
    """
    return crud.get_top_selling_products(db=db, limit=limit)

@router.get("/reports/batch-traceability")
def get_batch_traceability(db: Session = Depends(get_db)):
    """
    Get batch-level inventory and regulatory traceability data.
    """
    return crud.get_batch_traceability(db=db)

@router.get("/reports/search-products")
def search_products(
    search: Optional[str] = Query(None),
    expiry_date: Optional[str] = Query(None),
    quantity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search products with advanced filtering.
    """
    return crud.search_products(db=db, search=search, expiry_date=expiry_date, quantity=quantity)

@router.get("/reports/search-customers")
def search_customers(
    search: Optional[str] = Query(None),
    bill_amount: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search customers with analytics filtering.
    """
    return crud.search_customers(db=db, search=search, bill_amount=bill_amount)
