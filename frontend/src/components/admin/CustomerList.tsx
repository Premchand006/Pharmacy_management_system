import React, { useState, useEffect } from 'react';
import apiClient from '../../services/api';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';

interface Customer {
  c_id: number;
  name: string;
  phone: string;
  address: string;
  age: number;
  gender: string;
}

const CustomerList = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: '',
    age: '',
    gender: '',
  });

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const res = await apiClient.getCustomers();
      setCustomers(res.data);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this customer?')) return;
    try {
      await apiClient.deleteCustomer(id);
      setCustomers(customers.filter((c) => c.c_id !== id));
    } catch (error) {
      alert('Failed to delete customer');
    }
  };

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    setOpen(false);
    setFormData({ name: '', phone: '', address: '', age: '', gender: '' });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      const payload = {
        ...formData,
        age: parseInt(formData.age),
      };
      await apiClient.createCustomer(payload);
      fetchCustomers();
      handleClose();
    } catch (error) {
      alert('Failed to add customer');
    }
  };

  return (
    <>
      <Button variant="contained" color="primary" onClick={handleOpen} sx={{ mb: 2 }}>
        Add Customer
      </Button>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Address</TableCell>
              <TableCell>Age</TableCell>
              <TableCell>Gender</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {customers.map((customer) => (
              <TableRow key={customer.c_id}>
                <TableCell>{customer.c_id}</TableCell>
                <TableCell>{customer.name}</TableCell>
                <TableCell>{customer.phone}</TableCell>
                <TableCell>{customer.address}</TableCell>
                <TableCell>{customer.age}</TableCell>
                <TableCell>{customer.gender}</TableCell>
                <TableCell>
                  <Button size="small" color="primary">
                    View Details
                  </Button>
                  <Button size="small" color="error" onClick={() => handleDelete(customer.c_id)}>
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add New Customer</DialogTitle>
        <DialogContent>
          <TextField fullWidth margin="normal" label="Name" name="name" value={formData.name} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Phone" name="phone" value={formData.phone} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Address" name="address" value={formData.address} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Age" name="age" type="number" value={formData.age} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Gender" name="gender" value={formData.gender} onChange={handleChange} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} color="primary">Add</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default CustomerList;