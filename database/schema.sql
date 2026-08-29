-- QueryOpt AI Demo Database Schema
-- SQLite schema for the demo/analysis target database

PRAGMA foreign_keys = ON;

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    budget        REAL NOT NULL DEFAULT 0.0,
    location      TEXT NOT NULL
);

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    country       TEXT NOT NULL,
    contact_email TEXT
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    city        TEXT NOT NULL,
    country     TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    category         TEXT NOT NULL,
    price            REAL NOT NULL DEFAULT 0.0,
    stock_quantity   INTEGER NOT NULL DEFAULT 0,
    supplier_id      INTEGER NOT NULL REFERENCES suppliers(supplier_id)
);

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    employee_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    manager_id    INTEGER REFERENCES employees(employee_id),
    salary        REAL NOT NULL DEFAULT 0.0,
    join_date     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date    TEXT NOT NULL,
    status        TEXT NOT NULL CHECK(status IN ('pending','shipped','delivered','cancelled')),
    total_amount  REAL NOT NULL DEFAULT 0.0,
    shipping_city TEXT NOT NULL
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    item_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity   INTEGER NOT NULL DEFAULT 1,
    unit_price REAL NOT NULL DEFAULT 0.0
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer_id   ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date          ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_employees_dept       ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_products_category    ON products(category);
