from flask import Blueprint

auth = Blueprint('auth', __name__)
admin = Blueprint('admin', __name__)
customer = Blueprint('customer', __name__)

from . import auth_routes, admin_routes, customer_routes
