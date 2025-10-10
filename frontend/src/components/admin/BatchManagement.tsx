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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';

interface Batch {
  b_id: number;
  p_id: number;
  s_id: number;
  batch_no: string;
  manufacture_date: string;
  expiry_date: string;
  cost_price: number;
  qty_received: number;
  qty_available: number;
  received_on: string;
  manufacture_name: string;
  marketer_name: string;
}

const BatchManagement = () => {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    p_id: '',
    s_id: '',
    batch_no: '',
    manufacture_date: '',
    expiry_date: '',
    cost_price: '',
    qty_received: '',
    manufacture_name: '',
    marketer_name: '',
  });

  useEffect(() => {
    // TODO: Fetch batches from backend API
  }, []);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleSubmit = async () => {
    try {
      // TODO: Implement create batch logic with backend API
      handleClose();
    } catch (error) {
      console.error('Failed to create batch:', error);
    }
  };

  return (
    <>
      <Button variant="contained" color="primary" onClick={handleOpen} sx={{ mb: 2 }}>
        Add Batch
      </Button>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Batch ID</TableCell>
              <TableCell>Product ID</TableCell>
              <TableCell>Supplier ID</TableCell>
              <TableCell>Batch No</TableCell>
              <TableCell>Manufacture Date</TableCell>
              <TableCell>Expiry Date</TableCell>
              <TableCell>Cost Price</TableCell>
              <TableCell>Qty Received</TableCell>
              <TableCell>Qty Available</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {batches.map((batch) => (
              <TableRow key={batch.b_id}>
                <TableCell>{batch.b_id}</TableCell>
                <TableCell>{batch.p_id}</TableCell>
                <TableCell>{batch.s_id}</TableCell>
                <TableCell>{batch.batch_no}</TableCell>
                <TableCell>{batch.manufacture_date}</TableCell>
                <TableCell>{batch.expiry_date}</TableCell>
                <TableCell>{batch.cost_price}</TableCell>
                <TableCell>{batch.qty_received}</TableCell>
                <TableCell>{batch.qty_available}</TableCell>
                <TableCell>
                  <Button size="small" color="primary">
                    Edit
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add New Batch</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Product ID"
            value={formData.p_id}
            onChange={(e) => setFormData({ ...formData, p_id: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Supplier ID"
            value={formData.s_id}
            onChange={(e) => setFormData({ ...formData, s_id: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Batch No"
            value={formData.batch_no}
            onChange={(e) => setFormData({ ...formData, batch_no: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            type="date"
            label="Manufacture Date"
            value={formData.manufacture_date}
            onChange={(e) => setFormData({ ...formData, manufacture_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            fullWidth
            type="date"
            label="Expiry Date"
            value={formData.expiry_date}
            onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            fullWidth
            label="Cost Price"
            type="number"
            value={formData.cost_price}
            onChange={(e) => setFormData({ ...formData, cost_price: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Quantity Received"
            type="number"
            value={formData.qty_received}
            onChange={(e) => setFormData({ ...formData, qty_received: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} color="primary">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default BatchManagement;