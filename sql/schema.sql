IF DB_ID('fleetfix') IS NULL CREATE DATABASE fleetfix;
GO
USE fleetfix;
GO

CREATE TABLE customers (
    id          INT IDENTITY PRIMARY KEY,
    name        NVARCHAR(200) NOT NULL,
    email       NVARCHAR(200),
    created_at  DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE vehicles (
    id           INT IDENTITY PRIMARY KEY,
    customer_id  INT NOT NULL REFERENCES customers(id),
    plate        NVARCHAR(20),
    vehicle_type NVARCHAR(50),
    model_year   INT
);

CREATE TABLE work_orders (
    id              INT IDENTITY PRIMARY KEY,
    vehicle_id      INT NOT NULL REFERENCES vehicles(id),
    raw_text        NVARCHAR(MAX),
    clean_text      NVARCHAR(MAX),
    source_language NVARCHAR(10),
    status          NVARCHAR(20) DEFAULT 'pending',
    created_at      DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE invoices (
    id            INT IDENTITY PRIMARY KEY,
    work_order_id INT REFERENCES work_orders(id),
    total         DECIMAL(12,2),
    currency      NVARCHAR(3) DEFAULT 'CAD',
    generated_at  DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE invoice_lines (
    id          INT IDENTITY PRIMARY KEY,
    invoice_id  INT NOT NULL REFERENCES invoices(id),
    description NVARCHAR(500),
    quantity    DECIMAL(10,2),
    unit_price  DECIMAL(12,2)
);

CREATE TABLE suppliers (
    id    INT IDENTITY PRIMARY KEY,
    name  NVARCHAR(200) NOT NULL
);

CREATE TABLE supplier_invoices (
    id             INT IDENTITY PRIMARY KEY,
    supplier_id    INT REFERENCES suppliers(id),
    invoice_number NVARCHAR(50),
    invoice_date   DATE,
    total          DECIMAL(12,2),
    source_file    NVARCHAR(300),
    extracted_at   DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE supplier_invoice_lines (
    id                  INT IDENTITY PRIMARY KEY,
    supplier_invoice_id INT NOT NULL REFERENCES supplier_invoices(id),
    description         NVARCHAR(500),
    quantity            DECIMAL(10,2),
    unit_price          DECIMAL(12,2)
);
GO