import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, Button, TextField, Select, MenuItem } from '@mui/material';
import api from '../../services/api';

interface CartItem {
  p_id: number;
  b_id: number;
  qty: number;
  price: number;
}

export default function CheckoutPage() {
  const [search] = useSearchParams();
  const navigate = useNavigate();
  const c_id = Number(search.get('c_id') || 0);

  const [products, setProducts] = useState<any[]>([]);
  const [batchesByProduct, setBatchesByProduct] = useState<Record<number, any[]>>({});
  const [cart, setCart] = useState<CartItem[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<number | ''>('');
  const [selectedBatch, setSelectedBatch] = useState<number | ''>('');
  const [qty, setQty] = useState<number>(1);

  useEffect(() => {
    api.getProducts().then(r => { setProducts(r.data); }).catch(() => setProducts([]));
  }, []);

  const loadBatches = (p_id: number) => {
    api.getProductBatches(p_id).then(r => setBatchesByProduct(prev => ({ ...prev, [p_id]: r.data }))).catch(() => setBatchesByProduct(prev => ({ ...prev, [p_id]: [] })));
  };

  const addToCart = () => {
    if (!selectedProduct || !selectedBatch || qty <= 0) return alert('Select product, batch and qty');
    const product = products.find(p => p.p_id === Number(selectedProduct));
    const batchList = batchesByProduct[Number(selectedProduct)] || [];
    const batch = batchList.find((b: any) => b.b_id === Number(selectedBatch));
    if (!batch) return alert('Invalid batch');
    if (batch.qty_available < qty) return alert('Insufficient qty in batch');

    const item: CartItem = {
      p_id: Number(selectedProduct),
      b_id: Number(selectedBatch),
      qty,
      price: product ? product.unit_price || product.mrp || 0 : 0,
    };
    setCart(prev => [...prev, item]);
  };

  const removeFromCart = (index: number) => setCart(prev => prev.filter((_, i) => i !== index));

  const computeTotals = () => {
    const amount = cart.reduce((s, it) => s + it.price * it.qty, 0);
    const tax = amount * 0.05; // 5% example
    const discount = 0;
    const total = amount + tax - discount;
    return { amount, tax, discount, total };
  };

  const submitSale = async () => {
    if (!c_id) return alert('Missing customer id in query string');
    if (cart.length === 0) return alert('Cart is empty');

    const { amount, tax, discount, total } = computeTotals();
    const salePayload = {
      c_id,
      e_id: 1, // default employee id — you may change to logged in employee
      pres_id: 0,
      sale_date: new Date().toISOString().split('T')[0],
      payment_mode: 'cash',
      amount,
      tax,
      discount,
      total,
      status: 'completed',
      items: cart.map((it, idx) => ({ p_id: it.p_id, b_id: it.b_id, qty: it.qty, price: it.price, line_total: it.price * it.qty, line_discount: 0 })),
    };

    try {
      await api.createSale(salePayload);
      alert('Sale created');
      navigate(`/customer-dashboard?c_id=${c_id}`);
    } catch (e: any) {
      alert(e?.response?.data?.detail || e.message || 'Error creating sale');
    }
  };

  return (
    <Box>
      <Typography variant="h5">Checkout</Typography>
      <Typography sx={{ mb: 2 }}>Customer ID: {c_id}</Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Select value={selectedProduct} displayEmpty onChange={(e) => { setSelectedProduct(Number(e.target.value)); setSelectedBatch(''); loadBatches(Number(e.target.value)); }} sx={{ minWidth: 240 }}>
          <MenuItem value="">Select product</MenuItem>
          {products.map(p => <MenuItem key={p.p_id} value={p.p_id}>{p.brand_name} - {p.medicine_name}</MenuItem>)}
        </Select>

        <Select value={selectedBatch} displayEmpty onChange={(e) => setSelectedBatch(Number(e.target.value))} sx={{ minWidth: 200 }}>
          <MenuItem value="">Select batch</MenuItem>
          {(batchesByProduct[Number(selectedProduct)] || []).map((b: any) => <MenuItem key={b.b_id} value={b.b_id}>{b.batch_no} (avail: {b.qty_available})</MenuItem>)}
        </Select>

        <TextField type="number" label="Qty" value={qty} onChange={(e) => setQty(Number(e.target.value))} sx={{ width: 100 }} />
        <Button variant="contained" onClick={addToCart}>Add</Button>
      </Box>

      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Product</TableCell>
            <TableCell>Batch</TableCell>
            <TableCell>Qty</TableCell>
            <TableCell>Price</TableCell>
            <TableCell>Line Total</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {cart.map((it, idx) => {
            const prod = products.find(p => p.p_id === it.p_id);
            const batch = (batchesByProduct[it.p_id] || []).find(b => b.b_id === it.b_id) || {};
            return (
              <TableRow key={idx}>
                <TableCell>{prod ? `${prod.brand_name} ${prod.medicine_name}` : it.p_id}</TableCell>
                <TableCell>{batch.batch_no || it.b_id}</TableCell>
                <TableCell>{it.qty}</TableCell>
                <TableCell>{it.price}</TableCell>
                <TableCell>{it.price * it.qty}</TableCell>
                <TableCell><Button onClick={() => removeFromCart(idx)}>Remove</Button></TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <Box sx={{ mt: 2 }}>
        <Typography>Amount: {computeTotals().amount.toFixed(2)}</Typography>
        <Typography>Tax: {computeTotals().tax.toFixed(2)}</Typography>
        <Typography>Total: {computeTotals().total.toFixed(2)}</Typography>
      </Box>

      <Box sx={{ mt: 2 }}>
        <Button variant="contained" color="primary" onClick={submitSale}>Submit Sale</Button>
      </Box>
    </Box>
  );
}
