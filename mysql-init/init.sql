USE users_db;

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255)
);

-- Usuario de prueba
INSERT INTO users (name, email, password) VALUES ('Admin', 'admin@mastercook.com', '$2b$12$sQpDdb0.V9OgTQ2SKc9Zp.HKmIwLJkkQaA3E3S4dEymO6pT5Es2n2');



CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100),
    workshop_id INT,
    status ENUM('Confirmada', 'Cancelada', 'Completada') DEFAULT 'Confirmada',
    payment_status ENUM('Pendiente', 'Pagado') DEFAULT 'Pendiente',
    UNIQUE(user_email, workshop_id)
);




CREATE TABLE IF NOT EXISTS workshops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    category VARCHAR(50),
    date DATE,
    max_participants INT,
    current_participants INT DEFAULT 0
);
