import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Table, TableBody, TableCell, TableHead, TableRow, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import api from '../../services/api';
import AddEmployeeModal from '../../components/admin/AddEmployeeModal';

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [isModalOpen, setModalOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<any>(null);

  const fetchEmployees = () => {
    api.getEmployees().then(r => setEmployees(r.data)).catch(() => setEmployees([]));
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleAddEmployee = (employee: any) => {
    api.createEmployee(employee)
      .then(() => {
        alert('Employee added successfully');
        fetchEmployees();
        setModalOpen(false);
      })
      .catch(err => {
        console.error(err);
        alert('Failed to add employee');
      });
  };

  const handleEditEmployee = (employee: any) => {
    setEditingEmployee(employee);
    setModalOpen(true);
  };

  const handleUpdateEmployee = (employee: any) => {
    // For now, we'll use the same create endpoint
    // In a real app, you'd have an update endpoint
    api.createEmployee(employee)
      .then(() => {
        alert('Employee updated successfully');
        fetchEmployees();
        setModalOpen(false);
        setEditingEmployee(null);
      })
      .catch(err => {
        console.error(err);
        alert('Failed to update employee');
      });
  };

  const handleDeleteEmployee = (id: number) => {
    api.deleteEmployee(id)
      .then(() => {
        alert('Employee deleted successfully');
        fetchEmployees();
      })
      .catch(err => {
        console.error(err);
        alert('Failed to delete employee');
      });
  };

  return (
    <Box>
      <Typography variant="h6">Employees</Typography>
      <Button sx={{ mb: 2 }} variant="contained" onClick={() => setModalOpen(true)}>Add Employee</Button>
      <AddEmployeeModal
        open={isModalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingEmployee(null);
        }}
        onSubmit={editingEmployee ? handleUpdateEmployee : handleAddEmployee}
        editingEmployee={editingEmployee}
      />
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Role</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {employees.map(e => (
            <TableRow key={e.e_id}>
              <TableCell>{e.e_id}</TableCell>
              <TableCell>{e.name}</TableCell>
              <TableCell>{e.role}</TableCell>
              <TableCell>
                <IconButton onClick={() => handleEditEmployee(e)} aria-label="edit" sx={{ mr: 1 }}>
                  <EditIcon />
                </IconButton>
                <IconButton onClick={() => handleDeleteEmployee(e.e_id)} aria-label="delete">
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
