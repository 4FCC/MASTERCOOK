# Imagen base
FROM node:18-alpine

# Estructurar el contenedor
COPY . /app
WORKDIR /app

# Instalar dependencias
RUN npm install

# Exponer puerto para Vite
EXPOSE 3000

# Correr la aplicación Vite en el puerto 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]