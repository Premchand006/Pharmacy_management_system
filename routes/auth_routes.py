from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from extensions import db
from models import Customer, Employee

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        password = request.form.get('password')
        
        customer = None
        if customer_id.strip().isdigit():
            customer = db.session.get(Customer, int(customer_id))

        if (customer and customer.password_hash and password
                and check_password_hash(customer.password_hash, password)):
            session.clear()
            session['user_type'] = 'customer'
            session['user_id'] = customer.c_id
            session['user_name'] = customer.name
            return redirect(url_for('customer.customer_dashboard'))

        flash('Customer ID or password is incorrect.', 'error')
        return render_template('customer_login.html', error=True), 401

    return render_template('customer_login.html')

@auth_routes.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Employee.query.filter_by(username=username).first()
        
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_type'] = 'admin'
            session['user_id'] = user.e_id
            session['user_name'] = user.name
            return redirect(url_for('admin.admin_dashboard'))

        flash('Username or password is incorrect.', 'error')
        return render_template('admin_login.html', error=True), 401

    return render_template('admin_login.html')

@auth_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
