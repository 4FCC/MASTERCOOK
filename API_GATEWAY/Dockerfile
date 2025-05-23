# Imagen base
FROM python:3.12-slim

# Estructurar el contenedor
COPY . /app
WORKDIR /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto usado por uvicorn
EXPOSE 5000

# Correr la aplicación FastAPI en el puerto 5000
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "5000"]
