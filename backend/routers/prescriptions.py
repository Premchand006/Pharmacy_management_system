from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from database import get_db
import crud
import schemas

router = APIRouter()

@router.post("/prescriptions/", response_model=schemas.Prescription)
def create_prescription(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_db)):
    return crud.create_prescription(db=db, prescription=prescription)

@router.get("/prescriptions/customer/{customer_id}", response_model=List[schemas.Prescription])
def read_customer_prescriptions(customer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_prescriptions = crud.get_customer_prescriptions(db, customer_id=customer_id, skip=skip, limit=limit)
    # Return empty list if none found (frontend handles empty state)
    return db_prescriptions or []


@router.get('/prescriptions/{pres_id}/items')
def read_prescription_items(pres_id: int, db: Session = Depends(get_db)):
    pres = crud.get_prescription(db, pres_id)
    if not pres:
        raise HTTPException(status_code=404, detail='Prescription not found')
    # collect items
    return pres.items or []