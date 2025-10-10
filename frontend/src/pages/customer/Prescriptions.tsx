import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, Button, TextField } from '@mui/material';
import api from '../../services/api';
import { useSearchParams, useNavigate } from 'react-router-dom';

export default function PrescriptionsPage() {
  const [search] = useSearchParams();
  const c_id = Number(search.get('c_id') || 0);
  const action = search.get('action');
  const [prescriptions, setPrescriptions] = useState<any[]>([]);
  const [showItemsFor, setShowItemsFor] = useState<number | null>(null);
  
  // Add form state
  const [adding, setAdding] = useState(action === 'add');
  const [form, setForm] = useState<any>({ dr_id: '', doctor_license_no: '', hospital_name: '', validity: 30, date: new Date().toISOString().slice(0,10), items: [] });

  const navigate = useNavigate();

  useEffect(() => {
    if (c_id) api.getCustomerPrescriptions(c_id).then(r => setPrescriptions(r.data)).catch(() => setPrescriptions([]));
  }, [c_id]);

  const handleAdd = async () => {
    try {
      const payload = { ...form, c_id, items: form.items };
      await api.createPrescription(payload);
      alert('Prescription added');
      setAdding(false);
      const r = await api.getCustomerPrescriptions(c_id);
      setPrescriptions(r.data);
      setForm({ dr_id: '', doctor_license_no: '', hospital_name: '', validity: 30, date: new Date().toISOString().slice(0,10), items: [] });
    } catch (e: any) { alert(e.response?.data?.detail || e.message || 'Error'); }
  };

  const addItemToForm = () => {
    setForm((f: any) => ({ ...f, items: [...(f.items||[]), { product_id: 0, dosage: '', duration: '', qty: 1, instructions: '' }] }));
  };

  const updateItem = (idx: number, key: string, value: any) => {
    setForm((f: any) => {
      const items = [...(f.items||[])];
      items[idx] = { ...items[idx], [key]: value };
      return { ...f, items };
    });
  };

  const viewItemsFromPrescription = (pres: any) => {
    // use relationship-loaded items if available
    if (pres.items && pres.items.length) {
      setShowItemsFor(pres.pres_id);
      return;
    }
    // fallback: ask backend for items (optional endpoint)
    setShowItemsFor(pres.pres_id);
  };

  return (
    <Box>
      <Typography variant="h6">Prescriptions</Typography>
      <Table>
        <TableHead>
          <TableRow><TableCell>ID</TableCell><TableCell>Date</TableCell><TableCell>Hospital</TableCell></TableRow>
        </TableHead>
        <TableBody>
          {prescriptions.map(p => (
            <TableRow key={p.pres_id}>
              <TableCell>{p.pres_id}</TableCell>
              <TableCell>{p.date}</TableCell>
              <TableCell>{p.hospital_name}</TableCell>
              <TableCell>
                <Button size="small" onClick={() => viewItemsFromPrescription(p)}>View Items</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {showItemsFor && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle1">Items for Prescription {showItemsFor}</Typography>
          <Table>
            <TableHead>
              <TableRow><TableCell>Line</TableCell><TableCell>Product ID</TableCell><TableCell>Medicine Name</TableCell><TableCell>Qty</TableCell><TableCell>Dosage</TableCell><TableCell>Duration</TableCell><TableCell>Instructions</TableCell></TableRow>
            </TableHead>
            <TableBody>
              {(() => {
                const pres = prescriptions.find(p => p.pres_id === showItemsFor);
                const items = pres?.items || [];
                if (!items.length) return <TableRow><TableCell colSpan={7}>No items available</TableCell></TableRow>;
                return items.map((it:any, i:number) => (
                  <TableRow key={i}>
                    <TableCell>{it.line_no || i+1}</TableCell>
                    <TableCell>{it.product_id}</TableCell>
                    <TableCell>{it.medicine_name || 'Loading...'}</TableCell>
                    <TableCell>{it.qty}</TableCell>
                    <TableCell>{it.dosage}</TableCell>
                    <TableCell>{it.duration}</TableCell>
                    <TableCell>{it.instructions}</TableCell>
                  </TableRow>
                ));
              })()}
            </TableBody>
          </Table>
        </Box>
      )}

      {!adding ? (
            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button variant="contained" onClick={() => setAdding(true)}>Add Prescription</Button>
              <Button variant="outlined" onClick={() => navigate(`/customer/checkout?c_id=${c_id}`)}>Checkout (open cart)</Button>
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              <TextField label="Doctor ID" fullWidth sx={{ mb: 1 }} value={form.dr_id} onChange={e => setForm({ ...form, dr_id: e.target.value })} />
              <TextField label="Doctor License No" fullWidth sx={{ mb: 1 }} value={form.doctor_license_no} onChange={e => setForm({ ...form, doctor_license_no: e.target.value })} />
              <TextField label="Hospital Name" fullWidth sx={{ mb: 1 }} value={form.hospital_name} onChange={e => setForm({ ...form, hospital_name: e.target.value })} />
              <Button variant="outlined" onClick={addItemToForm} sx={{ mb: 1 }}>Add Item</Button>
              {form.items.map((it:any, idx:number) => (
                <Box key={idx} sx={{ mb: 1, p:1, border: '1px solid #ddd' }}>
                  <TextField label="Product ID" type="number" value={it.product_id} onChange={e => updateItem(idx, 'product_id', Number(e.target.value))} sx={{ mr:1 }} />
                  <TextField label="Qty" type="number" value={it.qty} onChange={e => updateItem(idx, 'qty', Number(e.target.value))} sx={{ mr:1 }} />
                  <TextField label="Dosage" value={it.dosage} onChange={e => updateItem(idx, 'dosage', e.target.value)} sx={{ mr:1 }} />
                  <TextField label="Duration" value={it.duration} onChange={e => updateItem(idx, 'duration', e.target.value)} sx={{ mr:1 }} />
                  <TextField label="Instructions" value={it.instructions} onChange={e => updateItem(idx, 'instructions', e.target.value)} sx={{ mr:1 }} />
                </Box>
              ))}
              <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                <Button variant="contained" onClick={handleAdd}>Submit Prescription</Button>
                <Button variant="text" onClick={() => setAdding(false)}>Cancel</Button>
              </Box>
            </Box>
          )}
    </Box>
  );
}
