import React, { useState, useEffect } from 'react';
import apiClient from '../../services/api';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';

interface Employee {
  e_id: number;
  name: string;
  salary: number;
  work_shift: string;
  role: string;
  experience: number;
}

const EmployeeManagement = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    salary: '',
    work_shift: '',
    role: '',
    experience: '',
  });

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const res = await apiClient.getEmployees();
      setEmployees(res.data);
    } catch (error) {
      console.error('Failed to fetch employees:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this employee?')) return;
    try {
      await apiClient.deleteEmployee(id);
      setEmployees(employees.filter((e) => e.e_id !== id));
    } catch (error) {
      alert('Failed to delete employee');
    }
  };

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleSubmit = async () => {
    try {
      const payload = {
        ...formData,
        salary: parseFloat(formData.salary),
        experience: parseInt(formData.experience),
      };
      await apiClient.createEmployee(payload);
      fetchEmployees();
      handleClose();
      setFormData({ name: '', salary: '', work_shift: '', role: '', experience: '' });
    } catch (error) {
      alert('Failed to add employee');
    }
  };

  return (
    <>
      <Button variant="contained" color="primary" onClick={handleOpen} sx={{ mb: 2 }}>
        Add Employee
      </Button>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Salary</TableCell>
              <TableCell>Work Shift</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Experience</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {employees.map((employee) => (
              <TableRow key={employee.e_id}>
                <TableCell>{employee.e_id}</TableCell>
                <TableCell>{employee.name}</TableCell>
                <TableCell>{employee.salary}</TableCell>
                <TableCell>{employee.work_shift}</TableCell>
                <TableCell>{employee.role}</TableCell>
                <TableCell>{employee.experience}</TableCell>
                <TableCell>
                  <Button size="small" color="primary">
                    Edit
                  </Button>
                  <Button size="small" color="error" onClick={() => handleDelete(employee.e_id)}>
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add New Employee</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Salary"
            type="number"
            value={formData.salary}
            onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Work Shift"
            value={formData.work_shift}
            onChange={(e) => setFormData({ ...formData, work_shift: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Role"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Experience (years)"
            type="number"
            value={formData.experience}
            onChange={(e) => setFormData({ ...formData, experience: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} color="primary">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default EmployeeManagement;