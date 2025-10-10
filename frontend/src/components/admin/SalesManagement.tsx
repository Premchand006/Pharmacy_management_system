import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  TextField,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';

interface Sale {
  sb_id: number;
  c_id: number;
  e_id: number;
  pres_id: number;
  sale_date: string;
  payment_mode: string;
  amount: number;
  tax: number;
  discount: number;
  total: number;
  status: string;
}

const SalesManagement = () => {
  const [sales, setSales] = useState<Sale[]>([]);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    employeeId: '',
    customerId: '',
  });

  useEffect(() => {
    // TODO: Fetch sales from backend API
  }, []);

  const handleFilter = () => {
    // TODO: Implement filter logic with backend API
  };

  return (
    <>
      <Box sx={{ mb: 3 }}>
        <TextField
          type="date"
          label="Start Date"
          value={filters.startDate}
          onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
          sx={{ mr: 2 }}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          type="date"
          label="End Date"
          value={filters.endDate}
          onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
          sx={{ mr: 2 }}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="Employee ID"
          value={filters.employeeId}
          onChange={(e) => setFilters({ ...filters, employeeId: e.target.value })}
          sx={{ mr: 2 }}
        />
        <TextField
          label="Customer ID"
          value={filters.customerId}
          onChange={(e) => setFilters({ ...filters, customerId: e.target.value })}
          sx={{ mr: 2 }}
        />
        <Button variant="contained" onClick={handleFilter}>
          Apply Filters
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Sale ID</TableCell>
              <TableCell>Customer ID</TableCell>
              <TableCell>Employee ID</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Payment Mode</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Tax</TableCell>
              <TableCell>Discount</TableCell>
              <TableCell>Total</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sales.map((sale) => (
              <TableRow key={sale.sb_id}>
                <TableCell>{sale.sb_id}</TableCell>
                <TableCell>{sale.c_id}</TableCell>
                <TableCell>{sale.e_id}</TableCell>
                <TableCell>{sale.sale_date}</TableCell>
                <TableCell>{sale.payment_mode}</TableCell>
                <TableCell>{sale.amount}</TableCell>
                <TableCell>{sale.tax}</TableCell>
                <TableCell>{sale.discount}</TableCell>
                <TableCell>{sale.total}</TableCell>
                <TableCell>{sale.status}</TableCell>
                <TableCell>
                  <Button size="small" color="primary">
                    View Details
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
};

export default SalesManagement;