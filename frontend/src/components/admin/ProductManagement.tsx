import React from 'react';
import apiClient from '../../services/api';
import { Container, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material';

interface Product {
  p_id: number;
  brand_name: string;
  medicine_name: string;
  form: string;
  strength: string;
  packing: string;
  prescription_type: string;
  mrp: number;
  unit_price: number;
}

const ProductManagement = () => {
  const [products, setProducts] = React.useState<Product[]>([]);
  const [open, setOpen] = React.useState(false);
  const [formData, setFormData] = React.useState({
    brand_name: '',
    medicine_name: '',
    form: '',
    strength: '',
    packing: '',
    prescription_type: '',
    mrp: '',
    unit_price: '',
  });

  React.useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const res = await apiClient.getProducts();
      setProducts(res.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    try {
      await apiClient.deleteProduct(id);
      setProducts(products.filter((p) => p.p_id !== id));
    } catch (error) {
      alert('Failed to delete product');
    }
  };

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    setOpen(false);
    setFormData({
      brand_name: '',
      medicine_name: '',
      form: '',
      strength: '',
      packing: '',
      prescription_type: '',
      mrp: '',
      unit_price: '',
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      // Validate required fields
      if (!formData.medicine_name) {
        alert('Medicine Name is required');
        return;
      }

      // Convert string values to numbers and prepare payload
      const payload = {
        ...formData,
        mrp: parseFloat(formData.mrp) || 0,
        unit_price: parseFloat(formData.unit_price) || 0,
        // Ensure all required fields from schema are present
        brand_name: formData.brand_name || '',
        form: formData.form || '',
        strength: formData.strength || '',
        packing: formData.packing || '',
        prescription_type: formData.prescription_type || 'OTC'
      };

      // Call the API to create product
      await apiClient.createProduct(payload);
      
      // Refresh the products list
      fetchProducts();
      
      // Clear form and close dialog
      handleClose();
      alert('Product added successfully');
    } catch (error: any) {
      // Show detailed error message if available
      alert(error.response?.data?.detail || 'Failed to add product');
    }
  };

  return (
    <>
      <Button variant="contained" color="primary" onClick={handleOpen} sx={{ mb: 2 }}>
        Add Product
      </Button>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Brand Name</TableCell>
              <TableCell>Medicine Name</TableCell>
              <TableCell>Form</TableCell>
              <TableCell>Strength</TableCell>
              <TableCell>Packing</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>MRP</TableCell>
              <TableCell>Unit Price</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {products.map((product) => (
              <TableRow key={product.p_id}>
                <TableCell>{product.p_id}</TableCell>
                <TableCell>{product.brand_name}</TableCell>
                <TableCell>{product.medicine_name}</TableCell>
                <TableCell>{product.form}</TableCell>
                <TableCell>{product.strength}</TableCell>
                <TableCell>{product.packing}</TableCell>
                <TableCell>{product.prescription_type}</TableCell>
                <TableCell>{product.mrp}</TableCell>
                <TableCell>{product.unit_price}</TableCell>
                <TableCell>
                  <Button size="small" color="primary">
                    Edit
                  </Button>
                  <Button size="small" color="primary">
                    View Batches
                  </Button>
                  <Button size="small" color="error" onClick={() => handleDelete(product.p_id)}>
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add New Product</DialogTitle>
        <DialogContent>
          <TextField fullWidth margin="normal" label="Brand Name" name="brand_name" value={formData.brand_name} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Medicine Name" name="medicine_name" value={formData.medicine_name} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Form" name="form" value={formData.form} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Strength" name="strength" value={formData.strength} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Packing" name="packing" value={formData.packing} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Prescription Type" name="prescription_type" value={formData.prescription_type} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="MRP" name="mrp" type="number" value={formData.mrp} onChange={handleChange} />
          <TextField fullWidth margin="normal" label="Unit Price" name="unit_price" type="number" value={formData.unit_price} onChange={handleChange} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} color="primary">Add</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ProductManagement;