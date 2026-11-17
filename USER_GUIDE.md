# Pharmacy Management System - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Customer Portal Guide](#customer-portal-guide)
3. [Admin Portal Guide](#admin-portal-guide)
4. [Troubleshooting](#troubleshooting)
5. [Quick Reference](#quick-reference)

## Getting Started

### Accessing the Application
1. Ensure the Flask server is running: `python app.py`
2. Open your web browser
3. Navigate to: `http://localhost:5000`

### Landing Page
The landing page presents two login options:
- **Sign in as Customer**: For patients/customers to view and manage prescriptions
- **Sign in as Admin**: For pharmacy staff to manage operations

---

## Customer Portal Guide

### Logging In
1. Click "Sign in as Customer" on the landing page
2. Enter your Customer ID and password
3. Click "Sign In"

The demo data has customers 1-8, all with the password `password123`.

### Customer Dashboard

After logging in, you'll see two main options:

#### 1. View Prescriptions
- **Purpose**: View all your prescriptions
- **Features**:
  - List of all prescriptions with doctor details
  - Prescription date and validity period
  - Hospital information
  - Status indicators (valid/expired)

#### 2. Add Prescription
- **Purpose**: Submit a new prescription
- **Steps**:
  1. Enter doctor information (ID and license number)
  2. Set prescription date and validity
  3. Enter hospital name
  4. Add medicine items:
     - Select medicine from dropdown
     - Enter dosage (e.g., "1 tablet 2 times daily")
     - Enter duration (e.g., "7 days")
     - Specify quantity needed
     - Add special instructions (optional)
  5. Click "Add Item" to add more medicines
  6. Click "Save Prescription" to submit

### Viewing Prescription Items
1. From "My Prescriptions", click "View Items" on any prescription
2. See detailed information:
   - Medicine name and brand
   - Form and strength
   - Dosage instructions
   - Duration of treatment
   - Quantity prescribed
   - Special instructions

---

## Admin Portal Guide

### Logging In
1. Click "Sign in as Admin" on the landing page
2. Enter credentials:
   - **Username**: admin
   - **Password**: admin123
3. Click "Sign In"

### Admin Dashboard

The admin dashboard provides access to five main management areas:

---

### 1. Employee Management

#### Viewing Employees
- Shows list of all employees with:
  - Employee ID
  - Name
  - Salary
  - Work shift
  - Role
  - Years of experience

#### Adding an Employee
1. Click "Add Employee"
2. Fill in the form:
   - **Full Name**: Employee's complete name
   - **Salary**: Annual or monthly salary
   - **Work Shift**: Select from Morning, Evening, Night, or Full Day
   - **Role**: Choose from:
     - Pharmacist
     - Assistant Pharmacist
     - Store Manager
     - Sales Associate
     - Inventory Clerk
     - Cashier
     - Manager
   - **Experience**: Total years of experience
3. Click "Add Employee"

#### Editing an Employee
1. Click "Edit" button next to employee
2. Modify required fields
3. Click "Update Employee"

#### Deleting an Employee
1. Click "Delete" button
2. Confirm deletion in modal dialog
3. Employee will be permanently removed

---

### 2. Product Management

#### Viewing Products
- Shows inventory with:
  - Product ID
  - Medicine name and brand
  - Form (Tablet, Syrup, etc.) and strength
  - Prescription type (OTC or Prescription)
  - MRP and Unit Price

#### Adding a Product
1. Click "Add Product"
2. Fill in details:
   - **Brand Name**: Commercial name (e.g., "Tylenol")
   - **Medicine Name**: Generic name (e.g., "Paracetamol")
   - **Form**: Select type (Tablet, Capsule, Syrup, etc.)
   - **Strength**: Dosage strength (e.g., "500mg")
   - **Packing**: Package description (e.g., "Strip of 10")
   - **Prescription Type**:
     - OTC: Can be sold without prescription
     - Prescription: Requires doctor's prescription
   - **MRP**: Maximum Retail Price
   - **Unit Price**: Selling price (should be ≤ MRP)
3. Click "Add Product"

#### Editing a Product
1. Click "Edit" next to product
2. Update necessary fields
3. Click "Update Product"

#### Deleting a Product
1. Click "Delete"
2. Confirm deletion
3. Product will be removed (affects related records)

---

### 3. Customer Management

#### Viewing Customers
- Displays all registered customers with:
  - Customer ID
  - Name and contact information
  - Age and gender
  - Number of prescriptions

#### Adding a Customer
1. Click "Add Customer"
2. Enter information:
   - **Full Name**: Customer's complete name
   - **Phone Number**: Contact number (e.g., "+1-234-567-8900")
   - **Address**: Complete address with street, city, zip
   - **Age**: Customer's age
   - **Gender**: Select Male, Female, or Other
3. Click "Add Customer"
4. Customer ID will be auto-generated
5. Give the customer their Customer ID and the portal password you set

---

### 4. Sales Reports

#### Viewing Sales by Products
- Shows sales aggregated by products:
  - Brand and medicine names
  - Associated supplier
  - Total quantity sold
  - Total sales amount
  - Grand totals at bottom

**Use Case**: Track which products are selling and from which suppliers

---

### 5. Reports

The Reports section provides four comprehensive views:

#### A. Current Stock Summary
- **Purpose**: Monitor inventory levels
- **Information**:
  - All products with available quantities
  - Stock status indicators:
    - 🔴 Red badge: Low stock (<10 units)
    - 🟡 Yellow badge: Medium stock (10-50 units)
    - 🟢 Green badge: Good stock (>50 units)
  - Nearest expiry date for each product

#### B. Near Expiry Items (Within 30 Days)
- **Purpose**: Prevent stock wastage
- **Features**:
  - Lists all items expiring soon
  - Shows batch numbers
  - Displays days until expiry
  - Priority levels:
    - **Critical**: ≤7 days (Red)
    - **Warning**: 8-15 days (Yellow)
    - **Monitor**: 16-30 days (Blue)
- **Action**: Plan promotions or discounts for near-expiry items

#### C. Top Selling Medicines (Top 10)
- **Purpose**: Identify popular products
- **Features**:
  - Ranked list with medals (🥇🥈🥉)
  - Visual performance bars
  - Percentage comparison to top seller
- **Use Case**: Stock planning and inventory optimization

#### D. Batch → Sale → Prescription Traceability
- **Purpose**: Regulatory compliance
- **Information**:
  - Complete traceability chain visualization
  - Links batches to sales to prescriptions
  - Ensures pharmaceutical compliance
  - Enables quick recall procedures if needed

---

## Troubleshooting

### Common Issues and Solutions

#### Cannot Login as Customer
**Issue**: "Customer ID or password is incorrect"  
**Solution**:
- Check the Customer ID printed on your bill
- Customers added without a portal password cannot sign in. Ask the pharmacy to set one.

#### Cannot Login as Admin
**Issue**: "Username or password is incorrect"  
**Solution**:
- Default credentials:
  - Username: `admin`
  - Password: `admin123`
- Check for typing errors
- Ensure Caps Lock is off

#### Application Not Loading
**Issue**: Server not responding  
**Solution**:
1. Check if Flask server is running
2. Restart server: `python app.py`
3. Verify port 5000 is not in use
4. Check terminal for error messages

#### Database Errors
**Issue**: Database connection errors  
**Solution**:
1. Stop the server (Ctrl+C)
2. Run `python seed_data.py` to reset `instance/pharmacy.db` with demo data
3. Restart: `python app.py`

#### Missing or Incorrect Data
**Issue**: Expected data not showing  
**Solution**:
- Check if database was properly seeded
- Re-run seed script if needed
- Verify form inputs are correct
- Check console for error messages

#### Form Submission Fails
**Issue**: Form doesn't submit  
**Solution**:
- Ensure all required fields are filled
- Check for validation errors (red borders)
- Verify data types (numbers for age, price, etc.)
- Check browser console for JavaScript errors

#### Pages Not Loading Properly
**Issue**: Styling or layout issues  
**Solution**:
- Clear browser cache (Ctrl+Shift+R)
- Check if CSS and JS files are loading
- Verify internet connection (for Bootstrap CDN)
- Try a different browser

### Getting Help

If you encounter persistent issues:
1. Check the terminal output for error messages
2. Review the `app.py` logs
4. Reinstall dependencies: `pip install -r requirements.txt`
5. Use Python 3.10 or newer

---

## Quick Reference

### Login Credentials (Demo)
- **Admin**: admin / admin123
- **Customers**: IDs 1-8 / password123

### Common Actions
- **Add Data**: Use green "Add" buttons
- **Edit Data**: Yellow "Edit" button
- **Delete Data**: Red "Delete" button (with confirmation)
- **View Details**: Blue "View" button
- **Return**: Grey "Back" button

### Navigation
- Click logo/title to return to landing page
- Use "Back to Dashboard" to return to main menu
- Use "Logout" in top-right to sign out
