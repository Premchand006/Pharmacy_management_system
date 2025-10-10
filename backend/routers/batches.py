from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from database import get_db
import crud
import schemas

router = APIRouter()

@router.post("/batches/", response_model=schemas.Batch)
def create_batch(batch: schemas.BatchCreate, db: Session = Depends(get_db)):
    return crud.create_batch(db=db, batch=batch)

@router.get("/batches/product/{product_id}", response_model=List[schemas.Batch])
def read_product_batches(product_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_batches = crud.get_product_batches(db, product_id=product_id, skip=skip, limit=limit)
    if not db_batches:
        raise HTTPException(status_code=404, detail="No batches found for this product")
    return db_batches