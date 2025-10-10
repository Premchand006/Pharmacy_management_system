from pydantic import BaseModel, validator
from typing import Optional
from datetime import date

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

    class Config:
        orm_mode = True

    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('Age must be between 0 and 150')
        return v

    @validator('gender')
    def validate_gender(cls, v):
        if v is not None and v not in ['M', 'F', 'O']:
            raise ValueError('Gender must be M, F, or O')
        return v

class ProductUpdate(BaseModel):
    brand_name: Optional[str] = None
    medicine_name: Optional[str] = None
    form: Optional[str] = None
    strength: Optional[str] = None
    packing: Optional[str] = None
    prescription_type: Optional[str] = None
    mrp: Optional[float] = None
    unit_price: Optional[float] = None

    class Config:
        orm_mode = True

    @validator('mrp', 'unit_price')
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price cannot be negative')
        return v

class BatchUpdate(BaseModel):
    batch_no: Optional[str] = None
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None
    cost_price: Optional[float] = None
    qty_received: Optional[int] = None
    qty_available: Optional[int] = None
    manufacture_name: Optional[str] = None
    marketer_name: Optional[str] = None

    class Config:
        orm_mode = True

    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if v and 'manufacture_date' in values and values['manufacture_date']:
            if v <= values['manufacture_date']:
                raise ValueError('Expiry date must be after manufacture date')
        return v