IF DB_ID('fleetfix') IS NULL CREATE DATABASE fleetfix;
GO
USE fleetfix;
GO

CREATE TABLE clientes (
    id          INT IDENTITY PRIMARY KEY,
    nombre      NVARCHAR(200) NOT NULL,
    email       NVARCHAR(200),
    creado_en   DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE vehiculos (
    id          INT IDENTITY PRIMARY KEY,
    cliente_id  INT NOT NULL REFERENCES clientes(id),
    placa       NVARCHAR(20),
    tipo        NVARCHAR(50),
    anio        INT
);

CREATE TABLE ordenes_trabajo (
    id            INT IDENTITY PRIMARY KEY,
    vehiculo_id   INT NOT NULL REFERENCES vehiculos(id),
    texto_crudo   NVARCHAR(MAX),
    texto_limpio  NVARCHAR(MAX),
    idioma_origen NVARCHAR(10),
    estado        NVARCHAR(20) DEFAULT 'pendiente',
    creado_en     DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE facturas (
    id          INT IDENTITY PRIMARY KEY,
    orden_id    INT REFERENCES ordenes_trabajo(id),
    total       DECIMAL(12,2),
    moneda      NVARCHAR(3) DEFAULT 'CAD',
    generada_en DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE factura_lineas (
    id              INT IDENTITY PRIMARY KEY,
    factura_id      INT NOT NULL REFERENCES facturas(id),
    descripcion     NVARCHAR(500),
    cantidad        DECIMAL(10,2),
    precio_unitario DECIMAL(12,2)
);

CREATE TABLE proveedores (
    id      INT IDENTITY PRIMARY KEY,
    nombre  NVARCHAR(200) NOT NULL
);

CREATE TABLE facturas_proveedor (
    id             INT IDENTITY PRIMARY KEY,
    proveedor_id   INT REFERENCES proveedores(id),
    numero         NVARCHAR(50),
    fecha          DATE,
    total          DECIMAL(12,2),
    archivo_origen NVARCHAR(300),
    extraido_en    DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE proveedor_lineas (
    id                   INT IDENTITY PRIMARY KEY,
    factura_proveedor_id INT NOT NULL REFERENCES facturas_proveedor(id),
    descripcion          NVARCHAR(500),
    cantidad             DECIMAL(10,2),
    precio_unitario      DECIMAL(12,2)
);
GO