import React from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Box, Button, Typography, Stack } from '@mui/material';

export default function AdminDashboard() {
  const [search] = useSearchParams();
  const s_id = search.get('s_id');

  return (
    <Box>
      <Typography variant="h5">Admin / Supplier Dashboard</Typography>
      <Typography sx={{ mb: 2 }}>ID: {s_id}</Typography>
      <Stack spacing={2} direction="column" sx={{ mt: 3 }}>
        <Button variant="contained" size="large" component={Link} to="/admin/employees">Employees</Button>
        <Button variant="contained" size="large" component={Link} to="/admin/products">Products</Button>
        <Button variant="contained" size="large" component={Link} to="/admin/customers">Customers</Button>
        <Button variant="contained" size="large" component={Link} to="/admin/sales">Sales</Button>
        <Button variant="contained" size="large" component={Link} to="/admin/reports">Reports</Button>
      </Stack>
    </Box>
  );
}