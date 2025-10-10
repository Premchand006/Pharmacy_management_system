from pydantic import BaseModel
from datetime import date
from typing import List

class CustomerBase(BaseModel):
    name: str
    phone: str
    address: str
    age: int
    gender: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    c_id: int

    class Config:
        orm_mode = True

class CustomerUpdate(CustomerBase):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    age: int | None = None
    gender: str | None = None

class EmployeeBase(BaseModel):
    name: str
    salary: float
    work_shift: str
    role: str
    experience: int

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    e_id: int

    class Config:
        orm_mode = True

class SupplierBase(BaseModel):
    firm_name: str
    owner_name: str
    gst_no: str
    phone: str
    address: str
    drug_license: str
    ifsc: str
    bank_acc_no: str

class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    s_id: int

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    brand_name: str
    medicine_name: str
    form: str
    strength: str
    packing: str
    prescription_type: str
    mrp: float
    unit_price: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    p_id: int

    class Config:
        orm_mode = True

class ProductUpdate(ProductBase):
    brand_name: str | None = None
    medicine_name: str | None = None
    form: str | None = None
    strength: str | None = None
    packing: str | None = None
    prescription_type: str | None = None
    mrp: float | None = None
    unit_price: float | None = None

class PrescriptionItemBase(BaseModel):
    product_id: int
    dosage: str
    duration: str
    qty: int
    instructions: str

class PrescriptionItemCreate(PrescriptionItemBase):
    pass

class PrescriptionItem(PrescriptionItemBase):
    pres_id: int
    line_no: int

    class Config:
        orm_mode = True

class PrescriptionBase(BaseModel):
    c_id: int
    dr_id: str
    doctor_license_no: str
    date: date
    validity: int
    hospital_name: str
    items: List[PrescriptionItemCreate]

class PrescriptionCreate(PrescriptionBase):
    pass

class Prescription(PrescriptionBase):
    pres_id: int
    items: List[PrescriptionItem] = []

    class Config:
        orm_mode = True

class BatchBase(BaseModel):
    p_id: int
    s_id: int
    batch_no: str
    manufacture_date: date
    expiry_date: date
    cost_price: float
    qty_received: int
    qty_available: int
    received_on: date
    manufacture_name: str
    marketer_name: str

class BatchCreate(BatchBase):
    pass

class Batch(BatchBase):
    b_id: int

    class Config:
        orm_mode = True

class PurchaseBase(BaseModel):
    b_id: int
    s_id: int
    p_id: int
    date: date
    cost: float
    status: str

class PurchaseCreate(PurchaseBase):
    pass

class Purchase(PurchaseBase):
    purchase_id: int

    class Config:
        orm_mode = True

class SaleItemBase(BaseModel):
    p_id: int
    b_id: int
    qty: int
    price: float
    line_total: float
    line_discount: float

class SaleItemCreate(SaleItemBase):
    pass

class SaleItem(SaleItemBase):
    sale_id: int
    line_no: int

    class Config:
        orm_mode = True

class SaleBase(BaseModel):
    c_id: int
    e_id: int
    pres_id: int
    sale_date: date
    payment_mode: str
    amount: float
    tax: float
    discount: float
    total: float
    status: str
    items: List[SaleItemCreate]

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    sb_id: int
    items: List[SaleItem] = []

    class Config:
        orm_mode = True

class StockReport(BaseModel):
    p_id: int
    medicine_name: str
    total_quantity: int

    class Config:
        orm_mode = True

class TopSellingProduct(BaseModel):
    p_id: int
    medicine_name: str
    total_sold: int

    class Config:
        orm_mode = True