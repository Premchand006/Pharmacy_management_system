from datetime import date, timedelta
from decimal import Decimal

import pytest

from pharmacy.billing import (BillingError, SaleRequest, create_sale, financial_year, split_tax,
                              void_sale)
from pharmacy.extensions import db
from pharmacy.models import Batch, Employee, PharmacySettings, Product, local_today


def test_financial_year_turns_over_in_april():
    assert financial_year(date(2026, 3, 31)) == "2025-26"
    assert financial_year(date(2026, 4, 1)) == "2026-27"
    assert financial_year(date(2027, 1, 15)) == "2026-27"


def test_split_tax_backs_gst_out_of_mrp():
    taxable, cgst, sgst = split_tax(Decimal("105.00"), Decimal("5"))
    assert (taxable, cgst, sgst) == (Decimal("100.00"), Decimal("2.50"), Decimal("2.50"))
    taxable, cgst, sgst = split_tax(Decimal("33.50"), Decimal("5"))
    assert taxable + cgst + sgst == Decimal("33.50")


def test_split_tax_composition_and_exempt():
    assert split_tax(Decimal("50"), Decimal("5"), composition=True) == (Decimal("50.00"), 0, 0)
    assert split_tax(Decimal("50"), Decimal("0")) == (Decimal("50.00"), 0, 0)


def _otc(app):
    return Product.query.filter_by(schedule="OTC").order_by(Product.p_id).first()


def _staff(username):
    return Employee.query.filter_by(username=username).one()


def test_sale_uses_earliest_expiry_and_skips_expired(app):
    with app.app_context():
        product = _otc(app)
        today = local_today()
        Batch.query.filter_by(p_id=product.p_id).delete()
        sup_id = 1
        expired = Batch(p_id=product.p_id, s_id=sup_id, batch_no="OLD", expiry_date=today - timedelta(days=1),
                        cost_price=1, mrp=10, qty_received=5, qty_available=5)
        soon = Batch(p_id=product.p_id, s_id=sup_id, batch_no="SOON", expiry_date=today + timedelta(days=10),
                     cost_price=1, mrp=10, qty_received=2, qty_available=2)
        later = Batch(p_id=product.p_id, s_id=sup_id, batch_no="LATER", expiry_date=today + timedelta(days=300),
                      cost_price=1, mrp=12, qty_received=10, qty_available=10)
        db.session.add_all([expired, soon, later])
        db.session.flush()
        sale = create_sale(SaleRequest(lines=[(product.p_id, 3)], billed_by=_staff("ravi")))
        assert [(i.batch.batch_no, i.qty) for i in sale.items] == [("SOON", 2), ("LATER", 1)]
        assert expired.qty_available == 5
        assert sale.gross_total == Decimal("32.00")
        assert sale.total == Decimal("32")

        with pytest.raises(BillingError, match="Only 9"):
            create_sale(SaleRequest(lines=[(product.p_id, 10)], billed_by=_staff("ravi")))


def test_invoice_numbers_run_per_financial_year(app):
    with app.app_context():
        product = _otc(app)
        a = create_sale(SaleRequest(lines=[(product.p_id, 1)], billed_by=_staff("ravi")))
        b = create_sale(SaleRequest(lines=[(product.p_id, 1)], billed_by=_staff("ravi")))
        assert b.seq == a.seq + 1
        prefix = PharmacySettings.get().invoice_prefix
        assert b.invoice_no == f"{prefix}/{financial_year(local_today())}/{b.seq:05d}"


def test_prescription_drug_needs_details_and_pharmacist(app):
    with app.app_context():
        h1 = Product.query.filter_by(schedule="H1").first()
        req = SaleRequest(lines=[(h1.p_id, 1)], billed_by=_staff("ravi"))
        with pytest.raises(BillingError, match="need a prescription"):
            create_sale(req)

        details = dict(patient_name="A Patient", patient_address="1 Road", prescriber_name="Dr B",
                       prescriber_reg_no="REG1", prescriber_address="Clinic")
        with pytest.raises(BillingError, match="registered pharmacist"):
            create_sale(SaleRequest(lines=[(h1.p_id, 1)], billed_by=_staff("ravi"), **details))

        sale = create_sale(SaleRequest(lines=[(h1.p_id, 1)], billed_by=_staff("ravi"),
                                       pharmacist=_staff("meera"), **details))
        assert sale.pharmacist.username == "meera"
        assert sale.items[0].schedule == "H1"


def test_schedule_x_needs_form_20f(app):
    with app.app_context():
        product = Product.query.filter_by(schedule="OTC").first()
        product.schedule = "X"
        details = dict(patient_name="P", patient_address="A", prescriber_name="D", prescriber_reg_no="R",
                       prescriber_address="C")
        with pytest.raises(BillingError, match="20F"):
            create_sale(SaleRequest(lines=[(product.p_id, 1)], billed_by=_staff("meera"), **details))


def test_prescription_cannot_be_dispensed_past_its_repeats(app):
    from pharmacy.models import Prescription
    with app.app_context():
        pres = Prescription.query.filter_by(repeats_allowed=0).filter(Prescription.sales.any()).first()
        assert pres is not None
        with pytest.raises(BillingError, match="already been dispensed"):
            create_sale(SaleRequest(lines=[(i.p_id, i.qty) for i in pres.items], billed_by=_staff("meera"),
                                    prescription=pres))


def test_void_returns_stock_and_keeps_invoice(app):
    with app.app_context():
        product = _otc(app)
        sale = create_sale(SaleRequest(lines=[(product.p_id, 2)], billed_by=_staff("ravi")))
        batch = sale.items[0].batch
        before = batch.qty_available
        with pytest.raises(BillingError):
            void_sale(sale, "   ", _staff("admin"))
        void_sale(sale, "Customer changed mind", _staff("admin"))
        assert sale.status == "void"
        assert batch.qty_available == before + 2
        with pytest.raises(BillingError, match="already void"):
            void_sale(sale, "again", _staff("admin"))


def test_discount_limits(app):
    with app.app_context():
        product = _otc(app)
        with pytest.raises(BillingError):
            create_sale(SaleRequest(lines=[(product.p_id, 1)], billed_by=_staff("ravi"),
                                    discount_pct=Decimal("150")))
        sale = create_sale(SaleRequest(lines=[(product.p_id, 2)], billed_by=_staff("ravi"),
                                       discount_pct=Decimal("10")))
        assert sale.discount_total == (sale.gross_total * Decimal("0.10")).quantize(Decimal("0.01"))
