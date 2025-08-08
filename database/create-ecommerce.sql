-- ========================================
-- SCRIPT SQL ADAPTADO PARA SQLITE3
-- Sistema E-commerce - Base de Datos
-- ========================================

-- Habilitar claves foráneas en SQLite3
PRAGMA foreign_keys = ON;

-- ========================================
-- CREAR TABLAS
-- ========================================

-- Tabla de Países
CREATE TABLE Country (
    iD_Country INTEGER PRIMARY KEY AUTOINCREMENT,
    CountryName TEXT NOT NULL
);

-- Tabla de Estados/Departamentos
CREATE TABLE States (
    iD_States INTEGER PRIMARY KEY AUTOINCREMENT,
    StatesName TEXT NOT NULL,
    iD_Country INTEGER NOT NULL,
    FOREIGN KEY (iD_Country) REFERENCES Country(iD_Country)
);

-- Tabla de Ciudades
CREATE TABLE City (
    iD_City INTEGER PRIMARY KEY AUTOINCREMENT,
    CityName TEXT NOT NULL,
    iD_States INTEGER NOT NULL,
    FOREIGN KEY (iD_States) REFERENCES States(iD_States)
);

-- Tabla de Usuarios
CREATE TABLE Users (
    iD_User INTEGER PRIMARY KEY AUTOINCREMENT,
    UserName TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    PasswoRDkey TEXT NOT NULL,
    iD_City INTEGER,
    FOREIGN KEY (iD_City) REFERENCES City(iD_City)
);

-- Tabla de Roles
CREATE TABLE RoleS (
    iDRole INTEGER PRIMARY KEY AUTOINCREMENT,
    TypeRole TEXT NOT NULL
);

-- Tabla de relación Usuario-Rol (Muchos a Muchos)
CREATE TABLE UserRole (
    idROLE INTEGER NOT NULL,
    iD_Useri INTEGER NOT NULL,
    PRIMARY KEY (idROLE, iD_Useri),
    FOREIGN KEY (idROLE) REFERENCES RoleS(iDRole),
    FOREIGN KEY (iD_Useri) REFERENCES Users(iD_User)
);

-- Tabla de Productos
CREATE TABLE Product (
    id_Product INTEGER PRIMARY KEY AUTOINCREMENT,
    Price REAL NOT NULL,
    ProductName TEXT NOT NULL,
    Stock INTEGER NOT NULL DEFAULT 0
);

-- Tabla de Ventas
CREATE TABLE Sales (
    id_Sale INTEGER PRIMARY KEY AUTOINCREMENT,
    DescripcionSale TEXT,
    iD_User INTEGER NOT NULL,
    DateCreated TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (iD_User) REFERENCES Users(iD_User)
);

-- Tabla de Ventas Temporales (Carrito)
CREATE TABLE TemporalSales (
    id_TemporalSales INTEGER PRIMARY KEY AUTOINCREMENT,
    iD_User INTEGER NOT NULL,
    id_Sale INTEGER,
    id_Product INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    DateAdded TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (iD_User) REFERENCES Users(iD_User),
    FOREIGN KEY (id_Sale) REFERENCES Sales(id_Sale),
    FOREIGN KEY (id_Product) REFERENCES Product(id_Product)
);

-- Tabla de Detalle de Ventas
CREATE TABLE SalesDetail (
    id_SalesDetails INTEGER PRIMARY KEY AUTOINCREMENT,
    id_Product INTEGER NOT NULL,
    id_Sale INTEGER NOT NULL,
    id_TemporalSales INTEGER,
    DateSales TEXT NOT NULL,
    amount INTEGER NOT NULL,
    ValueSale REAL NOT NULL,
    FOREIGN KEY (id_Product) REFERENCES Product(id_Product),
    FOREIGN KEY (id_Sale) REFERENCES Sales(id_Sale),
    FOREIGN KEY (id_TemporalSales) REFERENCES TemporalSales(id_TemporalSales)
);

-- Tabla de Categorías
CREATE TABLE Category (
    id_Category INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryName TEXT NOT NULL
);

-- Tabla de relación Producto-Categoría (Muchos a Muchos)
CREATE TABLE PRODUC_Category (
    id_Category INTEGER NOT NULL,
    id_Product INTEGER NOT NULL,
    PRIMARY KEY (id_Category, id_Product),
    FOREIGN KEY (id_Category) REFERENCES Category(id_Category),
    FOREIGN KEY (id_Product) REFERENCES Product(id_Product)
);

-- Tabla de Imágenes de Productos
CREATE TABLE PRODUC_Image (
    id_image INTEGER PRIMARY KEY AUTOINCREMENT,
    id_Category INTEGER,
    id_Product INTEGER NOT NULL,
    pathimage TEXT NOT NULL,
    alt_text TEXT,
    is_main_image INTEGER DEFAULT 0,
    FOREIGN KEY (id_Category) REFERENCES Category(id_Category),
    FOREIGN KEY (id_Product) REFERENCES Product(id_Product)
);

-- ========================================
-- CREAR ÍNDICES PARA OPTIMIZACIÓN
-- ========================================

CREATE INDEX IX_Users_Email ON Users(Email);
CREATE INDEX IX_Product_Name ON Product(ProductName);
CREATE INDEX IX_Sales_User ON Sales(iD_User);
CREATE INDEX IX_Sales_Date ON Sales(DateCreated);
CREATE INDEX IX_SalesDetail_Sale ON SalesDetail(id_Sale);
CREATE INDEX IX_SalesDetail_Product ON SalesDetail(id_Product);
CREATE INDEX IX_States_Country ON States(iD_Country);
CREATE INDEX IX_City_States ON City(iD_States);
CREATE INDEX IX_Users_City ON Users(iD_City);

