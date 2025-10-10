import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, Paper, Accordion, AccordionSummary, AccordionDetails, Button } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import api from '../../services/api';

export default function SalesPage() {
  const [sales, setSales] = useState<any[]>([]);
  const [saleItems, setSaleItems] = useState<{[key: number]: any[]}>({});

  useEffect(() => { 
    api.getSales().then(r => setSales(r.data)).catch(() => setSales([])); 
  }, []);

  const fetchSaleItems = async (saleId: number) => {
    try {
      const response = await api.getSaleItems(saleId);
      setSaleItems(prev => ({...prev, [saleId]: response.data}));
    } catch (error) {
      console.error('Failed to fetch sale items:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3 }}>Sales Based on Products</Typography>
      {sales.map(sale => (
        <Accordion key={sale.sb_id} sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">
              Sale ID: {sale.sb_id} - Product: {sale.medicine_name || 'N/A'} - Total: ₹{sale.total}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ mb: 2 }}>
              <Button 
                variant="contained" 
                onClick={() => fetchSaleItems(sale.sb_id)}
                sx={{ mb: 2 }}
              >
                Load Sale Items
              </Button>
            </Box>
            
            {saleItems[sale.sb_id] && saleItems[sale.sb_id].length > 0 && (
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Sale Items Details</Typography>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Item ID</TableCell>
                      <TableCell>Product ID</TableCell>
                      <TableCell>Product Name</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Unit Price</TableCell>
                      <TableCell>Total Price</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {saleItems[sale.sb_id].map((item: any) => (
                      <TableRow key={item.si_id}>
                        <TableCell>{item.si_id}</TableCell>
                        <TableCell>{item.p_id}</TableCell>
                        <TableCell>{item.medicine_name || 'N/A'}</TableCell>
                        <TableCell>{item.quantity}</TableCell>
                        <TableCell>₹{item.unit_price}</TableCell>
                        <TableCell>₹{item.total_price}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Paper>
            )}
            
            {saleItems[sale.sb_id] && saleItems[sale.sb_id].length === 0 && (
              <Typography color="text.secondary">No sale items found for this sale.</Typography>
            )}
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
}
