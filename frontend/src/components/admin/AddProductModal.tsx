import React, { useState, useEffect } from 'react';
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

interface AddProductModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (product: any) => void;
  editingProduct?: any;
}

export default function AddProductModal({ open, onClose, onSubmit, editingProduct }: AddProductModalProps) {
  const [product, setProduct] = useState({
    brand_name: '',
    medicine_name: '',
    form: '',
    strength: '',
    packing: '',
    prescription_type: 'OTC',
    mrp: 0,
    unit_price: 0,
  });

  useEffect(() => {
    if (editingProduct) {
      setProduct({
        brand_name: editingProduct.brand_name || '',
        medicine_name: editingProduct.medicine_name || '',
        form: editingProduct.form || '',
        strength: editingProduct.strength || '',
        packing: editingProduct.packing || '',
        prescription_type: editingProduct.prescription_type || 'OTC',
        mrp: editingProduct.mrp || 0,
        unit_price: editingProduct.unit_price || 0,
      });
    } else {
      setProduct({
        brand_name: '',
        medicine_name: '',
        form: '',
        strength: '',
        packing: '',
        prescription_type: 'OTC',
        mrp: 0,
        unit_price: 0,
      });
    }
  }, [editingProduct, open]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProduct(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    onSubmit(product);
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="add-product-modal-title"
    >
      <Box sx={style}>
        <Typography id="add-product-modal-title" variant="h6" component="h2">
          {editingProduct ? 'Edit Product' : 'Add New Product'}
        </Typography>
        <TextField margin="dense" name="brand_name" label="Brand Name" fullWidth value={product.brand_name} onChange={handleChange} />
        <TextField margin="dense" name="medicine_name" label="Medicine Name" fullWidth value={product.medicine_name} onChange={handleChange} />
        <TextField margin="dense" name="form" label="Form (e.g., Tablet)" fullWidth value={product.form} onChange={handleChange} />
        <TextField margin="dense" name="strength" label="Strength (e.g., 500mg)" fullWidth value={product.strength} onChange={handleChange} />
        <TextField margin="dense" name="packing" label="Packing (e.g., 10 tablets)" fullWidth value={product.packing} onChange={handleChange} />
        <TextField margin="dense" name="mrp" label="MRP" type="number" fullWidth value={product.mrp} onChange={handleChange} />
        <TextField margin="dense" name="unit_price" label="Unit Price" type="number" fullWidth value={product.unit_price} onChange={handleChange} />
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" sx={{ ml: 1 }}>
            {editingProduct ? 'Update' : 'Add'}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
}
