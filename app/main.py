from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models, schemas, crud
from backend.database import engine, get_db
from . import queries
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pharmacy Management")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# --- Authentication & Entry pages
@app.get("/auth", response_class=HTMLResponse)
def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/signin/customer", response_class=HTMLResponse)
def signin_customer_page(request: Request):
    return templates.TemplateResponse("signin_customer.html", {"request": request})


@app.get("/signin/admin", response_class=HTMLResponse)
def signin_admin_page(request: Request):
    return templates.TemplateResponse("signin_admin.html", {"request": request})


@app.post("/signin/customer")
def signin_customer(c_id: int = Form(...)):
    return RedirectResponse(url=f"/customer/dashboard?c_id={c_id}", status_code=303)


@app.post("/signin/admin")
def signin_admin(s_id: int = Form(...), e_id: int = Form(None)):
    # allow either supplier id or employee id to access admin dashboard
    if e_id:
        return RedirectResponse(url=f"/admin/dashboard?e_id={e_id}", status_code=303)
    return RedirectResponse(url=f"/admin/dashboard?s_id={s_id}", status_code=303)


# --- Customer dashboard
@app.get("/customer/dashboard", response_class=HTMLResponse)
def customer_dashboard(request: Request, c_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, c_id)
    prescriptions = crud.list_prescriptions_by_customer(db, c_id)
    return templates.TemplateResponse("customer_dashboard.html", {"request": request, "customer": customer, "prescriptions": prescriptions})


# --- Admin dashboard
@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, s_id: int = None, e_id: int = None, db: Session = Depends(get_db)):
    suppliers = crud.list_suppliers(db)
    employees = crud.list_employees(db)
    products = crud.list_products(db)
    customers = crud.list_customers(db)
    sales = crud.list_sales(db)
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "suppliers": suppliers, "employees": employees, "products": products, "customers": customers, "sales": sales})


# Supplier create
@app.post("/suppliers/add")
def suppliers_add(firm_name: str = Form(...), owner_name: str = Form(None), phone: str = Form(None), address: str = Form(None), db: Session = Depends(get_db)):
    sup = schemas.SupplierCreate(firm_name=firm_name, owner_name=owner_name, phone=phone, address=address)
    crud.create_supplier(db, sup)
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# Employees
@app.post("/employees/add")
def employees_add(name: str = Form(...), salary: float = Form(None), work_shift: str = Form(None), role: str = Form(None), experience: int = Form(None), db: Session = Depends(get_db)):
    emp = schemas.EmployeeCreate(name=name, salary=salary, work_shift=work_shift, role=role, experience=experience)
    crud.create_employee(db, emp)
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# Sale detail view
@app.get("/sales/{sb_id}", response_class=HTMLResponse)
def sale_detail(request: Request, sb_id: int, db: Session = Depends(get_db)):
    sale = crud.get_sale(db, sb_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    items = crud.list_sale_items(db, sb_id)
    return templates.TemplateResponse("sale_detail.html", {"request": request, "sale": sale, "items": items})


# Customer prescriptions (existing route kept)
@app.get("/customer/{c_id}/prescriptions", response_class=HTMLResponse)
def customer_prescriptions(request: Request, c_id: int, db: Session = Depends(get_db)):
    prescriptions = crud.list_prescriptions_by_customer(db, c_id)
    return templates.TemplateResponse("prescriptions.html", {"request": request, "prescriptions": prescriptions})


# -- Customer endpoints (HTML forms + JSON API)
@app.get("/customers/", response_class=HTMLResponse)
def customers_page(request: Request, db: Session = Depends(get_db)):
    customers = crud.list_customers(db)
    return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})


@app.post("/customers/add")
def customers_add(name: str = Form(...), phone: str = Form(None), address: str = Form(None), db: Session = Depends(get_db)):
    cust = schemas.CustomerCreate(name=name, phone=phone, address=address)
    crud.create_customer(db, cust)
    return RedirectResponse(url="/customers/", status_code=303)


@app.post("/api/customers/", response_model=schemas.Customer)
def api_create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, customer)


# -- Product endpoints
@app.get("/products/", response_class=HTMLResponse)
def products_page(request: Request, db: Session = Depends(get_db)):
    products = crud.list_products(db)
    return templates.TemplateResponse("products.html", {"request": request, "products": products})


@app.post("/products/add")
def products_add(name: str = Form(...), brand: str = Form(None), price: float = Form(0.0), db: Session = Depends(get_db)):
    prod = schemas.ProductCreate(brand_name=brand, medicine_name=name, unit_price=price)
    crud.create_product(db, prod)
    return RedirectResponse(url="/products/", status_code=303)


@app.post("/api/products/", response_model=schemas.Product)
def api_create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, product)


# -- Batches page
@app.get("/batches/", response_class=HTMLResponse)
def batches_page(request: Request, db: Session = Depends(get_db)):
    batches = crud.list_batches(db)
    return templates.TemplateResponse("batches.html", {"request": request, "batches": batches})