-- ========================================
-- INSERTAR DATOS DE EJEMPLO
-- ========================================

-- Insertar países de ejemplo
INSERT INTO Country (CountryName) VALUES 
('Colombia'),
('Estados Unidos'),
('México'),
('Argentina'),
('España');

-- Insertar estados de Colombia
INSERT INTO States (StatesName, iD_Country) VALUES 
('Antioquia', 1),
('Cundinamarca', 1),
('Valle del Cauca', 1),
('Atlántico', 1);

-- Insertar ciudades de Antioquia
INSERT INTO City (CityName, iD_States) VALUES 
('Medellín', 1),
('Bello', 1),
('Envigado', 1),
('Itagüí', 1);

-- Insertar roles de ejemplo
INSERT INTO RoleS (TypeRole) VALUES 
('Administrador'),
('Usuario'),
('Vendedor'),
('Cliente');

-- Insertar categorías de ejemplo
INSERT INTO Category (CategoryName) VALUES 
('Electrónicos'),
('Ropa'),
('Hogar'),
('Deportes'),
('Libros'),
('Tecnología'),
('Alimentación');

-- Insertar usuarios de ejemplo
INSERT INTO Users (UserName, Email, PasswoRDkey, iD_City) VALUES 
('admin', 'admin@ecommerce.com', 'admin123', 1),
('juan_perez', 'juan@email.com', 'password123', 1),
('maria_garcia', 'maria@email.com', 'password456', 2),
('carlos_lopez', 'carlos@email.com', 'password789', 1);

-- Asignar roles a usuarios
INSERT INTO UserRole (idROLE, iD_Useri) VALUES 
(1, 1),  -- admin es Administrador
(4, 2),  -- juan es Cliente
(4, 3),  -- maria es Cliente
(3, 4);  -- carlos es Vendedor

-- Insertar productos de ejemplo
INSERT INTO Product (ProductName, Price, Stock) VALUES 
('iPhone 15 Pro', 999.99, 10),
('Samsung Galaxy S24', 899.99, 15),
('MacBook Air M2', 1199.99, 5),
('Auriculares Sony WH-1000XM5', 299.99, 20),
('Camiseta Nike', 29.99, 50),
('Pantalón Jeans Levis', 79.99, 30),
('Zapatillas Adidas', 89.99, 25),
('Libro "Clean Code"', 39.99, 40),
('Cafetera Nespresso', 199.99, 8),
('Tablet iPad Air', 599.99, 12);

-- Relacionar productos con categorías
INSERT INTO PRODUC_Category (id_Category, id_Product) VALUES 
(1, 1),  -- iPhone es Electrónico
(6, 1),  -- iPhone es Tecnología
(1, 2),  -- Samsung es Electrónico
(6, 2),  -- Samsung es Tecnología
(1, 3),  -- MacBook es Electrónico
(6, 3),  -- MacBook es Tecnología
(1, 4),  -- Auriculares son Electrónicos
(2, 5),  -- Camiseta es Ropa
(2, 6),  -- Pantalón es Ropa
(2, 7),  -- Zapatillas son Ropa
(4, 7),  -- Zapatillas son Deportes
(5, 8),  -- Libro es Libros
(3, 9),  -- Cafetera es Hogar
(1, 10), -- iPad es Electrónico
(6, 10); -- iPad es Tecnología

-- Insertar imágenes de productos de ejemplo
INSERT INTO PRODUC_Image (id_Product, id_Category, pathimage, alt_text, is_main_image) VALUES 
(1, 1, '/images/iphone15_main.jpg', 'iPhone 15 Pro vista frontal', 1),
(1, 1, '/images/iphone15_back.jpg', 'iPhone 15 Pro vista trasera', 0),
(2, 1, '/images/samsung_s24_main.jpg', 'Samsung Galaxy S24 vista frontal', 1),
(3, 1, '/images/macbook_air_main.jpg', 'MacBook Air M2 abierto', 1),
(4, 1, '/images/sony_headphones.jpg', 'Auriculares Sony WH-1000XM5', 1),
(5, 2, '/images/nike_shirt.jpg', 'Camiseta Nike deportiva', 1),
(6, 2, '/images/levis_jeans.jpg', 'Pantalón Jeans Levis', 1),
(7, 2, '/images/adidas_shoes.jpg', 'Zapatillas Adidas deportivas', 1),
(8, 5, '/images/clean_code_book.jpg', 'Libro Clean Code portada', 1),
(9, 3, '/images/nespresso_machine.jpg', 'Cafetera Nespresso', 1);

-- ========================================
-- CONSULTAS DE VERIFICACIÓN
-- ========================================

-- Verificar que las tablas se crearon correctamente
-- .tables

-- Verificar algunos datos
-- SELECT * FROM Country;
-- SELECT * FROM Users;
-- SELECT * FROM Product;

-- Consulta compleja de ejemplo: Productos con sus categorías
-- SELECT 
--     p.ProductName,
--     p.Price,
--     c.CategoryName
-- FROM Product p
-- JOIN PRODUC_Category pc ON p.id_Product = pc.id_Product
-- JOIN Category c ON pc.id_Category = c.id_Category
-- ORDER BY p.ProductName;