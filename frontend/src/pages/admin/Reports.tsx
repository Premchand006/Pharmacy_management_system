import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, TextField, Button } from '@mui/material';
import api from '../../services/api';

export default function ReportsPage() {
  const [nearExpiry, setNearExpiry] = useState<any[]>([]);
  const [stock, setStock] = useState<any[]>([]);
  const [topSelling, setTopSelling] = useState<any[]>([]);
  const [days, setDays] = useState(30);
  const [limit, setLimit] = useState(10);

  const fetchNearExpiry = () => {
    api.getNearExpiryReport(days).then(r => setNearExpiry(r.data)).catch(() => setNearExpiry([]));
  };

  const fetchStock = () => {
    api.getStockReport().then(r => setStock(r.data)).catch(() => setStock([]));
  };

  const fetchTopSelling = () => {
    api.getTopSellingProductsReport(limit).then(r => setTopSelling(r.data)).catch(() => setTopSelling([]));
  };

  useEffect(() => {
    fetchNearExpiry();
    fetchStock();
    fetchTopSelling();
  }, []);

  return (
    <Box>
      <Typography variant="h6">Reports</Typography>

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
          <Button variant="contained" onClick={fetchNearExpiry}>Generate</Button>
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

      <Box sx={{ my: 4 }}>
        <Typography variant="h6">Stock Report</Typography>
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
          <Button variant="contained" onClick={fetchTopSelling}>Generate</Button>
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
    </Box>
  );
}
