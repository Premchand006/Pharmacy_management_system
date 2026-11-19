import json

import pytest

from pharmacy.extensions import db
from pharmacy.models import AuditLog, Customer, Prescription, Product, Sale

from .conftest import csrf_token, login_customer, login_staff

STAFF_PAGES = [
    "/staff/", "/staff/products", "/staff/products/new", "/staff/products/1", "/staff/customers",
    "/staff/customers/new", "/staff/customers/1", "/staff/suppliers", "/staff/suppliers/new",
    "/staff/prescriptions", "/staff/prescriptions/1", "/staff/stock/", "/staff/stock/?show=expired",
    "/staff/stock/?show=expiring", "/staff/stock/purchases", "/staff/stock/purchases/1",
    "/staff/stock/purchases/new", "/staff/stock/reorder", "/staff/sales/", "/staff/sales/new",
    "/staff/sales/new?pres_id=4", "/staff/sales/1", "/staff/reports/", "/staff/reports/trace",
    "/staff/reports/register", "/staff/reports/register?schedule=ALL", "/staff/reports/schedule-x",
    "/staff/reports/purchases", "/staff/reports/gst", "/account/password",
]
ADMIN_PAGES = ["/staff/employees", "/staff/employees/new", "/staff/employees/2", "/staff/settings",
               "/staff/reports/audit"]


def test_public_pages(client):
    for path in ["/", "/privacy", "/login", "/portal/login", "/healthz", "/robots.txt"]:
        assert client.get(path).status_code == 200, path
    assert client.get("/nope").status_code == 404


def test_security_headers(client):
    r = client.get("/")
    assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]
    assert "'unsafe-inline'" not in r.headers["Content-Security-Policy"].split("script-src")[1].split(";")[0]
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["Cache-Control"] == "no-store"


def test_staff_pages_require_login(client):
    r = client.get("/staff/products")
    assert r.status_code == 302 and "/login" in r.location


def test_every_staff_page_renders(client):
    assert login_staff(client).status_code == 302
    for path in STAFF_PAGES + ADMIN_PAGES:
        assert client.get(path).status_code == 200, path


def test_csv_exports(client):
    login_staff(client)
    for path in ["/staff/reports/?format=csv", "/staff/reports/register?format=csv&schedule=ALL",
                 "/staff/reports/purchases?format=csv", "/staff/reports/gst?export=hsn",
                 "/staff/reports/gst?export=b2cs", "/staff/reports/gst?export=b2b"]:
        r = client.get(path)
        assert r.status_code == 200 and r.mimetype == "text/csv", path


def test_counter_staff_cannot_open_admin_pages(client):
    login_staff(client, "ravi", "staff-demo-2026")
    assert client.get("/staff/").status_code == 200
    for path in ADMIN_PAGES:
        assert client.get(path).status_code == 403, path


def test_bad_password_and_lockout(client):
    token = csrf_token(client, "/login")
    for _ in range(5):
        r = client.post("/login", data={"username": "admin", "password": "wrong", "csrf_token": token})
        assert r.status_code == 401
    r = client.post("/login", data={"username": "admin", "password": "admin-demo-2026", "csrf_token": token})
    assert r.status_code == 429


def test_post_without_csrf_is_rejected(client):
    r = client.post("/login", data={"username": "admin", "password": "admin-demo-2026"})
    assert r.status_code == 400


def test_logout_is_post_only_and_ends_session(client):
    login_staff(client)
    assert client.get("/logout").status_code == 405
    token = csrf_token(client, "/staff/")
    client.post("/logout", data={"csrf_token": token})
    assert client.get("/staff/").status_code == 302


def test_deactivated_staff_are_signed_out(app, client):
    login_staff(client, "ravi", "staff-demo-2026")
    with app.app_context():
        from pharmacy.models import Employee
        emp = Employee.query.filter_by(username="ravi").one()
        emp.is_active = False
        db.session.commit()
    assert client.get("/staff/").status_code == 302


def test_checkout_through_the_counter(app, client):
    login_staff(client, "ravi", "staff-demo-2026")
    with app.app_context():
        otc = Product.query.filter_by(schedule="OTC").first()
        before = Sale.query.count()
    token = csrf_token(client, "/staff/sales/new")
    r = client.post("/staff/sales/new", data={"csrf_token": token, "item_id[]": [str(otc.p_id)],
                                              "item_qty[]": ["2"], "payment_mode": "UPI", "discount_pct": "0"})
    assert r.status_code == 302 and "print=1" in r.location
    assert client.get(r.location).status_code == 200
    with app.app_context():
        assert Sale.query.count() == before + 1


