# 📊 Sales Intelligence Hub

A branch-based sales management and financial analytics system built using *Python, MySQL, and Streamlit*.

The application helps businesses manage customer sales, track split payments, monitor pending amounts, and analyze sales performance across branches.

---

## 🚀 Project Overview

Sales Intelligence Hub is designed to provide a centralized platform for:

- Branch-wise sales management
- Customer and product tracking
- Payment collection
- Split payment management
- Automatic pending amount calculation
- Automatic payment status updates
- Role-based access control
- Sales analytics and reporting
- Financial performance monitoring

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web application and dashboard |
| MySQL | Relational database |
| SQL | Data management and analytics |
| Pandas | Data processing and reporting |
| MySQL Connector | Python-MySQL connectivity |
| VS Code | Development environment |

---

## ✨ Key Features

### 🔐 Role-Based Login

The application supports two roles:

- *Super Admin* – Access to all branches
- *Admin* – Access restricted to the assigned branch

---

### 🛒 Sales Management

Admins can record:

- Customer name
- Mobile number
- Product
- Gross sales
- Branch
- Sale date

Supported products:

- DS
- DA
- BA
- FSD

---

### 💰 Payment Management

The system supports multiple payment methods:

- Cash
- UPI
- Card
- Bank Transfer

Split payments are supported for a single sale.

For example:

```text
Gross Sale       ₹8,000
First Payment    ₹3,000
Pending          ₹5,000

Second Payment   ₹5,000
Pending          ₹0
Status           Close