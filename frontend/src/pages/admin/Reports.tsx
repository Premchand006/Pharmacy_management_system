import React, { useEffect, useState, useCallback } from 'react';
import { 
  Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, 
  TextField, Button, Accordion, AccordionSummary, AccordionDetails, Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import api from '../../services/api';

export default function ReportsPage() {
  const [nearExpiry, setNearExpiry] = useState<any[]>([]);
  const [stock, setStock] = useState<any[]>([]);
  const [topSelling, setTopSelling] = useState<any[]>([]);
  const [batchTraceability, setBatchTraceability] = useState<any[]>([]);
  
  // Filter states
  const [days, setDays] = useState(30);
  const [limit, setLimit] = useState(10);

  const fetchNearExpiry = useCallback(() => {
    api.getNearExpiryReport(days).then(r => setNearExpiry(r.data)).catch(() => setNearExpiry([]));
  }, [days]);

  const fetchStock = useCallback(() => {
    api.getStockReport().then(r => setStock(r.data)).catch(() => setStock([]));
  }, []);

  const fetchTopSelling = useCallback(() => {
    api.getTopSellingProductsReport(limit).then(r => setTopSelling(r.data)).catch(() => setTopSelling([]));
  }, [limit]);

  const fetchBatchTraceability = useCallback(async () => {
    try {
      const response = await api.getBatchTraceability();
      setBatchTraceability(response.data);
    } catch (error) {
      console.error('Failed to fetch batch traceability:', error);
    }
  }, []);


  useEffect(() => {
    fetchNearExpiry();
    fetchStock();
    fetchTopSelling();
    fetchBatchTraceability();
  }, [fetchNearExpiry, fetchStock, fetchTopSelling, fetchBatchTraceability]);

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4 }}>Advanced Reports & Analytics</Typography>

      {/* Batch-Level Inventory & Regulatory Traceability */}
      <Accordion sx={{ mb: 3 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Batch-Level Inventory & Regulatory Traceability</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 3 }}>
            <Button variant="contained" onClick={fetchBatchTraceability} sx={{ mb: 2 }}>
              Load Batch Traceability Data
            </Button>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Batch ID</TableCell>
                  <TableCell>Product</TableCell>
                  <TableCell>Supplier</TableCell>
                  <TableCell>Purchase Date</TableCell>
                  <TableCell>Expiry Date</TableCell>
                  <TableCell>Quantity</TableCell>
                  <TableCell>Sales Count</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {batchTraceability.map(batch => (
                  <TableRow key={batch.b_id}>
                    <TableCell>{batch.b_id}</TableCell>
                    <TableCell>{batch.medicine_name}</TableCell>
                    <TableCell>{batch.supplier_name}</TableCell>
                    <TableCell>{new Date(batch.purchase_date).toLocaleDateString()}</TableCell>
                    <TableCell>{new Date(batch.expiry_date).toLocaleDateString()}</TableCell>
                    <TableCell>{batch.quantity}</TableCell>
                    <TableCell>{batch.sales_count || 0}</TableCell>
                    <TableCell>
                      <Chip 
                        label={batch.quantity > 0 ? 'In Stock' : 'Out of Stock'} 
                        color={batch.quantity > 0 ? 'success' : 'error'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        </AccordionDetails>
      </Accordion>


      {/* Standard Reports */}
      <Accordion sx={{ mb: 3 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Standard Reports</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {/* Near Expiry Report */}
          <Box sx={{ my: 4 }}>
            <Typography variant="h6">Near Expiry Report</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <TextField
                label="Days to Expiry"
                type="number"
                value={days}
                onChange={(e) => setDays(parseInt(e.target.value, 10))}
                sx={{ mr: 2 }}
              />
            </Box>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Batch ID</TableCell>
                  <TableCell>Product ID</TableCell>
                  <TableCell>Expiry Date</TableCell>
                  <TableCell>Quantity Available</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {nearExpiry.map(b => (
                  <TableRow key={b.b_id}>
                    <TableCell>{b.b_id}</TableCell>
                    <TableCell>{b.p_id}</TableCell>
                    <TableCell>{new Date(b.expiry_date).toLocaleDateString()}</TableCell>
                    <TableCell>{b.qty_available}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>

          {/* Stock Report */}
          <Box sx={{ my: 4 }}>
            <Typography variant="h6">Stock Report</Typography>
            <Button variant="contained" onClick={fetchStock} sx={{ mb: 2 }}>Refresh Stock Report</Button>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Product ID</TableCell>
                  <TableCell>Medicine Name</TableCell>
                  <TableCell>Total Quantity</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {stock.map(s => (
                  <TableRow key={s.p_id}>
                    <TableCell>{s.p_id}</TableCell>
                    <TableCell>{s.medicine_name}</TableCell>
                    <TableCell>{s.total_quantity}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>

          {/* Top Selling Products */}
          <Box sx={{ my: 4 }}>
            <Typography variant="h6">Top Selling Products</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <TextField
                label="Limit"
                type="number"
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value, 10))}
                sx={{ mr: 2 }}
              />
            </Box>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Product ID</TableCell>
                  <TableCell>Medicine Name</TableCell>
                  <TableCell>Total Sold</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {topSelling.map(p => (
                  <TableRow key={p.p_id}>
                    <TableCell>{p.p_id}</TableCell>
                    <TableCell>{p.medicine_name}</TableCell>
                    <TableCell>{p.total_sold}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}
