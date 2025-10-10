import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';
const API_PREFIX = '/api'; // backend routers are mounted under /api

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

const apiClient = {
  // Customers
  createCustomer: (payload: any) => api.post(`${API_PREFIX}/customers/`, payload),
  getCustomers: () => api.get(`${API_PREFIX}/customers/`),
  getCustomer: (id: number) => api.get(`${API_PREFIX}/customers/${id}`),
  deleteCustomer: (id: number) => api.delete(`${API_PREFIX}/customers/${id}`),

  // Employees
  createEmployee: (payload: any) => api.post(`${API_PREFIX}/employees/`, payload),
  getEmployees: () => api.get(`${API_PREFIX}/employees/`),
  deleteEmployee: (id: number) => api.delete(`${API_PREFIX}/employees/${id}`),

  // Suppliers
  createSupplier: (payload: any) => api.post(`${API_PREFIX}/suppliers/`, payload),
  getSuppliers: () => api.get(`${API_PREFIX}/suppliers/`),

  // Products
  createProduct: (payload: any) => api.post(`${API_PREFIX}/products/`, payload),
  getProducts: () => api.get(`${API_PREFIX}/products/`),
  deleteProduct: (id: number) => api.delete(`${API_PREFIX}/products/${id}`),

  // Prescriptions
  createPrescription: (payload: any) => api.post(`${API_PREFIX}/prescriptions/`, payload),
  getCustomerPrescriptions: (customerId: number) => api.get(`${API_PREFIX}/prescriptions/customer/${customerId}`),
  getPrescriptionsByCustomer: (customerId: number) => api.get(`${API_PREFIX}/prescriptions/customer/${customerId}`),

  // Batches
  createBatch: (payload: any) => api.post(`${API_PREFIX}/batches/`, payload),
  getProductBatches: (productId: number) => api.get(`${API_PREFIX}/batches/product/${productId}`),

  // Sales
  createSale: (payload: any) => api.post(`${API_PREFIX}/sales/`, payload),
  getSales: () => api.get(`${API_PREFIX}/sales/`),
  getCustomerSales: (customerId: number) => api.get(`${API_PREFIX}/sales/customer/${customerId}`),
  getFilteredSales: (params: any) => api.get(`${API_PREFIX}/sales/filter/`, { params }),
  getSaleItems: (saleId: number) => api.get(`${API_PREFIX}/sales/${saleId}/items`),

  // Purchases
  createPurchase: (payload: any) => api.post(`${API_PREFIX}/purchases/`, payload),
  getPurchases: () => api.get(`${API_PREFIX}/purchases/`),

  // Reports
  getNearExpiryReport: (days: number) => api.get(`${API_PREFIX}/reports/near-expiry?days=${days}`),
  getStockReport: () => api.get(`${API_PREFIX}/reports/stock`),
  getTopSellingProductsReport: (limit: number) => api.get(`${API_PREFIX}/reports/top-selling?limit=${limit}`),
  getBatchTraceability: () => api.get(`${API_PREFIX}/reports/batch-traceability`),
  searchProducts: (params: string) => api.get(`${API_PREFIX}/reports/search-products?${params}`),
  searchCustomers: (params: string) => api.get(`${API_PREFIX}/reports/search-customers?${params}`),
};

export default apiClient;