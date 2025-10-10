import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import LoginPage from './pages/Login';
import RegisterPage from './pages/Register';
import CustomerDashboard from './pages/CustomerDashboard';
import AdminDashboard from './pages/AdminDashboard';
import ProductsPage from './pages/admin/Products';
import EmployeesPage from './pages/admin/Employees';
import BatchesPage from './pages/admin/Batches';
import CustomersPage from './pages/admin/Customers';
import SalesPage from './pages/admin/Sales';
import ReportsPage from './pages/admin/Reports';
import PurchasesPage from './pages/admin/Purchases';
import PrescriptionsPage from './pages/customer/Prescriptions';
import CheckoutPage from './pages/customer/Checkout';

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Pharmacy Management System
            </Typography>
            <Button color="inherit" component={Link} to="/">Sign In</Button>
            <Button color="inherit" component={Link} to="/register">Create New</Button>
          </Toolbar>
        </AppBar>
        <Container sx={{ mt: 3 }}>
          <Routes>
            <Route path="/" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/customer-dashboard/*" element={<CustomerDashboard />} />
            <Route path="/admin-dashboard/*" element={<AdminDashboard />} />

            {/* Admin sub-pages */}
            <Route path="/admin/products" element={<ProductsPage />} />
            <Route path="/admin/employees" element={<EmployeesPage />} />
            <Route path="/admin/batches" element={<BatchesPage />} />
            <Route path="/admin/customers" element={<CustomersPage />} />
            <Route path="/admin/sales" element={<SalesPage />} />
            <Route path="/admin/purchases" element={<PurchasesPage />} />
            <Route path="/admin/reports" element={<ReportsPage />} />

            {/* Customer pages */}
            <Route path="/customer/prescriptions" element={<PrescriptionsPage />} />
            <Route path="/customer/checkout" element={<CheckoutPage />} />
          </Routes>
        </Container>
      </Router>
    </ThemeProvider>
  );
}

export default App;