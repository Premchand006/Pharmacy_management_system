import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import api from '../../services/api';
import AddBatchModal from '../../components/admin/AddBatchModal';

export default function BatchesPage() {
  const [batches, setBatches] = useState<any[]>([]);
  const [isModalOpen, setModalOpen] = useState(false);

  const fetchBatches = () => {
    // For demo, fetch products and their batches for first product
    // In a real app, you'd likely have a product selector
    api.getProducts().then(r => {
      const p = r.data[0];
      if (p) {
        api.getProductBatches(p.p_id).then(b => setBatches(b.data)).catch(() => setBatches([]));
      }
    }).catch(() => setBatches([]));
  };

  useEffect(() => {
    fetchBatches();
  }, []);

  const handleAddBatch = (batch: any) => {
    api.createBatch(batch)
      .then(() => {
        alert('Batch added successfully');
        fetchBatches();
        setModalOpen(false);
      })
      .catch(err => {
        console.error(err);
        alert('Failed to add batch');
      });
  };

  return (
    <Box>
      <Typography variant="h6">Batches (for first product)</Typography>
      <Button sx={{ mb: 2 }} variant="contained" onClick={() => setModalOpen(true)}>Add Batch</Button>
      <AddBatchModal
        open={isModalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleAddBatch}
      />
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Batch No</TableCell>
            <TableCell>Qty Available</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {batches.map(b => (
            <TableRow key={b.b_id}>
              <TableCell>{b.b_id}</TableCell>
              <TableCell>{b.batch_no}</TableCell>
              <TableCell>{b.qty_available}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
