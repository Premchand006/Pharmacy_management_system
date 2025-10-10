import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, Button, Paper, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import api from '../../services/api';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [prescriptions, setPrescriptions] = useState<{[key: number]: any[]}>({});

  useEffect(() => { 
    api.getCustomers().then(r => setCustomers(r.data)).catch(() => setCustomers([])); 
  }, []);

  const fetchPrescriptions = async (customerId: number) => {
    try {
      const response = await api.getPrescriptionsByCustomer(customerId);
      setPrescriptions(prev => ({...prev, [customerId]: response.data}));
    } catch (error) {
      console.error('Failed to fetch prescriptions:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3 }}>Customer Details and Prescriptions</Typography>
      {customers.map(customer => (
        <Accordion key={customer.c_id} sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">
              {customer.name} (ID: {customer.c_id}) - Phone: {customer.phone}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            
            {prescriptions[customer.c_id] && prescriptions[customer.c_id].length > 0 && (
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Prescription Details</Typography>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Prescription ID</TableCell>
                      <TableCell>Medicine</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Dosage</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {prescriptions[customer.c_id].map((prescription: any) => (
                      <TableRow key={prescription.pr_id}>
                        <TableCell>{prescription.pr_id}</TableCell>
                        <TableCell>{prescription.medicine_name}</TableCell>
                        <TableCell>{prescription.quantity}</TableCell>
                        <TableCell>{prescription.dosage}</TableCell>
                        <TableCell>{new Date(prescription.date).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Paper>
            )}
            
            {prescriptions[customer.c_id] && prescriptions[customer.c_id].length === 0 && (
              <Typography color="text.secondary">No prescriptions found for this customer.</Typography>
            )}
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
}
