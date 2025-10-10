import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import api from '../../services/api';

export default function SalesPage() {
  const [sales, setSales] = useState<any[]>([]);
  useEffect(() => { api.getSales().then(r => setSales(r.data)).catch(() => setSales([])); }, []);

  return (
    <Box>
      <Typography variant="h6">Sales</Typography>
      <Table>
        <TableHead>
          <TableRow><TableCell>ID</TableCell><TableCell>Customer</TableCell><TableCell>Total</TableCell></TableRow>
        </TableHead>
        <TableBody>
          {sales.map(s => (
            <TableRow key={s.sb_id}><TableCell>{s.sb_id}</TableCell><TableCell>{s.c_id}</TableCell><TableCell>{s.total}</TableCell></TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
