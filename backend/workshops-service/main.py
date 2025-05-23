# Importación de librerías necesarias
from fastapi import FastAPI, HTTPException, Query                      # FastAPI para crear rutas y manejar errores
from fastapi.middleware.cors import CORSMiddleware                    # Permite acceso desde el frontend
from pydantic import BaseModel, Field, validator                      # Validación de datos con Pydantic
from typing import Optional, List                                     # Tipos de datos para parámetros opcionales y listas
import mysql.connector                                                # Conexión a base de datos MySQL
import time                                                           # Esperas entre intentos de conexión
from datetime import date, datetime                                   # Manejo de fechas

# Instancia principal de la aplicación
app = FastAPI(title="Workshops Service", version="1.2")

# Middleware CORS: permite solicitudes del frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada para crear un nuevo taller
class WorkshopCreate(BaseModel):
    title: str = Field(..., min_length=4, max_length=100)
    description: str 
    category: str
    date: date
    max_participants: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

    # Validación personalizada para asegurar que la fecha del taller sea futura
    @validator("date")
    def validar_fecha(cls, v):
        if v < datetime.utcnow().date():
            raise ValueError("La fecha del taller debe ser futura.")
        return v

# Modelo de salida para mostrar información de un taller
class Workshop(BaseModel):
    id: int
    title: str
    description: str
    category: str
    date: date
    max_participants: int
    current_participants: int
    price: float

# Función para obtener una conexión a la base de datos con reintento automático
def get_connection():
    for attempt in range(20):
        try:
            return mysql.connector.connect(
                host="db",
                user="root",
                password="12345",
                database="users_db"
            )
        except mysql.connector.Error:
            print(f"[workshops-service] Intento {attempt+1} fallido, esperando...")
            time.sleep(3)
    raise Exception("No se pudo conectar a la base de datos.")

# Evento que se ejecuta al iniciar el microservicio
# Crea la tabla de talleres si no existe
@app.on_event("startup")
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workshops (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100),
            description TEXT,
            category VARCHAR(50),
            date DATE,
            max_participants INT,
            current_participants INT DEFAULT 0,
            price DECIMAL(10,2) NOT NULL DEFAULT 0.00
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Ruta para registrar un nuevo taller
@app.post("/api/workshops", summary="Registrar un nuevo taller", response_model=Workshop)
def crear_taller(data: WorkshopCreate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar que no exista un taller con el mismo título
    cursor.execute("SELECT * FROM workshops WHERE title = %s", (data.title,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=409, detail="Ya existe un taller con este título")

    # Insertar nuevo taller en la base de datos
    cursor.execute("""
        INSERT INTO workshops (title, description, category, date, max_participants, price)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data.title, data.description, data.category, data.date, data.max_participants, data.price))
    conn.commit()

    # Obtener el taller recién creado
    cursor.execute("SELECT * FROM workshops WHERE title = %s", (data.title,))
    taller = cursor.fetchone()
    cursor.close()
    conn.close()

    return taller

# Ruta para listar todos los talleres con cupo disponible
@app.get("/api/workshops", response_model=List[Workshop], summary="Listar todos los talleres disponibles")
def listar_talleres():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Seleccionar talleres que aún tengan cupos disponibles, ordenados por fecha
    cursor.execute("""
        SELECT * FROM workshops
        WHERE current_participants < max_participants
        ORDER BY date ASC
    """)
    talleres = cursor.fetchall()
    cursor.close()
    conn.close()

    if not talleres:
        raise HTTPException(status_code=404, detail="No hay talleres disponibles")

    return talleres

# Ruta para buscar talleres por categoría y/o palabra clave
@app.get("/api/workshops/buscar", response_model=List[Workshop], summary="Buscar talleres por categoría o palabra clave")
def buscar_talleres(
    categoria: Optional[str] = Query(None),    # Filtro por categoría
    palabra: Optional[str] = Query(None)       # Filtro por palabra clave en título o descripción (opcional)
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Construir la consulta SQL base
    sql = """
        SELECT * FROM workshops
        WHERE current_participants < max_participants
    """
    params = []

    # Agregar filtro por categoría si se proporciona
    if categoria:
        sql += " AND category = %s"
        params.append(categoria)

    # Agregar filtro por palabra clave si se proporciona
    if palabra:
        sql += " AND (title LIKE %s OR description LIKE %s)"
        palabra_busqueda = f"%{palabra}%"
        params.extend([palabra_busqueda, palabra_busqueda])

    # Ordenar resultados por fecha
    sql += " ORDER BY date ASC"

    # Ejecutar consulta y devolver resultados
    cursor.execute(sql, params)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron talleres con los filtros especificados")

    return resultados

# Ruta para comprobar si el microservicio está activo
@app.get("/api/workshops/health", summary="Verifica si el microservicio está activo")
def health():
    return {"status": "workshops-service ok"}
