import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import api from '../../services/api';
import AddPurchaseModal from '../../components/admin/AddPurchaseModal';

export default function PurchasesPage() {
  const [purchases, setPurchases] = useState<any[]>([]);
  const [isModalOpen, setModalOpen] = useState(false);

  const fetchPurchases = () => {
    api.getPurchases().then(r => setPurchases(r.data)).catch(() => setPurchases([]));
  };

  useEffect(() => { fetchPurchases(); }, []);

  const handleAddPurchase = (purchase: any) => {
    api.createPurchase(purchase)
      .then(() => { alert('Purchase recorded'); setModalOpen(false); fetchPurchases(); })
      .catch(err => { console.error(err); alert('Failed to record purchase'); });
  };

  return (
    <Box>
      <Typography variant="h6">Purchases</Typography>
      <Button sx={{ mb: 2 }} variant="contained" onClick={() => setModalOpen(true)}>Add Purchase</Button>
      <AddPurchaseModal open={isModalOpen} onClose={() => setModalOpen(false)} onSubmit={handleAddPurchase} />
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Product ID</TableCell>
            <TableCell>Supplier ID</TableCell>
            <TableCell>Date</TableCell>
            <TableCell>Cost</TableCell>
            <TableCell>Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {purchases.map(p => (
            <TableRow key={p.purchase_id}>
              <TableCell>{p.purchase_id}</TableCell>
              <TableCell>{p.p_id}</TableCell>
              <TableCell>{p.s_id}</TableCell>
              <TableCell>{new Date(p.date).toLocaleDateString()}</TableCell>
              <TableCell>{p.cost}</TableCell>
              <TableCell>{p.status}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
