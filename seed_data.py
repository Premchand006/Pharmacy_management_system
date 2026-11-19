"""Wipe the configured database and load the demo data.

    python seed_data.py
"""
from app import app
from pharmacy.extensions import db
from pharmacy.seed import (ADMIN_PASSWORD, CUSTOMER_PASSWORD, STAFF_PASSWORD, populate)

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate()
    print("Database reloaded with demo data.")
    print(f"Staff:     admin / {ADMIN_PASSWORD}   (admin, pharmacist)")
    print(f"           meera / {STAFF_PASSWORD}   (pharmacist)")
    print(f"           ravi  / {STAFF_PASSWORD}   (counter assistant)")
    print(f"Customers: ID 1-8 / {CUSTOMER_PASSWORD}")
