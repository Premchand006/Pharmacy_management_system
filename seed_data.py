"""
Seed data script to populate the Pharmacy Management System database with sample data
"""
from datetime import date, datetime, timedelta
import random
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def seed_database():
    """Populate database with sample data"""

    # Import here to avoid circular imports
    from app import app, db, Customer, Employee, Supplier, Product, Batch, Purchase, Sale, SaleItem, Prescription, PrescriptionItem

    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Seeding Customers...")
        customers_data = [
            {"name": "John Smith", "phone": "+1-555-0101",
                "address": "123 Main St, New York, NY 10001", "age": 45, "gender": "Male"},
            {"name": "Emma Johnson", "phone": "+1-555-0102",
                "address": "456 Oak Ave, Los Angeles, CA 90001", "age": 32, "gender": "Female"},
            {"name": "Michael Brown", "phone": "+1-555-0103",
                "address": "789 Pine Rd, Chicago, IL 60601", "age": 58, "gender": "Male"},
            {"name": "Sarah Davis", "phone": "+1-555-0104",
                "address": "321 Elm St, Houston, TX 77001", "age": 41, "gender": "Female"},
            {"name": "Robert Wilson", "phone": "+1-555-0105",
                "address": "654 Maple Dr, Phoenix, AZ 85001", "age": 67, "gender": "Male"},
            {"name": "Lisa Anderson", "phone": "+1-555-0106",
                "address": "987 Cedar Ln, Philadelphia, PA 19101", "age": 29, "gender": "Female"},
            {"name": "David Martinez", "phone": "+1-555-0107",
                "address": "147 Birch Ct, San Antonio, TX 78201", "age": 52, "gender": "Male"},
            {"name": "Jennifer Taylor", "phone": "+1-555-0108",
                "address": "258 Spruce Way, San Diego, CA 92101", "age": 38, "gender": "Female"},
        ]

        customers = []
        for data in customers_data:
            customer = Customer(**data)
            db.session.add(customer)
            customers.append(customer)
        db.session.commit()
        print(f"Added {len(customers)} customers")

        print("Seeding Employees...")
        employees_data = [
            {"name": "Dr. Alice Cooper", "salary": 75000.00,
                "work_shift": "Morning", "role": "Pharmacist", "experience": 10},
            {"name": "Bob Williams", "salary": 45000.00, "work_shift": "Evening",
                "role": "Assistant Pharmacist", "experience": 5},
            {"name": "Carol Martinez", "salary": 55000.00,
                "work_shift": "Full Day", "role": "Store Manager", "experience": 8},
            {"name": "Daniel Lee", "salary": 35000.00, "work_shift": "Morning",
                "role": "Sales Associate", "experience": 3},
            {"name": "Eva Rodriguez", "salary": 38000.00, "work_shift": "Evening",
                "role": "Inventory Clerk", "experience": 4},
        ]

        employees = []
        for data in employees_data:
            employee = Employee(**data)
            db.session.add(employee)
            employees.append(employee)
        db.session.commit()
        print(f"Added {len(employees)} employees")

        print("Seeding Suppliers...")
        suppliers_data = [
            {
                "firm_name": "MediSupply Inc.", "owner_name": "James Wilson",
                "gst_no": "GST001234567", "phone": "+1-555-1001",
                "address": "100 Medical Plaza, Boston, MA 02101",
                "drug_license": "DL-MA-001234", "ifsc": "ABCD0123456",
                "bank_acc_no": "1234567890123456"
            },
            {
                "firm_name": "PharmaDistributors LLC", "owner_name": "Mary Johnson",
                "gst_no": "GST007654321", "phone": "+1-555-1002",
                "address": "200 Healthcare Blvd, Seattle, WA 98101",
                "drug_license": "DL-WA-007654", "ifsc": "EFGH0654321",
                "bank_acc_no": "6543210987654321"
            },
            {
                "firm_name": "HealthCare Solutions", "owner_name": "Robert Chen",
                "gst_no": "GST009876543", "phone": "+1-555-1003",
                "address": "300 Wellness Way, Miami, FL 33101",
                "drug_license": "DL-FL-009876", "ifsc": "IJKL0987654",
                "bank_acc_no": "9876543210123456"
            },
        ]

        suppliers = []
        for data in suppliers_data:
            supplier = Supplier(**data)
            db.session.add(supplier)
            suppliers.append(supplier)
        db.session.commit()
        print(f"Added {len(suppliers)} suppliers")

        print("Seeding Products...")
        products_data = [
            {"brand_name": "Tylenol", "medicine_name": "Paracetamol", "form": "Tablet", "strength": "500mg",
                "packing": "Strip of 10", "prescription_type": "OTC", "mrp": 8.99, "unit_price": 7.50},
            {"brand_name": "Advil", "medicine_name": "Ibuprofen", "form": "Tablet", "strength": "200mg",
                "packing": "Bottle of 50", "prescription_type": "OTC", "mrp": 12.99, "unit_price": 10.50},
            {"brand_name": "Amoxil", "medicine_name": "Amoxicillin", "form": "Capsule", "strength": "250mg",
                "packing": "Strip of 15", "prescription_type": "Prescription", "mrp": 15.99, "unit_price": 13.00},
            {"brand_name": "Zithromax", "medicine_name": "Azithromycin", "form": "Tablet", "strength": "500mg",
                "packing": "Pack of 6", "prescription_type": "Prescription", "mrp": 25.99, "unit_price": 22.00},
            {"brand_name": "Ventolin", "medicine_name": "Albuterol", "form": "Inhaler", "strength": "100mcg",
                "packing": "1 Inhaler", "prescription_type": "Prescription", "mrp": 45.99, "unit_price": 40.00},
            {"brand_name": "Benadryl", "medicine_name": "Diphenhydramine", "form": "Syrup", "strength": "12.5mg/5ml",
                "packing": "Bottle of 120ml", "prescription_type": "OTC", "mrp": 9.99, "unit_price": 8.00},
            {"brand_name": "Lipitor", "medicine_name": "Atorvastatin", "form": "Tablet", "strength": "10mg",
                "packing": "Strip of 10", "prescription_type": "Prescription", "mrp": 35.99, "unit_price": 30.00},
            {"brand_name": "Nexium", "medicine_name": "Esomeprazole", "form": "Capsule", "strength": "40mg",
                "packing": "Strip of 14", "prescription_type": "Prescription", "mrp": 28.99, "unit_price": 25.00},
            {"brand_name": "Aspirin", "medicine_name": "Acetylsalicylic Acid", "form": "Tablet", "strength": "75mg",
                "packing": "Bottle of 30", "prescription_type": "OTC", "mrp": 6.99, "unit_price": 5.50},
            {"brand_name": "Vitamin D3", "medicine_name": "Cholecalciferol", "form": "Capsule", "strength": "1000IU",
                "packing": "Bottle of 60", "prescription_type": "OTC", "mrp": 14.99, "unit_price": 12.00},
        ]

        products = []
        for data in products_data:
            product = Product(**data)
            db.session.add(product)
            products.append(product)
        db.session.commit()
        print(f"Added {len(products)} products")

        print("Seeding Batches...")
        batches = []
        for product in products:
            # Create 2-3 batches per product
            for i in range(random.randint(2, 3)):
                supplier = random.choice(suppliers)
                manufacture_date = date.today() - timedelta(days=random.randint(30, 365))
                expiry_date = manufacture_date + \
                    timedelta(days=random.randint(365, 1095))

                batch = Batch(
                    p_id=product.p_id,
                    s_id=supplier.s_id,
                    batch_no=f"BATCH-{product.p_id:03d}-{i+1:02d}",
                    manufacture_date=manufacture_date,
                    expiry_date=expiry_date,
                    cost_price=product.unit_price * 0.8,
                    qty_received=random.randint(100, 500),
                    qty_available=random.randint(50, 300),
                    received_on=manufacture_date + timedelta(days=7),
                    manufacture_name=supplier.firm_name,
                    marketer_name=supplier.firm_name
                )
                db.session.add(batch)
                batches.append(batch)
        db.session.commit()
        print(f"Added {len(batches)} batches")

        print("Seeding Purchases...")
        purchases = []
        for batch in batches[:15]:  # Create purchases for first 15 batches
            purchase = Purchase(
                b_id=batch.b_id,
                s_id=batch.s_id,
                p_id=batch.p_id,
                date=batch.received_on,
                cost=batch.cost_price * batch.qty_received,
                status="Completed"
            )
            db.session.add(purchase)
            purchases.append(purchase)
        db.session.commit()
        print(f"Added {len(purchases)} purchases")

        print("Seeding Prescriptions...")
        prescriptions = []
        for customer in customers[:5]:  # First 5 customers have prescriptions
            for i in range(random.randint(1, 3)):
                prescription = Prescription(
                    c_id=customer.c_id,
                    dr_id=f"DR{random.randint(1000, 9999)}",
                    doctor_license_no=f"LIC-{random.randint(100000, 999999)}",
                    date=date.today() - timedelta(days=random.randint(1, 60)),
                    validity=date.today() + timedelta(days=random.randint(30, 90)),
                    hospital_name=random.choice(
                        ["City Hospital", "General Medical Center", "Community Health Clinic"])
                )
                db.session.add(prescription)
                db.session.flush()

                # Add prescription items
                num_items = random.randint(1, 4)
                selected_products = random.sample([p for p in products if p.prescription_type == "Prescription"],
                                                  min(num_items, len([p for p in products if p.prescription_type == "Prescription"])))

                for line_no, product in enumerate(selected_products, 1):
                    item = PrescriptionItem(
                        pres_id=prescription.pres_id,
                        line_no=line_no,
                        product_id=product.p_id,
                        dosage=random.choice(
                            ["1 tablet twice daily", "2 tablets once daily", "1 capsule three times daily"]),
                        duration=random.choice(
                            ["7 days", "14 days", "30 days"]),
                        qty=random.randint(7, 30),
                        instructions=random.choice(
                            ["Take after meals", "Take before meals", "Take with water", "Take at bedtime"])
                    )
                    db.session.add(item)

                prescriptions.append(prescription)
        db.session.commit()
        print(f"Added {len(prescriptions)} prescriptions")

        print("Seeding Sales...")
        sales = []
        for i in range(20):  # Create 20 sales
            customer = random.choice(customers)
            employee = random.choice(employees)
            prescription = random.choice(
                prescriptions) if prescriptions and random.random() > 0.5 else None

            sale = Sale(
                c_id=customer.c_id,
                e_id=employee.e_id,
                pres_id=prescription.pres_id if prescription else None,
                sale_date=date.today() - timedelta(days=random.randint(1, 90)),
                payment_mode=random.choice(["Cash", "Card", "UPI"]),
                amount=0,  # Will be calculated
                tax=0,  # Will be calculated
                discount=0,
                total=0,  # Will be calculated
                status="Completed"
            )
            db.session.add(sale)
            db.session.flush()

            # Add sale items
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, num_items)
            total_amount = 0

            for line_no, product in enumerate(selected_products, 1):
                # Find a batch with available quantity
                available_batches = [
                    b for b in batches if b.p_id == product.p_id and b.qty_available > 0]
                if not available_batches:
                    continue

                batch = random.choice(available_batches)
                qty = min(random.randint(1, 5), batch.qty_available)
                price = product.unit_price
                line_total = qty * price

                sale_item = SaleItem(
                    sale_id=sale.sb_id,
                    line_no=line_no,
                    p_id=product.p_id,
                    b_id=batch.b_id,
                    qty=qty,
                    price=price,
                    line_total=line_total,
                    line_discount=0
                )
                db.session.add(sale_item)
                total_amount += line_total

                # Update batch quantity
                batch.qty_available -= qty

            # Update sale totals
            sale.amount = total_amount
            sale.tax = total_amount * 0.08  # 8% tax
            sale.total = sale.amount + sale.tax - sale.discount

            sales.append(sale)

        db.session.commit()
        print(f"Added {len(sales)} sales")

        print("\n" + "="*50)
        print("Database seeded successfully!")
        print("="*50)
        print(f"Customers: {len(customers)}")
        print(f"Employees: {len(employees)}")
        print(f"Suppliers: {len(suppliers)}")
        print(f"Products: {len(products)}")
        print(f"Batches: {len(batches)}")
        print(f"Purchases: {len(purchases)}")
        print(f"Prescriptions: {len(prescriptions)}")
        print(f"Sales: {len(sales)}")
        print("="*50)
        print("\nLogin credentials:")
        print("Admin - Username: admin, Password: admin123")
        print(f"Customer - Use any Customer ID from 1 to {len(customers)}")
        print("="*50)


if __name__ == '__main__':
    seed_database()
