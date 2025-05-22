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
