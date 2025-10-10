from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
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
