from .auth import router as auth
from .customers import router as customers
from .products import router as products
from .employees import router as employees
from .suppliers import router as suppliers
from .prescriptions import router as prescriptions
from .batches import router as batches
from .sales import router as sales
from .reports import router as reports
from .purchases import router as purchases

__all__ = [
    'auth', 'customers', 'products', 'employees', 'suppliers',
    'prescriptions', 'batches', 'sales', 'reports', 'purchases'
]
