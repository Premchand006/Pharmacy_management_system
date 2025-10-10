import React, { useState } from 'react';
import { Modal, Box, Typography, TextField, Button } from '@mui/material';

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

interface AddBatchModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (batch: any) => void;
}

export default function AddBatchModal({ open, onClose, onSubmit }: AddBatchModalProps) {
  const [batch, setBatch] = useState({
    p_id: 0,
    s_id: 0,
    batch_no: '',
    manufacture_date: '',
    expiry_date: '',
    cost_price: 0,
    qty_received: 0,
    qty_available: 0,
    received_on: '',
    manufacture_name: '',
    marketer_name: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setBatch(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    onSubmit(batch);
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="add-batch-modal-title"
    >
      <Box sx={style}>
        <Typography id="add-batch-modal-title" variant="h6" component="h2">
          Add New Batch
        </Typography>
        <TextField margin="dense" name="p_id" label="Product ID" type="number" fullWidth value={batch.p_id} onChange={handleChange} />
        <TextField margin="dense" name="s_id" label="Supplier ID" type="number" fullWidth value={batch.s_id} onChange={handleChange} />
        <TextField margin="dense" name="batch_no" label="Batch Number" fullWidth value={batch.batch_no} onChange={handleChange} />
        <TextField margin="dense" name="manufacture_date" label="Manufacture Date" type="date" fullWidth InputLabelProps={{ shrink: true }} value={batch.manufacture_date} onChange={handleChange} />
        <TextField margin="dense" name="expiry_date" label="Expiry Date" type="date" fullWidth InputLabelProps={{ shrink: true }} value={batch.expiry_date} onChange={handleChange} />
        <TextField margin="dense" name="cost_price" label="Cost Price" type="number" fullWidth value={batch.cost_price} onChange={handleChange} />
        <TextField margin="dense" name="qty_received" label="Quantity Received" type="number" fullWidth value={batch.qty_received} onChange={handleChange} />
        <TextField margin="dense" name="qty_available" label="Quantity Available" type="number" fullWidth value={batch.qty_available} onChange={handleChange} />
        <TextField margin="dense" name="received_on" label="Received On" type="date" fullWidth InputLabelProps={{ shrink: true }} value={batch.received_on} onChange={handleChange} />
        <TextField margin="dense" name="manufacture_name" label="Manufacturer Name" fullWidth value={batch.manufacture_name} onChange={handleChange} />
        <TextField margin="dense" name="marketer_name" label="Marketer Name" fullWidth value={batch.marketer_name} onChange={handleChange} />
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" sx={{ ml: 1 }}>Add</Button>
        </Box>
      </Box>
    </Modal>
  );
}
