-- Selecciona la base de datos llamada 'users_db' donde se crearán las tablas
USE users_db;
-- Crea una tabla llamada 'users' si no existe aún
CREATE TABLE IF NOT EXISTS users (
-- Columna 'id' como clave primaria autoincremental
id INT AUTO_INCREMENT PRIMARY KEY,
-- Columna para el nombre de usuario con un máximo de 50 caracteres
username VARCHAR(50),
-- Columna para la contraseña con un máximo de 50 caracteres
password VARCHAR(50)
);
-- Inserta un usuario inicial de prueba con username 'admin' y contraseña '1234'
INSERT INTO users (username, password) VALUES ('admin', '1234');