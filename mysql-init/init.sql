-- Selecciona la base de datos donde se trabajará
USE users_db;

-- Elimina las tablas si ya existen, para evitar errores de duplicado
DROP TABLE IF EXISTS bookings;   -- Elimina la tabla de reservas
DROP TABLE IF EXISTS workshops;  -- Elimina la tabla de talleres
DROP TABLE IF EXISTS users;      -- Elimina la tabla de usuarios


-- CREACIÓN DE TABLA: USUARIOS

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- Identificador único y automático
    name VARCHAR(100),                        -- Nombre del usuario
    email VARCHAR(100) UNIQUE,                -- Correo electrónico único (no se puede repetir)
    password VARCHAR(255)                     -- Contraseña cifrada
);

-- Inserta un usuario de prueba para login inicial
INSERT INTO users (name, email, password) VALUES (
    'Admin',
    'admin@mastercook.com',
    '$2b$12$sQpDdb0.V9OgTQ2SKc9Zp.HKmIwLJkkQaA3E3S4dEymO6pT5Es2n2'  -- Contraseña cifrada con bcrypt
);

-- CREACIÓN DE TABLA: TALLERES

CREATE TABLE IF NOT EXISTS workshops (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- Identificador único del taller
    title VARCHAR(100),                       -- Título del taller
    description TEXT,                         -- Descripción completa
    category VARCHAR(50),                     -- Categoría del taller (ej. cocina, arte)
    date DATE,                                -- Fecha del evento
    max_participants INT,                     -- Máximo de participantes permitidos
    current_participants INT DEFAULT 0,       -- Participantes actuales (inicia en 0)
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00 -- Precio del taller con dos decimales
);

-- CREACIÓN DE TABLA: RESERVAS

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- Identificador único de la reserva
    user_email VARCHAR(100),                  -- Correo del usuario que hizo la reserva
    workshop_id INT,                          -- ID del taller reservado

    -- Estado de la reserva: por defecto "Confirmada"
    status ENUM('Confirmada', 'Cancelada', 'Completada') DEFAULT 'Confirmada',

    -- Estado de pago: por defecto "Pendiente"
    payment_status ENUM('Pendiente', 'Pagado') DEFAULT 'Pendiente',

    -- Evita reservas duplicadas para el mismo taller y usuario
    UNIQUE(user_email, workshop_id),

    -- Clave foránea: asegura que el correo del usuario exista en la tabla users
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,

    -- Clave foránea: asegura que el taller exista en la tabla workshops
    FOREIGN KEY (workshop_id) REFERENCES workshops(id) ON DELETE CASCADE
);
