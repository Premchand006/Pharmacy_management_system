from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from database import get_db
import crud
import schemas

router = APIRouter(
    prefix="/purchases",
    tags=["purchases"]
)

@router.post("/", response_model=schemas.Purchase)
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    # Creates purchase and batches via crud.create_purchase
    return crud.create_purchase(db=db, purchase=purchase)

@router.get("/", response_model=List[schemas.Purchase])
def list_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_purchases(db=db, skip=skip, limit=limit)
