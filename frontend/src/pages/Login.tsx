import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, TextField, Button, Typography, ToggleButtonGroup, ToggleButton } from '@mui/material';

export default function LoginPage() {
  const [id, setId] = useState('');
  const navigate = useNavigate();

  const handleCustomerSignIn = () => {
    const idNum = Number(id);
    if (!idNum) return alert('Enter customer id');
    navigate(`/customer-dashboard?c_id=${idNum}`);
  };

  const handleAdminSignIn = () => {
    const idNum = Number(id);
    if (!idNum) return alert('Enter admin/employee id');
    navigate(`/admin-dashboard?s_id=${idNum}`);
  };

  return (
    <Box sx={{ maxWidth: 520, mx: 'auto', textAlign: 'center' }}>
      <Typography variant="h4" gutterBottom>Pharmacy Management System</Typography>
      <Typography variant="h6" gutterBottom>Sign In</Typography>

      <TextField label={'User ID'} value={id} onChange={e => setId(e.target.value)} fullWidth sx={{ mb: 2 }} />

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button variant="contained" onClick={handleCustomerSignIn}>Sign In as Customer</Button>
        <Button variant="outlined" onClick={handleAdminSignIn}>Sign In as Admin</Button>
      </Box>
    </Box>
  );
}
