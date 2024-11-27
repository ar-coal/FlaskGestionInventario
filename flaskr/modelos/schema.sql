--Reseteamos tablas
DROP TABLE if EXISTS Usuario;

DROP TABLE if EXISTS Ubicacion;

DROP TABLE if EXISTS Almacen;

DROP TABLE if EXISTS Proveedor;

DROP TABLE if EXISTS Producto;

DROP TABLE if EXISTS Categoria;

DROP TABLE if EXISTS Acciones;


--Creamos tablas
-- Tabla Usuario
CREATE TABLE
    Usuario (
        Clave INTEGER PRIMARY KEY AUTOINCREMENT,
        Usuario VARCHAR(50) UNIQUE NOT NULL,
        Contrasena VARCHAR(500) NOT NULL,
        Nombre VARCHAR(100) NOT NULL,
        Puesto CHAR NOT NULL
    );

-- Tabla Ubicacion
CREATE TABLE
    Ubicacion (
        Clave INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre VARCHAR(10) UNIQUE NOT NULL,
        Descripcion VARCHAR(100)
    );

--Tabla Almacen
CREATE TABLE
    Almacen (
        Clave INTEGER PRIMARY KEY AUTOINCREMENT,
        Ubicacion INTEGER NOT NULL,
        Capacidad INT NOT NULL,
        FOREIGN KEY (Ubicacion) REFERENCES Ubicacion (Clave)
    );

-- Tabla Proveedor
CREATE TABLE
    Proveedor (
        Clave INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre VARCHAR(100) NOT NULL UNIQUE,
        Telefono VARCHAR(12)
    );

-- Tabla Categoria
CREATE TABLE
    Categoria (
        Clave VARCHAR(5) PRIMARY KEY UNIQUE ,
        Descripcion VARCHAR(100)
    );

-- Tabla Producto
CREATE TABLE
    Producto (
        Clave INTEGER PRIMARY KEY AUTOINCREMENT,
        Almacen INTEGER NOT NULL,
        Categoria VARCHAR(5),
        Proveedor INTEGER NOT NULL,
        Nombre VARCHAR(100) NOT NULL,
        FechaOrden DATE,
        FechaCaducidad DATE,
        CantidadDisponible INT NOT NULL,
        CantidadMinima INT,
        FOREIGN KEY (Categoria) REFERENCES Categoria (Clave) ON UPDATE CASCADE,
        FOREIGN KEY (Almacen) REFERENCES Almacen (Clave),
        FOREIGN KEY (Proveedor) REFERENCES Proveedor (Clave)
    );

-- Tabla Acciones
CREATE TABLE
    Acciones (
        Almacen INTEGER NOT NULL,
        Usuario INTEGER NOT NULL,
        Producto INTEGER NOT NULL,
        Accion VARCHAR(50) NOT NULL,
        Fecha DATETIME NOT NULL,
        FOREIGN KEY (Almacen) REFERENCES Almacen (Clave),
        FOREIGN KEY (Usuario) REFERENCES Usuario (Clave),
        FOREIGN KEY (Producto) REFERENCES Producto (Clave)
    );

--Tablas prellenadas para mayor facilidad, eliminar si se necesita

INSERT INTO Usuario (Usuario, Contrasena, Nombre, Puesto) VALUES ("Admin", "scrypt:32768:8:1$vuhlfXBfNNc8mnRq$cd1547bdc150f0a412fe2e89f281503e70231e2c8349e888bdfcb263a03d89f241f3f1db97e35c6a0386c0ac2a6aae3f28412c2a2f556c9f95845019d0df3bcf", "Admin", "A");
-- INSERT INTO Usuario (Usuario, Contrasena, Nombre, Puesto) VALUES ("Admin inventarios", "123", "Admin Inventarios", "J");
-- INSERT INTO Usuario (Usuario, Contrasena, Nombre, Puesto) VALUES ("Inventarios", "123", "Inventarios", "E");

INSERT INTO Ubicacion (Nombre,Descripcion) VALUES ("WEST2", "Almacen en el este No.2");
INSERT INTO Ubicacion (Nombre,Descripcion) VALUES ("NORTH1", "Almacen en el Norte No.1");

INSERT INTO Almacen (Ubicacion,Capacidad) VALUES (1,200);
INSERT INTO Almacen (Ubicacion,Capacidad) VALUES (1,100);

INSERT INTO Proveedor (Nombre,Telefono) VALUES ("Lala", "1234567890");
INSERT INTO Proveedor (Nombre,Telefono) VALUES ("Bimbo", "0987654321");

INSERT INTO Categoria (Clave,Descripcion) VALUES ("LACT1", "Lacteos bebibles");
INSERT INTO Categoria (Clave,Descripcion) VALUES ("PAN01", "Reposteria de panificadora");



