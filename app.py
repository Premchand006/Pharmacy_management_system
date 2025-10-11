from models import create_models
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pharmacy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import and create models
models = create_models(db)

# Make models available globally
Customer = models['Customer']
Employee = models['Employee']
Supplier = models['Supplier']
Product = models['Product']
Batch = models['Batch']
Purchase = models['Purchase']
Sale = models['Sale']
SaleItem = models['SaleItem']
Prescription = models['Prescription']
PrescriptionItem = models['PrescriptionItem']

# Create tables
with app.app_context():
    db.create_all()

# Make date available in templates


@app.context_processor
def utility_processor():
    return dict(date=date)

# Landing page


@app.route('/')
def index():
    return render_template('index.html')

# Customer routes


@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        customer = Customer.query.filter_by(c_id=customer_id).first()

        if customer:
            session['user_type'] = 'customer'
            session['user_id'] = customer.c_id
            session['user_name'] = customer.name
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid Customer ID', 'error')
            return render_template('customer_login.html', error=True)

    return render_template('customer_login.html')


@app.route('/customer_dashboard')
def customer_dashboard():
    if session.get('user_type') != 'customer':
        return redirect(url_for('index'))
    return render_template('customer_dashboard.html')


@app.route('/customer_prescriptions')
def customer_prescriptions():
    if session.get('user_type') != 'customer':
        return redirect(url_for('index'))

    customer_id = session.get('user_id')
    prescriptions = Prescription.query.filter_by(c_id=customer_id).all()
    return render_template('customer_prescriptions.html', prescriptions=prescriptions)


@app.route('/prescription_items/<int:prescription_id>')
def prescription_items(prescription_id):
    if session.get('user_type') != 'customer':
        return redirect(url_for('index'))

    items = PrescriptionItem.query.filter_by(pres_id=prescription_id).all()
    prescription = Prescription.query.get(prescription_id)
    return render_template('prescription_items.html', items=items, prescription=prescription)


@app.route('/add_prescription', methods=['GET', 'POST'])
def add_prescription():
    if session.get('user_type') != 'customer':
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Create new prescription
            prescription = Prescription(
                c_id=session.get('user_id'),
                dr_id=request.form['dr_id'],
                doctor_license_no=request.form['doctor_license_no'],
                date=datetime.strptime(
                    request.form['date'], '%Y-%m-%d').date(),
                validity=datetime.strptime(
                    request.form['validity'], '%Y-%m-%d').date(),
                hospital_name=request.form['hospital_name']
            )

            db.session.add(prescription)
            db.session.flush()  # Get the prescription ID

            # Add prescription items
            product_ids = request.form.getlist('product_id[]')
            dosages = request.form.getlist('dosage[]')
            durations = request.form.getlist('duration[]')
            quantities = request.form.getlist('qty[]')
            instructions = request.form.getlist('instructions[]')

            for i, product_id in enumerate(product_ids):
                if product_id:  # Only add if product_id is provided
                    item = PrescriptionItem(
                        pres_id=prescription.pres_id,
                        line_no=i+1,
                        product_id=int(product_id),
                        dosage=dosages[i],
                        duration=durations[i],
                        qty=int(quantities[i]),
                        instructions=instructions[i]
                    )
                    db.session.add(item)

            db.session.commit()
            flash('Prescription added successfully!', 'success')
            return redirect(url_for('customer_prescriptions'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding prescription: {str(e)}', 'error')

    products = Product.query.all()
    return render_template('add_prescription.html', products=products)

# Admin routes


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Simple admin authentication (you can enhance this)
        if username == 'admin' and password == 'admin123':
            session['user_type'] = 'admin'
            session['user_name'] = 'Administrator'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
            return render_template('admin_login.html', error=True)

    return render_template('admin_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html',
                           Product=Product,
                           Customer=Customer,
                           Employee=Employee,
                           Sale=Sale)

# Employee management routes


@app.route('/admin/employees')
def admin_employees():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    employees = Employee.query.all()
    return render_template('admin_employees.html', employees=employees)


@app.route('/admin/employees/add', methods=['GET', 'POST'])
def add_employee():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
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
            return redirect(url_for('admin_employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')

    return render_template('add_employee.html')


@app.route('/admin/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))

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
            return redirect(url_for('admin_employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'error')

    return render_template('edit_employee.html', employee=employee)


@app.route('/admin/employees/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))

    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'error')

    return redirect(url_for('admin_employees'))

# Product management routes


@app.route('/admin/products')
def admin_products():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    products = Product.query.all()
    return render_template('admin_products.html', products=products)


@app.route('/admin/products/add', methods=['GET', 'POST'])
def add_product():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))

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
            return redirect(url_for('admin_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'error')

    return render_template('add_product.html')


@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))

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
            return redirect(url_for('admin_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'error')

    return render_template('edit_product.html', product=product)


@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))

    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')

    return redirect(url_for('admin_products'))

# Customer management routes


@app.route('/admin/customers')
def admin_customers():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    customers = Customer.query.all()
    return render_template('admin_customers.html', customers=customers)


@app.route('/admin/customers/add', methods=['GET', 'POST'])
def add_customer():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))

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
            return redirect(url_for('admin_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding customer: {str(e)}', 'error')

    return render_template('add_customer.html')

# Sales management routes


@app.route('/admin/sales')
def admin_sales():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))

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

# Reports routes


@app.route('/admin/reports')
def admin_reports():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))

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
    from datetime import timedelta
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

# Logout route


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
