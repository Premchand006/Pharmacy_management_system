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

interface AddEmployeeModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (employee: any) => void;
  editingEmployee?: any;
}

export default function AddEmployeeModal({ open, onClose, onSubmit, editingEmployee }: AddEmployeeModalProps) {
  const [employee, setEmployee] = useState({
    name: '',
    salary: 0,
    work_shift: '',
    role: '',
    experience: 0,
  });

  useEffect(() => {
    if (editingEmployee) {
      setEmployee({
        name: editingEmployee.name || '',
        salary: editingEmployee.salary || 0,
        work_shift: editingEmployee.work_shift || '',
        role: editingEmployee.role || '',
        experience: editingEmployee.experience || 0,
      });
    } else {
      setEmployee({
        name: '',
        salary: 0,
        work_shift: '',
        role: '',
        experience: 0,
      });
    }
  }, [editingEmployee, open]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEmployee(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    onSubmit(employee);
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="add-employee-modal-title"
    >
      <Box sx={style}>
        <Typography id="add-employee-modal-title" variant="h6" component="h2">
          {editingEmployee ? 'Edit Employee' : 'Add New Employee'}
        </Typography>
        <TextField margin="dense" name="name" label="Name" fullWidth value={employee.name} onChange={handleChange} />
        <TextField margin="dense" name="salary" label="Salary" type="number" fullWidth value={employee.salary} onChange={handleChange} />
        <TextField margin="dense" name="work_shift" label="Work Shift" fullWidth value={employee.work_shift} onChange={handleChange} />
        <TextField margin="dense" name="role" label="Role" fullWidth value={employee.role} onChange={handleChange} />
        <TextField margin="dense" name="experience" label="Experience (years)" type="number" fullWidth value={employee.experience} onChange={handleChange} />
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" sx={{ ml: 1 }}>
            {editingEmployee ? 'Update' : 'Add'}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
}
