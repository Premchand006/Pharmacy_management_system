import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, Button } from '@mui/material';
import api from '../../services/api';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  useEffect(() => { api.getCustomers().then(r => setCustomers(r.data)).catch(() => setCustomers([])); }, []);

  return (
    <Box>
      <Typography variant="h6">Customers</Typography>
      <Table>
        <TableHead>
          <TableRow><TableCell>ID</TableCell><TableCell>Name</TableCell><TableCell>Phone</TableCell><TableCell>Actions</TableCell></TableRow>
        </TableHead>
        <TableBody>
          {customers.map(c => (
            <TableRow key={c.c_id}>
              <TableCell>{c.c_id}</TableCell>
              <TableCell>{c.name}</TableCell>
              <TableCell>{c.phone}</TableCell>
              <TableCell>
                <Button size="small" onClick={() => window.location.assign(`/customer/prescriptions?c_id=${c.c_id}`)}>View Prescriptions</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
