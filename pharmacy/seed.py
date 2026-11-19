"""Demo data: a small store with staff, stock, prescriptions and a few weeks of sales.

Brand names are invented. Licence numbers and GSTINs are placeholders in
the right shape, not real registrations.
"""
import random
from datetime import timedelta
from decimal import Decimal

from . import auth
from .billing import SaleRequest, create_sale
from .extensions import db
from .models import (Batch, Customer, Employee, PharmacySettings, Prescription, PrescriptionItem,
                     Product, Purchase, Supplier, day_start_utc, local_today)

ADMIN_PASSWORD = "admin-demo-2026"
STAFF_PASSWORD = "staff-demo-2026"
CUSTOMER_PASSWORD = "customer-demo-2026"

PRODUCTS = [
    # brand, generic, form, strength, packing, schedule, mrp, reorder
    ("Feverex", "Paracetamol", "Tablet", "650 mg", "Strip of 15", "OTC", "33.50", 40),
    ("Citrizen", "Cetirizine", "Tablet", "10 mg", "Strip of 10", "OTC", "22.00", 20),
    ("Gastrolin", "Pantoprazole", "Tablet", "40 mg", "Strip of 15", "H", "118.00", 20),
    ("Amoxy", "Amoxicillin", "Capsule", "500 mg", "Strip of 10", "H", "96.40", 15),
    ("Azimax", "Azithromycin", "Tablet", "500 mg", "Strip of 3", "H1", "71.20", 10),
    ("Cefoz", "Cefixime", "Tablet", "200 mg", "Strip of 10", "H1", "109.00", 10),
    ("Glucomet", "Metformin", "Tablet", "500 mg", "Strip of 20", "H", "38.00", 30),
    ("Amlopres", "Amlodipine", "Tablet", "5 mg", "Strip of 30", "H", "54.60", 20),
    ("Calmora", "Alprazolam", "Tablet", "0.25 mg", "Strip of 15", "NDPS", "41.00", 5),
    ("Hydrasol", "Oral rehydration salts", "Sachet", "21.8 g", "1 sachet", "OTC", "21.00", 50),
    ("Coughex", "Dextromethorphan + Chlorpheniramine", "Syrup", "100 ml", "Bottle", "H", "112.00", 10),
    ("Vitacal", "Calcium + Vitamin D3", "Tablet", "500 mg", "Strip of 15", "OTC", "128.00", 15),
]

CUSTOMERS = [
    ("Ananya Rao", "+91 98450 11201", "14 MG Road, Bengaluru 560001", 34, "Female"),
    ("Rahul Verma", "+91 98102 22311", "B-22 Lajpat Nagar, New Delhi 110024", 46, "Male"),
    ("Fatima Shaikh", "+91 98201 33421", "7 Linking Road, Mumbai 400050", 29, "Female"),
    ("Suresh Iyer", "+91 94440 44531", "3 TTK Road, Chennai 600018", 67, "Male"),
    ("Priya Das", "+91 98300 55641", "21 Park Street, Kolkata 700016", 38, "Female"),
    ("Arjun Reddy", "+91 98490 66751", "Road No. 12, Banjara Hills, Hyderabad 500034", 52, "Male"),
    ("Neha Kulkarni", "+91 98220 77861", "FC Road, Pune 411004", 25, "Female"),
    ("Imran Khan", "+91 94140 88971", "MI Road, Jaipur 302001", 41, "Male"),
]

DOCTORS = [
    ("Dr. Kavita Menon", "KMC-48213", "City Care Clinic, 9 Residency Road, Bengaluru"),
    ("Dr. Sanjay Gupta", "DMC-77120", "Lifeline Hospital, Ring Road, New Delhi"),
    ("Dr. Leena Joseph", "TNMC-30544", "Sunrise Nursing Home, Anna Nagar, Chennai"),
]


