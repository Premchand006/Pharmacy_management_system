import re

import pytest

from pharmacy import auth, create_app
from pharmacy.extensions import db

# Cheap hashes keep the suite fast; production uses auth.HASH_METHOD.
auth.HASH_METHOD = "scrypt:1024:8:1"
auth._DUMMY_HASH = auth.generate_password_hash("x", method=auth.HASH_METHOD)


@pytest.fixture()
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        "SEED_DEMO_DATA": True,
        "SECRET_KEY": "test",
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf_token(client, path):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def login_staff(client, username="admin", password="admin-demo-2026"):
    token = csrf_token(client, "/login")
    return client.post("/login", data={"username": username, "password": password, "csrf_token": token})


def login_customer(client, cid=1, password="customer-demo-2026"):
    token = csrf_token(client, "/portal/login")
    return client.post("/portal/login", data={"customer_id": str(cid), "password": password, "csrf_token": token})
