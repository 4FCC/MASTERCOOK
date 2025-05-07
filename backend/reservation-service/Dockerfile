# Imagen base
FROM python:3.12-slim

# Estructurar el contenedor
COPY . /app
WORKDIR /app

# Instalar dependencias
RUN pip install -r requirements.txt

# Correr la aplicación FastAPI
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]


