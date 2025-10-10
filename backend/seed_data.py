from sqlalchemy.orm import Session
from models import Base, Customer, Employee, Supplier, Product, Prescription, PrescriptionItem, Batch, Purchase, Sale, SaleItem
from sqlalchemy import create_engine
from datetime import date

# Update the path to your SQLite DB if needed
engine = create_engine('sqlite:///pharmacy.db')
Base.metadata.create_all(engine)
session = Session(bind=engine)

# 1️⃣ Customers
customers = [
    Customer(c_id=1, name='Rahul Sharma', phone='9876543210', address='123 MG Road, Delhi', age=35, gender='M'),
    Customer(c_id=2, name='Sneha Kapoor', phone='9123456780', address='45 Park Street, Kolkata', age=28, gender='F'),
    Customer(c_id=3, name='Amit Verma', phone='9988776655', address='78 Marine Drive, Mumbai', age=42, gender='M'),
    Customer(c_id=4, name='Pooja Singh', phone='9001122334', address='21 Residency Rd, Bangalore', age=31, gender='F'),
    Customer(c_id=5, name='Karan Mehta', phone='9012345678', address='12 Brigade Rd, Bangalore', age=29, gender='M'),
]
session.add_all(customers)

# 2️⃣ Employees
employees = [
    Employee(e_id=101, name='Sunil Kumar', salary=25000, work_shift='Morning', role='Pharmacist', experience=5),
    Employee(e_id=102, name='Anita Joshi', salary=28000, work_shift='Evening', role='Cashier', experience=3),
    Employee(e_id=103, name='Rakesh Mehra', salary=30000, work_shift='Morning', role='Store Manager', experience=7),
    Employee(e_id=104, name='Divya Singh', salary=27000, work_shift='Evening', role='Pharmacist', experience=4),
    Employee(e_id=105, name='Vikram Das', salary=26000, work_shift='Morning', role='Cashier', experience=2),
]
session.add_all(employees)

# 3️⃣ Suppliers
suppliers = [
    Supplier(s_id=201, firm_name='HealthCare Pvt Ltd', owner_name='Rajesh Kumar', gst_no='GSTIN12345', phone='9876501234', address='Sector 10, Noida', drug_license='DL1234', ifsc='HDFC0001', bank_acc_no='1234567890'),
    Supplier(s_id=202, firm_name='MediSuppliers', owner_name='Vikram Singh', gst_no='GSTIN67890', phone='9988771122', address='MG Road, Delhi', drug_license='DL5678', ifsc='SBI0002', bank_acc_no='9876543210'),
    Supplier(s_id=203, firm_name='PharmaPlus', owner_name='Anil Jain', gst_no='GSTIN54321', phone='9876512345', address='Sector 22, Gurgaon', drug_license='DL9101', ifsc='ICIC0003', bank_acc_no='1122334455'),
    Supplier(s_id=204, firm_name='LifeMed', owner_name='Rekha Verma', gst_no='GSTIN09876', phone='9988123456', address='Kolkata', drug_license='DL1122', ifsc='HDFC0004', bank_acc_no='5566778899'),
    Supplier(s_id=205, firm_name='MedicoCare', owner_name='Suresh Rao', gst_no='GSTIN56789', phone='9876540987', address='Mumbai', drug_license='DL3344', ifsc='SBI0005', bank_acc_no='6677889900'),
]
session.add_all(suppliers)

# 4️⃣ Products
products = [
    Product(p_id=301, brand_name='Cipla', medicine_name='Paracetamol', form='Tablet', strength='500mg', packing='Strip of 10', prescription_type='OTC', mrp=50, unit_price=35),
    Product(p_id=302, brand_name='Sun Pharma', medicine_name='Amoxicillin', form='Capsule', strength='250mg', packing='Strip of 10', prescription_type='Prescription', mrp=120, unit_price=90),
    Product(p_id=303, brand_name='Bayer', medicine_name='Ibuprofen', form='Tablet', strength='400mg', packing='Strip of 10', prescription_type='OTC', mrp=80, unit_price=60),
    Product(p_id=304, brand_name='Zydus', medicine_name='Vitamin C', form='Tablet', strength='500mg', packing='Bottle of 60', prescription_type='OTC', mrp=150, unit_price=120),
    Product(p_id=305, brand_name='Mankind', medicine_name='Cetirizine', form='Tablet', strength='10mg', packing='Strip of 10', prescription_type='OTC', mrp=40, unit_price=25),
]
session.add_all(products)

# 5️⃣ Prescriptions
prescriptions = [
    Prescription(pres_id=401, c_id=1, dr_id='DR101', doctor_license_no='LIC1234', date=date(2025,10,1), validity=10, hospital_name='Apollo Hospital'),
    Prescription(pres_id=402, c_id=2, dr_id='DR102', doctor_license_no='LIC5678', date=date(2025,10,5), validity=15, hospital_name='Fortis Hospital'),
    Prescription(pres_id=403, c_id=3, dr_id='DR103', doctor_license_no='LIC9101', date=date(2025,10,8), validity=7, hospital_name='Max Hospital'),
    Prescription(pres_id=404, c_id=4, dr_id='DR104', doctor_license_no='LIC1121', date=date(2025,10,10), validity=5, hospital_name='Medanta Hospital'),
    Prescription(pres_id=405, c_id=5, dr_id='DR105', doctor_license_no='LIC3141', date=date(2025,10,12), validity=12, hospital_name='Columbia Asia'),
]
session.add_all(prescriptions)

