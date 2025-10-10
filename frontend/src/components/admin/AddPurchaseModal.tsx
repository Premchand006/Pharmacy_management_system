import React, { useState } from 'react';
import { Modal, Box, Typography, TextField, Button } from '@mui/material';

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 500,
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

interface AddPurchaseModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (purchase: any) => void;
}

export default function AddPurchaseModal({ open, onClose, onSubmit }: AddPurchaseModalProps) {
  const [purchase, setPurchase] = useState({
    b_id: 0,
    s_id: 0,
    p_id: 0,
    date: '',
    cost: 0,
    status: 'received'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPurchase(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    onSubmit({
      ...purchase,
      b_id: Number(purchase.b_id),
      s_id: Number(purchase.s_id),
      p_id: Number(purchase.p_id),
      cost: Number(purchase.cost),
      date: purchase.date || new Date().toISOString().split('T')[0]
    });
  };

  return (
    <Modal open={open} onClose={onClose} aria-labelledby="add-purchase-modal">
      <Box sx={style}>
        <Typography id="add-purchase-modal" variant="h6">Add Purchase</Typography>
        <TextField margin="dense" name="b_id" label="Batch ID (optional)" fullWidth value={purchase.b_id} onChange={handleChange} />
        <TextField margin="dense" name="s_id" label="Supplier ID" type="number" fullWidth value={purchase.s_id} onChange={handleChange} />
        <TextField margin="dense" name="p_id" label="Product ID" type="number" fullWidth value={purchase.p_id} onChange={handleChange} />
        <TextField margin="dense" name="date" label="Date" type="date" fullWidth InputLabelProps={{ shrink: true }} value={purchase.date} onChange={handleChange} />
        <TextField margin="dense" name="cost" label="Cost" type="number" fullWidth value={purchase.cost} onChange={handleChange} />
        <TextField margin="dense" name="status" label="Status" fullWidth value={purchase.status} onChange={handleChange} />
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" sx={{ ml: 1 }}>Add</Button>
        </Box>
      </Box>
    </Modal>
  );
}
