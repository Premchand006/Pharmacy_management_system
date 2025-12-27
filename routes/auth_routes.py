from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from models import Customer, Employee

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        password = request.form.get('password')
        
        customer = Customer.query.filter_by(c_id=customer_id).first()
        
        if customer:
            # Check password if provided, or if hash exists
            offset_auth = True
            if customer.password_hash:
                if not password or not check_password_hash(customer.password_hash, password):
                    offset_auth = False
            
            if offset_auth:
                session['user_type'] = 'customer'
                session['user_id'] = customer.c_id
                session['user_name'] = customer.name
                return redirect(url_for('customer.customer_dashboard'))
            else:
                flash('Invalid Password', 'error')
                return render_template('customer_login.html', error=True)
        else:
            flash('Invalid Customer ID', 'error')
            return render_template('customer_login.html', error=True)

    return render_template('customer_login.html')

@auth_routes.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Employee.query.filter_by(username=username).first()
        
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            session['user_type'] = 'admin'
            session['user_name'] = user.name
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
            return render_template('admin_login.html', error=True)

    return render_template('admin_login.html')

@auth_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