# 6️⃣ Prescription Items
prescription_items = [
    PrescriptionItem(pres_id=401, line_no=1, product_id=301, dosage='1 Tablet', duration='5 Days', qty=5, instructions='After meals'),
    PrescriptionItem(pres_id=401, line_no=2, product_id=302, dosage='1 Capsule', duration='7 Days', qty=7, instructions='Twice daily'),
    PrescriptionItem(pres_id=402, line_no=1, product_id=303, dosage='2 Tablets', duration='3 Days', qty=6, instructions='After meals'),
    PrescriptionItem(pres_id=403, line_no=1, product_id=304, dosage='1 Tablet', duration='10 Days', qty=10, instructions='Once daily'),
    PrescriptionItem(pres_id=404, line_no=1, product_id=305, dosage='1 Tablet', duration='5 Days', qty=5, instructions='Before meals'),
]
session.add_all(prescription_items)

# 7️⃣ Batches
batches = [
    Batch(b_id=501, p_id=301, s_id=201, batch_no='BCH101', manufacture_date=date(2025,1,1), expiry_date=date(2026,1,1), cost_price=25, qty_received=100, qty_available=95, received_on=date(2025,1,5), manufacture_name='Cipla Ltd', marketer_name='HealthCare Pvt Ltd'),
    Batch(b_id=502, p_id=302, s_id=202, batch_no='BCH102', manufacture_date=date(2025,2,1), expiry_date=date(2026,2,1), cost_price=70, qty_received=200, qty_available=193, received_on=date(2025,2,3), manufacture_name='Sun Pharma', marketer_name='MediSuppliers'),
    Batch(b_id=503, p_id=303, s_id=201, batch_no='BCH103', manufacture_date=date(2025,3,1), expiry_date=date(2026,3,1), cost_price=45, qty_received=150, qty_available=144, received_on=date(2025,3,5), manufacture_name='Bayer', marketer_name='HealthCare Pvt Ltd'),
    Batch(b_id=504, p_id=304, s_id=203, batch_no='BCH104', manufacture_date=date(2025,4,1), expiry_date=date(2026,4,1), cost_price=100, qty_received=120, qty_available=115, received_on=date(2025,4,3), manufacture_name='Zydus', marketer_name='PharmaPlus'),
    Batch(b_id=505, p_id=305, s_id=204, batch_no='BCH105', manufacture_date=date(2025,5,1), expiry_date=date(2026,5,1), cost_price=20, qty_received=80, qty_available=75, received_on=date(2025,5,3), manufacture_name='Mankind', marketer_name='LifeMed'),
]
session.add_all(batches)

# 8️⃣ Purchases
purchases = [
    Purchase(purchase_id=601, b_id=501, s_id=201, p_id=301, date=date(2025,1,5), cost=2500, status='Received'),
    Purchase(purchase_id=602, b_id=502, s_id=202, p_id=302, date=date(2025,2,3), cost=14000, status='Received'),
    Purchase(purchase_id=603, b_id=503, s_id=201, p_id=303, date=date(2025,3,5), cost=6750, status='Received'),
    Purchase(purchase_id=604, b_id=504, s_id=203, p_id=304, date=date(2025,4,3), cost=12000, status='Received'),
    Purchase(purchase_id=605, b_id=505, s_id=204, p_id=305, date=date(2025,5,3), cost=1600, status='Received'),
]
session.add_all(purchases)

# 9️⃣ Sales
sales = [
    Sale(sb_id=701, c_id=1, e_id=101, pres_id=401, sale_date=date(2025,10,2), payment_mode='Cash', amount=500, tax=50, discount=20, total=530, status='Completed'),
    Sale(sb_id=702, c_id=2, e_id=102, pres_id=402, sale_date=date(2025,10,6), payment_mode='Card', amount=480, tax=48, discount=10, total=518, status='Completed'),
    Sale(sb_id=703, c_id=3, e_id=103, pres_id=403, sale_date=date(2025,10,8), payment_mode='UPI', amount=600, tax=60, discount=15, total=645, status='Completed'),
    Sale(sb_id=704, c_id=4, e_id=104, pres_id=404, sale_date=date(2025,10,10), payment_mode='Cash', amount=300, tax=30, discount=5, total=325, status='Completed'),
    Sale(sb_id=705, c_id=5, e_id=105, pres_id=405, sale_date=date(2025,10,12), payment_mode='Card', amount=450, tax=45, discount=10, total=485, status='Completed'),
]
session.add_all(sales)

# 🔟 Sale Items
sale_items = [
    SaleItem(sale_id=701, line_no=1, p_id=301, b_id=501, qty=5, price=35, line_total=175, line_discount=5),
    SaleItem(sale_id=701, line_no=2, p_id=302, b_id=502, qty=7, price=90, line_total=630, line_discount=15),
    SaleItem(sale_id=702, line_no=1, p_id=303, b_id=503, qty=6, price=60, line_total=360, line_discount=10),
    SaleItem(sale_id=703, line_no=1, p_id=304, b_id=504, qty=10, price=120, line_total=1200, line_discount=20),
    SaleItem(sale_id=704, line_no=1, p_id=305, b_id=505, qty=5, price=25, line_total=125, line_discount=5),
]
session.add_all(sale_items)

session.commit()
session.close()
print('Sample data seeded successfully.')