def populate(seed=7):
    rng = random.Random(seed)
    today = local_today()

    s = PharmacySettings.get()
    s.name = "Sample Pharmacy (demo)"
    s.address = "12 Market Road, Bengaluru 560002, Karnataka"
    s.phone = "+91 80 4000 0000"
    s.gstin = "29AAAAA0000A1Z5"
    s.state_code = "29"
    s.licence_20 = "KA-B20-DEMO-0001"
    s.licence_21 = "KA-B21-DEMO-0001"
    s.licence_fee_due = today + timedelta(days=400)
    s.invoice_prefix = "SP"

    admin = Employee(name="Asha Nair", username="admin", access="admin", role="Owner and pharmacist",
                     work_shift="General", salary=Decimal("0"), experience=12,
                     pharmacist_reg_no="KSPC-12345", password_hash=auth.hash_password(ADMIN_PASSWORD))
    pharmacist = Employee(name="Meera Pillai", username="meera", access="staff", role="Pharmacist",
                          work_shift="Morning", salary=Decimal("32000"), experience=5,
                          pharmacist_reg_no="KSPC-23456", password_hash=auth.hash_password(STAFF_PASSWORD))
    cashier = Employee(name="Ravi Kumar", username="ravi", access="staff", role="Counter assistant",
                       work_shift="Evening", salary=Decimal("18000"), experience=2,
                       password_hash=pharmacist.password_hash)
    db.session.add_all([admin, pharmacist, cashier])

    customer_hash = auth.hash_password(CUSTOMER_PASSWORD)
    customers = [Customer(name=n, phone=p, address=a, age=age, gender=g, password_hash=customer_hash)
                 for n, p, a, age, g in CUSTOMERS]
    db.session.add_all(customers)

    suppliers = [
        Supplier(firm_name="Karnataka Medical Distributors", owner_name="R. Prakash",
                 gstin="29BBBBB0000B1Z4", drug_licence="KA-20B-DEMO-1001", phone="+91 80 4100 1001",
                 address="Avenue Road, Bengaluru", licence_valid_until=today + timedelta(days=700)),
        Supplier(firm_name="Southern Pharma Agencies", owner_name="S. Lakshmi",
                 gstin="29CCCCC0000C1Z3", drug_licence="KA-20B-DEMO-1002", phone="+91 80 4100 1002",
                 address="Chickpet, Bengaluru", licence_valid_until=today + timedelta(days=20)),
    ]
    db.session.add_all(suppliers)

    products = []
    for brand, generic, form, strength, packing, schedule, mrp, reorder in PRODUCTS:
        products.append(Product(brand_name=brand, medicine_name=generic, form=form, strength=strength,
                                packing=packing, schedule=schedule, hsn_code="30049099",
                                gst_rate=Decimal("5"), mrp=Decimal(mrp), reorder_level=reorder,
                                barcode=f"890{rng.randint(10**9, 10**10 - 1)}"))
    db.session.add_all(products)
    db.session.flush()

    # Two supplier invoices: an older one and a recent one.
    for sup, days_ago in ((suppliers[0], 75), (suppliers[1], 20)):
        received = today - timedelta(days=days_ago)
        purchase = Purchase(s_id=sup.s_id, supplier_invoice_no=f"{sup.firm_name[:3].upper()}-{rng.randint(1000, 9999)}",
                            invoice_date=received, received_on=received, e_id=pharmacist.e_id)
        total = Decimal(0)
        for p in products:
            qty = rng.choice([20, 30, 40, 60]) if p.schedule != "NDPS" else 10
            mrp = Decimal(p.mrp)
            cost = (mrp * Decimal("0.72")).quantize(Decimal("0.01"))
            expiry = received + timedelta(days=rng.randint(200, 900))
            purchase.batches.append(Batch(
                p_id=p.p_id, s_id=sup.s_id, batch_no=f"{p.brand_name[:2].upper()}{rng.randint(1000, 9999)}",
                manufacture_date=received - timedelta(days=rng.randint(30, 120)), expiry_date=expiry,
                cost_price=cost, mrp=mrp, qty_received=qty, qty_available=qty, received_on=received,
                manufacturer_name=f"{p.brand_name} Labs Pvt Ltd", marketer_name=""))
            total += cost * qty
        purchase.total_cost = total
        db.session.add(purchase)
    db.session.flush()

    # Make the report pages interesting: one batch close to expiry, one expired.
    first_batches = Batch.query.order_by(Batch.b_id).limit(2).all()
    first_batches[0].expiry_date = today + timedelta(days=18)
    first_batches[1].expiry_date = today - timedelta(days=5)

    prescriptions = []
    for i, cust in enumerate(customers[:5]):
        name, reg, addr = DOCTORS[i % len(DOCTORS)]
        pres = Prescription(c_id=cust.c_id, doctor_name=name, doctor_reg_no=reg, doctor_address=addr,
                            hospital_name=addr.split(",")[0], date=today - timedelta(days=rng.randint(1, 30)),
                            repeats_allowed=1 if i % 2 else 0)
        rx_products = rng.sample([p for p in products if p.needs_prescription and p.schedule != "NDPS"], 2)
        for line, p in enumerate(rx_products, 1):
            pres.items.append(PrescriptionItem(line_no=line, p_id=p.p_id, dosage="1-0-1", duration="5 days",
                                               qty=rng.randint(1, 2), instructions="After food"))
        prescriptions.append(pres)
    db.session.add_all(prescriptions)
    db.session.flush()

    otc = [p for p in products if not p.needs_prescription]
    # Oldest first, so invoice numbers run in date order.
    for day in sorted(today - timedelta(days=rng.randint(1, 45)) for _ in range(40)):
        cust = rng.choice(customers + [None, None])
        req = SaleRequest(lines=[(p.p_id, rng.randint(1, 3)) for p in rng.sample(otc, rng.randint(1, 3))],
                          billed_by=rng.choice([pharmacist, cashier]), customer=cust,
                          payment_mode=rng.choice(["Cash", "UPI", "UPI", "Card"]), today=day)
        sale = create_sale(req)
        sale.sold_at = day_start_utc(day) + timedelta(hours=rng.randint(4, 14), minutes=rng.randint(0, 59))
    for pres in prescriptions[:3]:
        req = SaleRequest(lines=[(i.p_id, i.qty) for i in pres.items], billed_by=pharmacist,
                          prescription=pres, payment_mode="UPI", today=today)
        create_sale(req)

    db.session.commit()
