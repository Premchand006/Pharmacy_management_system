import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Table, TableBody, TableCell, TableHead, TableRow, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import api from '../../services/api';
import AddProductModal from '../../components/admin/AddProductModal';

export default function ProductsPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [isModalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<any>(null);

  const fetchProducts = () => {
    api.getProducts().then(r => setProducts(r.data)).catch(() => setProducts([]));
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleAddProduct = (product: any) => {
    api.createProduct(product)
      .then(() => {
        alert('Product added successfully');
        fetchProducts(); // Refresh the list
        setModalOpen(false); // Close modal
      })
      .catch(err => {
        console.error(err);
        alert('Failed to add product');
      });
  };

  const handleEditProduct = (product: any) => {
    setEditingProduct(product);
    setModalOpen(true);
  };

  const handleUpdateProduct = (product: any) => {
    // For now, we'll use the same create endpoint
    // In a real app, you'd have an update endpoint
    api.createProduct(product)
      .then(() => {
        alert('Product updated successfully');
        fetchProducts();
        setModalOpen(false);
        setEditingProduct(null);
      })
      .catch(err => {
        console.error(err);
        alert('Failed to update product');
      });
  };

  const handleDeleteProduct = (id: number) => {
    api.deleteProduct(id)
      .then(() => {
        alert('Product deleted successfully');
        fetchProducts(); // Refresh the list
      })
      .catch(err => {
        console.error(err);
        alert('Failed to delete product');
      });
  };

  return (
    <Box>
      <Typography variant="h6">Products</Typography>
      <Button sx={{ mb: 2 }} variant="contained" onClick={() => setModalOpen(true)}>Add Product</Button>
      <AddProductModal
        open={isModalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingProduct(null);
        }}
        onSubmit={editingProduct ? handleUpdateProduct : handleAddProduct}
        editingProduct={editingProduct}
      />
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Brand</TableCell>
            <TableCell>Medicine</TableCell>
            <TableCell>MRP</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {products.map(p => (
            <TableRow key={p.p_id}>
              <TableCell>{p.p_id}</TableCell>
              <TableCell>{p.brand_name}</TableCell>
              <TableCell>{p.medicine_name}</TableCell>
              <TableCell>{p.mrp}</TableCell>
              <TableCell>
                <IconButton onClick={() => handleEditProduct(p)} aria-label="edit" sx={{ mr: 1 }}>
                  <EditIcon />
                </IconButton>
                <IconButton onClick={() => handleDeleteProduct(p.p_id)} aria-label="delete">
                  <DeleteIcon />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
