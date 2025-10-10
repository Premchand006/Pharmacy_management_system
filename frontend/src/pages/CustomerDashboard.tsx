import React from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Box, Button, Typography } from '@mui/material';

export default function CustomerDashboard() {
  const [search] = useSearchParams();
  const c_id = search.get('c_id');

  return (
    <Box>
      <Typography variant="h5">Customer Dashboard</Typography>
      <Typography sx={{ mb: 2 }}>Customer ID: {c_id}</Typography>
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button variant="contained" component={Link} to={`/customer/prescriptions?c_id=${c_id}`}>Show Prescriptions</Button>
        <Button variant="outlined" component={Link} to={`/customer/prescriptions?c_id=${c_id}&action=add`}>Add Prescription</Button>
      </Box>
    </Box>
  );
}