def test_counter_keeps_cart_on_error(app, client):
    login_staff(client, "ravi", "staff-demo-2026")
    with app.app_context():
        h1 = Product.query.filter_by(schedule="H1").first()
    token = csrf_token(client, "/staff/sales/new")
    r = client.post("/staff/sales/new", data={"csrf_token": token, "item_id[]": [str(h1.p_id)],
                                              "item_qty[]": ["1"], "payment_mode": "Cash"})
    assert r.status_code == 422
    html = r.get_data(as_text=True)
    assert "need a prescription" in html
    assert h1.brand_name in html  # cart restored from data-cart


def test_product_search_json(client):
    login_staff(client)
    data = json.loads(client.get("/staff/sales/products.json?q=fev").data)
    assert data and data[0]["label"].startswith("Feverex")


def test_audit_log_records_changes_without_customer_pii(app, client):
    login_staff(client)
    token = csrf_token(client, "/staff/customers/1")
    client.post("/staff/customers/1", data={"csrf_token": token, "name": "Renamed Person", "phone": "999"})
    with app.app_context():
        entry = AuditLog.query.filter_by(entity="Customer", action="update").order_by(AuditLog.id.desc()).first()
        assert entry is not None
        assert "Renamed Person" not in entry.changes and "(changed)" in entry.changes


def test_erasing_a_customer_keeps_sale_records(app, client):
    login_staff(client)
    with app.app_context():
        sale = Sale.query.filter(Sale.c_id.isnot(None), Sale.patient_name != "").first()
        cid, name = sale.c_id, sale.patient_name
    token = csrf_token(client, "/staff/customers")
    client.post(f"/staff/customers/{cid}/anonymise", data={"csrf_token": token})
    with app.app_context():
        cust = db.session.get(Customer, cid)
        assert cust.name.startswith("Erased") and not cust.phone and not cust.is_active
        assert db.session.get(Sale, sale.sb_id).patient_name == name


def test_customer_portal_is_scoped_to_the_customer(app, client):
    assert login_customer(client, 1).status_code == 302
    assert client.get("/portal/").status_code == 200
    with app.app_context():
        mine = Prescription.query.filter_by(c_id=1).first()
        other = Prescription.query.filter(Prescription.c_id != 1).first()
        other_sale = Sale.query.filter(Sale.c_id.isnot(None), Sale.c_id != 1).first()
    assert client.get(f"/portal/prescriptions/{mine.pres_id}").status_code == 200
    assert client.get(f"/portal/prescriptions/{other.pres_id}").status_code == 404
    assert client.get(f"/portal/purchases/{other_sale.sb_id}").status_code == 404
    assert client.get("/staff/").status_code == 302
    assert client.get("/portal/prescriptions/new").status_code == 200


def test_customer_can_send_a_prescription(app, client):
    login_customer(client, 2)
    token = csrf_token(client, "/portal/prescriptions/new")
    r = client.post("/portal/prescriptions/new", data={
        "csrf_token": token, "doctor_name": "Dr Test", "doctor_reg_no": "R-1", "doctor_address": "Clinic",
        "date": "2026-01-02", "p_id[]": ["1"], "qty[]": ["2"], "dosage[]": ["1-0-1"], "duration[]": ["3 days"],
        "instructions[]": [""]})
    assert r.status_code == 302


def test_password_change_signs_out_other_sessions(app):
    a, b = app.test_client(), app.test_client()
    login_staff(a, "meera", "staff-demo-2026")
    login_staff(b, "meera", "staff-demo-2026")
    token = csrf_token(a, "/account/password")
    r = a.post("/account/password", data={"csrf_token": token, "current": "staff-demo-2026",
                                          "new": "a much longer passphrase", "confirm": "a much longer passphrase"})
    assert r.status_code == 302
    assert a.get("/staff/").status_code == 200
    assert b.get("/staff/").status_code == 302


@pytest.mark.parametrize("bad", ["short", "aaaaaaaaaaaaaaaa"])
def test_weak_passwords_rejected(bad):
    from pharmacy.auth import password_problem
    assert password_problem(bad)
