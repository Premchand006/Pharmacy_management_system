from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import db
from models import Prescription, PrescriptionItem, Product
from datetime import datetime

customer_routes = Blueprint('customer', __name__)

@customer_routes.before_request
def require_customer():
    if session.get('user_type') != 'customer':
        return redirect(url_for('index')) # Or auth.customer_login

@customer_routes.route('/customer_dashboard')
def customer_dashboard():
    return render_template('customer_dashboard.html')

@customer_routes.route('/customer_prescriptions')
def customer_prescriptions():
    customer_id = session.get('user_id')
    prescriptions = Prescription.query.filter_by(c_id=customer_id).all()
    return render_template('customer_prescriptions.html', prescriptions=prescriptions)

@customer_routes.route('/prescription_items/<int:prescription_id>')
def prescription_items(prescription_id):
    items = PrescriptionItem.query.filter_by(pres_id=prescription_id).all()
    prescription = Prescription.query.get(prescription_id)
    return render_template('prescription_items.html', items=items, prescription=prescription)

@customer_routes.route('/add_prescription', methods=['GET', 'POST'])
def add_prescription():
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
            return redirect(url_for('customer.customer_prescriptions'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding prescription: {str(e)}', 'error')

    products = Product.query.all()
    return render_template('add_prescription.html', products=products)
