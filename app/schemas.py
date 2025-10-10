
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime


class CustomerBase(BaseModel):
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    c_id: int

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    brand_name: Optional[str] = None
    medicine_name: str
    form: Optional[str] = None
    strength: Optional[str] = None
    packing: Optional[str] = None
    prescription_type: Optional[str] = None
    mrp: Optional[float] = None
    unit_price: Optional[float] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    p_id: int

    class Config:
        orm_mode = True


class BatchBase(BaseModel):
    p_id: int
    s_id: Optional[int] = None
    batch_no: Optional[str] = None
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None
    cost_price: Optional[float] = None
    qty_received: Optional[int] = None
    qty_available: Optional[int] = None
    received_on: Optional[date] = None
    manufacture_name: Optional[str] = None
    marketer_name: Optional[str] = None

    @validator("manufacture_date", "expiry_date", "received_on", pre=True)
    def _parse_dates(cls, v):
        if v is None:
            return v
        if isinstance(v, date):
            return v
        return date.fromisoformat(v)


class BatchCreate(BatchBase):
    pass


class Batch(BatchBase):
    b_id: int

    class Config:
        orm_mode = True


class PrescriptionBase(BaseModel):
    c_id: Optional[int] = None
    dr_id: Optional[int] = None
    doctor_license_no: Optional[str] = None
    date: Optional[date] = None
    validity: Optional[int] = None
    hospital_name: Optional[str] = None

    @validator("date", pre=True)
    def _parse_prescription_date(cls, v):
        if v is None:
            return v
        if isinstance(v, date):
            return v
        return date.fromisoformat(v)


class PrescriptionCreate(PrescriptionBase):
    pass


class Prescription(PrescriptionBase):
    pres_id: int

    class Config:
        orm_mode = True


class PrescriptionItemBase(BaseModel):
    pres_id: int
    line_no: int
    product_id: Optional[int] = None
    dosage: Optional[str] = None
    duration: Optional[str] = None
    qty: Optional[int] = None
    instructions: Optional[str] = None


class PrescriptionItemCreate(PrescriptionItemBase):
    pass


class PrescriptionItem(PrescriptionItemBase):
    class Config:
        orm_mode = True


class SaleBase(BaseModel):
    c_id: Optional[int] = None
    e_id: Optional[int] = None
    pres_id: Optional[int] = None
    sale_date: Optional[datetime] = None
    payment_mode: Optional[str] = None
    amount: Optional[float] = None
    tax: Optional[float] = None
    discount: Optional[float] = None
    total: Optional[float] = None
    status: Optional[str] = None

    @validator("sale_date", pre=True)
    def _parse_sale_date(cls, v):
        if v is None:
            return v
        if isinstance(v, datetime):
            return v
        return datetime.fromisoformat(v)


class SaleCreate(SaleBase):
    pass


class Sale(SaleBase):
    sb_id: int

    class Config:
        orm_mode = True


class SaleItemBase(BaseModel):
    sale_id: int
    line_no: int
    p_id: Optional[int] = None
    b_id: Optional[int] = None
    qty: Optional[int] = None
    price: Optional[float] = None
    line_total: Optional[float] = None
    line_discount: Optional[float] = None


class SaleItemCreate(SaleItemBase):
    pass


class SaleItem(SaleItemBase):
    class Config:
        orm_mode = True


# Supplier schemas
class SupplierBase(BaseModel):
    firm_name: str
    owner_name: Optional[str] = None
    gst_no: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    drug_license: Optional[str] = None
    ifsc: Optional[str] = None
    bank_acc_no: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class Supplier(SupplierBase):
    s_id: int

    class Config:
        orm_mode = True


# Employee schemas
class EmployeeBase(BaseModel):
    name: str
    salary: Optional[float] = None
    work_shift: Optional[str] = None
    role: Optional[str] = None
    experience: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    e_id: int

    class Config:
        orm_mode = True

