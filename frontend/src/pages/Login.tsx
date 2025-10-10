import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, TextField, Button, Typography, Alert } from '@mui/material';

export default function LoginPage() {
  const [id, setId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCustomerSignIn = async () => {
    const idNum = Number(id);
    if (!idNum) {
      setError('Please enter a valid customer ID');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Check if customer exists in database
      const response = await fetch(`http://127.0.0.1:8000/api/customers/${idNum}`);
      if (!response.ok) {
        setError('Customer not found in database. Please register first.');
        setLoading(false);
        return;
      }
      const customer = await response.json();
      if (customer && customer.c_id) {
        setLoading(false);
        navigate(`/customer-dashboard?c_id=${idNum}`);
      } else {
        setError('Customer not found in database. Please register first.');
        setLoading(false);
      }
    } catch (error) {
      setError('Customer not found in database. Please register first.');
      setLoading(false);
    }
  };

  const handleAdminSignIn = async () => {
    const idNum = Number(id);
    if (!idNum) {
      setError('Please enter a valid admin/employee ID');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Check if employee exists in database
      const response = await fetch(`http://127.0.0.1:8000/api/employees/${idNum}`);
      if (!response.ok) {
        setError('Admin/Employee not found in database. Please register first.');
        setLoading(false);
        return;
      }
      const employee = await response.json();
      if (employee && employee.e_id) {
        setLoading(false);
        navigate(`/admin-dashboard?s_id=${idNum}`);
      } else {
        setError('Admin/Employee not found in database. Please register first.');
        setLoading(false);
      }
    } catch (error) {
      setError('Admin/Employee not found in database. Please register first.');
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 520, mx: 'auto', textAlign: 'center' }}>
      <Typography variant="h4" gutterBottom>Pharmacy Management System</Typography>
      <Typography variant="h6" gutterBottom>Sign In</Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <TextField 
        label={'User ID'} 
        value={id} 
        onChange={e => {
          setId(e.target.value);
          setError(''); // Clear error when user types
        }} 
        fullWidth 
        sx={{ mb: 2 }} 
      />

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button 
          variant="contained" 
          onClick={handleCustomerSignIn}
          disabled={loading}
          sx={{
            '&:hover': {
              backgroundColor: '#1976d2',
              color: 'white'
            }
          }}
        >
          {loading ? 'Checking...' : 'Sign In as Customer'}
        </Button>
        <Button 
          variant="outlined" 
          onClick={handleAdminSignIn}
          disabled={loading}
          sx={{
            '&:hover': {
              backgroundColor: '#1976d2',
              color: 'white',
              borderColor: '#1976d2'
            }
          }}
        >
          {loading ? 'Checking...' : 'Sign In as Admin'}
        </Button>
      </Box>
    </Box>
  );
}