@app.post("/batches/add")
def batches_add(p_id: int = Form(...), s_id: int = Form(None), batch_no: str = Form(None), manufacture_date: str = Form(None), expiry_date: str = Form(None), cost_price: float = Form(None), qty_received: int = Form(None), received_on: str = Form(None), db: Session = Depends(get_db)):
    # basic date parsing happens in schemas
    b = schemas.BatchCreate(p_id=p_id, s_id=s_id, batch_no=batch_no, manufacture_date=manufacture_date or None, expiry_date=expiry_date or None, cost_price=cost_price, qty_received=qty_received, qty_available=qty_received, received_on=received_on or None)
    crud.create_batch(db, b)
    return RedirectResponse(url="/batches/", status_code=303)


# -- Prescriptions
@app.get("/prescriptions/", response_class=HTMLResponse)
def prescriptions_page(request: Request, db: Session = Depends(get_db)):
    prescriptions = crud.list_prescriptions(db)
    return templates.TemplateResponse("prescriptions.html", {"request": request, "prescriptions": prescriptions})


@app.get("/prescriptions/add", response_class=HTMLResponse)
def prescriptions_add_page(request: Request, db: Session = Depends(get_db)):
    customers = crud.list_customers(db)
    return templates.TemplateResponse("prescriptions_add.html", {"request": request, "customers": customers})


@app.post("/prescriptions/add")
def prescriptions_add(customer_id: int = Form(None), dr_id: str = Form(None), doctor_license_no: str = Form(None), date: str = Form(None), validity: int = Form(None), hospital_name: str = Form(None), db: Session = Depends(get_db)):
    pres = schemas.PrescriptionCreate(c_id=customer_id or None, dr_id=dr_id or None, doctor_license_no=doctor_license_no or None, date=date or None, validity=validity or None, hospital_name=hospital_name or None)
    crud.create_prescription(db, pres)
    return RedirectResponse(url="/prescriptions/", status_code=303)


# -- Sales and reports
@app.get("/sales/", response_class=HTMLResponse)
def sales_page(request: Request, db: Session = Depends(get_db)):
    sales = crud.list_sales(db)
    return templates.TemplateResponse("sales.html", {"request": request, "sales": sales})


@app.get("/sales/create", response_class=HTMLResponse)
def sales_create_page(request: Request, db: Session = Depends(get_db)):
    # Show customers, employees, available batches to build a sale
    customers = crud.list_customers(db)
    employees = crud.list_employees(db)
    batches = crud.list_batches(db)
    return templates.TemplateResponse("sales_create.html", {"request": request, "customers": customers, "employees": employees, "batches": batches})


@app.get("/reports/stock", response_class=HTMLResponse)
def report_stock(request: Request, db: Session = Depends(get_db)):
    rows = crud.report_stock_by_product(db)
    return templates.TemplateResponse("report_stock.html", {"request": request, "rows": rows})


@app.get("/reports/search_products", response_class=HTMLResponse)
def search_products_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    results = []
    if q:
        results = crud.search_products_by_name(db, q)
    return templates.TemplateResponse("search_products.html", {"request": request, "results": results, "q": q})


@app.get("/reports", response_class=HTMLResponse)
def reports_index(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})


@app.post("/reports/run")
def run_report(payload: dict):
    name = payload.get("query")
    params = payload.get("params", {}) or {}
    if name not in queries.NAMED_QUERIES:
        return JSONResponse(status_code=400, content={"error": "Unknown or disallowed query"})
    try:
        rows = queries.execute_named_query(name, params)
        return {"query": name, "rows": rows}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/sales/create")
def create_sale_endpoint(payload: dict, db: Session = Depends(get_db)):
    sale_data = payload.get("sale")
    items = payload.get("items", [])
    if not sale_data:
        return JSONResponse(status_code=400, content={"error": "Missing sale data"})
    if sale_data.get("sale_date"):
        try:
            sale_data["sale_date"] = datetime.fromisoformat(sale_data["sale_date"])
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid sale_date format"})
    try:
        # debug: show which engine/session bind is in use
        try:
            print('DEBUG create_sale_endpoint db.bind ->', getattr(db, 'bind', None))
        except Exception:
            pass
        with db.begin():
            sale = models.Sale(
                c_id=sale_data.get("c_id"),
                e_id=sale_data.get("e_id"),
                pres_id=sale_data.get("pres_id"),
                sale_date=sale_data.get("sale_date"),
                payment_mode=sale_data.get("payment_mode"),
                amount=sale_data.get("amount"),
                tax=sale_data.get("tax"),
                discount=sale_data.get("discount"),
                total=sale_data.get("total"),
                status=sale_data.get("status"),
            )
            db.add(sale)
            db.flush()
            for it in items:
                b_id = it.get("b_id")
                qty = int(it.get("qty") or 0)
                if qty <= 0:
                    return JSONResponse(status_code=400, content={"error": "Item quantity must be > 0"})
                batch = db.query(models.Batch).get(b_id)
                if not batch:
                    return JSONResponse(status_code=400, content={"error": f"Batch {b_id} not found"})
                if (batch.qty_available or 0) < qty:
                    return JSONResponse(status_code=400, content={"error": f"Insufficient stock in batch {b_id}"})
                sale_item = models.SaleItem(
                    sale_id=sale.sb_id,
                    line_no=it.get("line_no"),
                    p_id=it.get("p_id"),
                    b_id=b_id,
                    qty=qty,
                    price=it.get("price"),
                    line_total=it.get("line_total"),
                    line_discount=it.get("line_discount"),
                )
                db.add(sale_item)
                batch.qty_available = (batch.qty_available or 0) - qty
            db.refresh(sale)
            return sale
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

