from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import db
from models import Customer, Employee, Product, Sale, Supplier, Batch, SaleItem
from datetime import datetime, timedelta

admin_routes = Blueprint('admin', __name__)

@admin_routes.before_request
def require_admin():
    if session.get('user_type') != 'admin':
        return redirect(url_for('auth.admin_login')) # Redirect to login if not admin

@admin_routes.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html',
                           Product=Product,
                           Customer=Customer,
                           Employee=Employee,
                           Sale=Sale)

# Employee Management
@admin_routes.route('/admin/employees')
def admin_employees():
    employees = Employee.query.all()
    return render_template('admin_employees.html', employees=employees)

@admin_routes.route('/admin/employees/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        try:
            # TODO: Add username/password handling in form
            employee = Employee(
                name=request.form['name'],
                salary=float(request.form['salary']),
                work_shift=request.form['work_shift'],
                role=request.form['role'],
                experience=int(request.form['experience'])
            )
            db.session.add(employee)
            db.session.commit()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('admin.admin_employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')

    return render_template('add_employee.html')

@admin_routes.route('/admin/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        try:
            employee.name = request.form['name']
            employee.salary = float(request.form['salary'])
            employee.work_shift = request.form['work_shift']
            employee.role = request.form['role']
            employee.experience = int(request.form['experience'])

            db.session.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('admin.admin_employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'error')

    return render_template('edit_employee.html', employee=employee)

@admin_routes.route('/admin/employees/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'error')

    return redirect(url_for('admin.admin_employees'))

# Product Management
@admin_routes.route('/admin/products')
def admin_products():
    products = Product.query.all()
    return render_template('admin_products.html', products=products)

@admin_routes.route('/admin/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            product = Product(
                brand_name=request.form['brand_name'],
                medicine_name=request.form['medicine_name'],
                form=request.form['form'],
                strength=request.form['strength'],
                packing=request.form['packing'],
                prescription_type=request.form['prescription_type'],
                mrp=float(request.form['mrp']),
                unit_price=float(request.form['unit_price'])
            )
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin.admin_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'error')

    return render_template('add_product.html')

@admin_routes.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        try:
            product.brand_name = request.form['brand_name']
            product.medicine_name = request.form['medicine_name']
            product.form = request.form['form']
            product.strength = request.form['strength']
            product.packing = request.form['packing']
            product.prescription_type = request.form['prescription_type']
            product.mrp = float(request.form['mrp'])
            product.unit_price = float(request.form['unit_price'])

            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin.admin_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'error')

    return render_template('edit_product.html', product=product)

@admin_routes.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')

    return redirect(url_for('admin.admin_products'))

# Customer Management
@admin_routes.route('/admin/customers')
def admin_customers():
    customers = Customer.query.all()
    return render_template('admin_customers.html', customers=customers)

@admin_routes.route('/admin/customers/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        try:
            customer = Customer(
                name=request.form['name'],
                phone=request.form['phone'],
                address=request.form['address'],
                age=int(request.form['age']),
                gender=request.form['gender']
            )
            db.session.add(customer)
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('admin.admin_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding customer: {str(e)}', 'error')

    return render_template('add_customer.html')

# Sales
@admin_routes.route('/admin/sales')
def admin_sales():
    # Group sales by product with supplier information
    sales_data = db.session.query(
        Product.brand_name,
        Product.medicine_name,
        Supplier.firm_name,
        db.func.sum(SaleItem.qty).label('total_qty'),
        db.func.sum(SaleItem.line_total).label('total_sales')
    ).join(
        SaleItem, Product.p_id == SaleItem.p_id
    ).join(
        Batch, SaleItem.b_id == Batch.b_id
    ).join(
        Supplier, Batch.s_id == Supplier.s_id
    ).group_by(
        Product.p_id, Supplier.s_id
    ).all()

    return render_template('admin_sales.html', sales_data=sales_data)

# Reports
@admin_routes.route('/admin/reports')
def admin_reports():
    # Current stock summary
    stock_data = db.session.query(
        Product.brand_name,
        Product.medicine_name,
        db.func.sum(Batch.qty_available).label('total_stock'),
        db.func.min(Batch.expiry_date).label('nearest_expiry')
    ).join(
        Batch, Product.p_id == Batch.p_id
    ).group_by(Product.p_id).all()

    # Near expiry items (within 30 days)
    near_expiry_date = datetime.now().date() + timedelta(days=30)
    near_expiry = db.session.query(
        Product.brand_name,
        Product.medicine_name,
        Batch.batch_no,
        Batch.expiry_date,
        Batch.qty_available
    ).join(
        Batch, Product.p_id == Batch.p_id
    ).filter(
        Batch.expiry_date <= near_expiry_date,
        Batch.qty_available > 0
    ).all()

    # Top selling medicines
    top_selling = db.session.query(
        Product.brand_name,
        Product.medicine_name,
        db.func.sum(SaleItem.qty).label('total_sold')
    ).join(
        SaleItem, Product.p_id == SaleItem.p_id
    ).group_by(Product.p_id).order_by(
        db.func.sum(SaleItem.qty).desc()
    ).limit(10).all()

    return render_template('admin_reports.html',
                           stock_data=stock_data,
                           near_expiry=near_expiry,
                           top_selling=top_selling)
