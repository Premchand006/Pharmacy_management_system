import React, { useState } from 'react';
import { Box, TextField, Button, Typography, ToggleButton, ToggleButtonGroup } from '@mui/material';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function RegisterPage() {
  const [type, setType] = useState<'customer' | 'supplier'>('customer');
  const [form, setForm] = useState<any>({});
  const navigate = useNavigate();

  const handleSubmit = async () => {
    try {
      if (type === 'customer') {
        await api.createCustomer(form);
        alert('Customer created');
      } else {
        await api.createSupplier(form);
        alert('Supplier created');
      }
      navigate('/');
    } catch (e: any) {
      alert(e.message || 'Error');
    }
  };

  return (
    <Box sx={{ maxWidth: 720, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>Create New Account</Typography>
      <ToggleButtonGroup value={type} exclusive onChange={(_, v) => v && setType(v)} sx={{ mb: 2 }}>
        <ToggleButton value="customer">Customer</ToggleButton>
        <ToggleButton value="supplier">Supplier</ToggleButton>
      </ToggleButtonGroup>

      {type === 'customer' ? (
        <Box>
          <TextField label="Name" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, name: e.target.value })} />
          <TextField label="Phone" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, phone: e.target.value })} />
          <TextField label="Address" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, address: e.target.value })} />
          <TextField label="Age" type="number" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, age: Number(e.target.value) })} />
          <TextField label="Gender" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, gender: e.target.value })} />
        </Box>
      ) : (
        <Box>
          <TextField label="Firm Name" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, firm_name: e.target.value })} />
          <TextField label="Owner Name" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, owner_name: e.target.value })} />
          <TextField label="GST No" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, gst_no: e.target.value })} />
          <TextField label="Phone" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, phone: e.target.value })} />
          <TextField label="Address" fullWidth sx={{ mb: 1 }} onChange={e => setForm({ ...form, address: e.target.value })} />
        </Box>
      )}

      <Button variant="contained" sx={{ mt: 2 }} onClick={handleSubmit}>Create</Button>
    </Box>
  );
}