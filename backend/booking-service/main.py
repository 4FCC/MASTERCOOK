# Importación de librerías necesarias
from fastapi import FastAPI, HTTPException                     # FastAPI para crear el servicio web y manejar errores
from fastapi.middleware.cors import CORSMiddleware             # Middleware para permitir peticiones desde otros dominios (como un frontend)
from pydantic import BaseModel, EmailStr, Field                # Validación de datos con Pydantic
import mysql.connector                                         # Conexión a base de datos MySQL
import time                                                    # Usado para esperar entre reintentos de conexión

# Instancia principal de la aplicación FastAPI
app = FastAPI(title="Booking Service", version="1.0")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada para hacer una reserva
class BookingRequest(BaseModel):
    user_email: EmailStr
    workshop_id: int = Field(..., gt=0)

# Modelo de salida para mostrar información de una reserva
class BookingResponse(BaseModel):
    id: int
    user_email: EmailStr
    workshop_id: int
    status: str
    payment_status: str

# Función que intenta conectarse a la base de datos hasta 20 veces antes de fallar
def get_connection():
    for attempt in range(20):
        try:
            return mysql.connector.connect(
                host="db",                   # Nombre del host o servicio
                user="root",                 # Usuario de base de datos
                password="12345",            # Contraseña
                database="users_db"          # Nombre de la base de datos
            )
        except mysql.connector.Error:
            print(f"[booking-service] Intento {attempt+1} fallido, esperando...")
            time.sleep(3)
    raise Exception("No se pudo conectar a la base de datos.")

# Evento que se ejecuta al iniciar el servidor
# Crea la tabla de reservas si no existe
@app.on_event("startup")
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(100),
            workshop_id INT,
            status ENUM('Confirmada', 'Cancelada', 'Completada') DEFAULT 'Confirmada',
            payment_status ENUM('Pendiente', 'Pagado') DEFAULT 'Pendiente',
            UNIQUE(user_email, workshop_id)  -- Impide que un mismo usuario reserve el mismo taller dos veces
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Ruta para reservar un taller
@app.post("/api/booking/reservar", summary="Reservar un taller con validación completa")
def reservar_taller(data: BookingRequest):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar si el usuario existe en la base de datos
    cursor.execute("SELECT * FROM users WHERE email = %s", (data.user_email,))
    usuario = cursor.fetchone()
    if not usuario:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="El usuario no está registrado")

    # Verificar si el taller existe
    cursor.execute("SELECT * FROM workshops WHERE id = %s", (data.workshop_id,))
    taller = cursor.fetchone()
    if not taller:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    # Validar que aún haya cupos disponibles en el taller
    if taller["current_participants"] >= taller["max_participants"]:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="No hay cupos disponibles para este taller")

    # Verificar si el usuario ya tiene una reserva para este taller
    cursor.execute("SELECT * FROM bookings WHERE user_email = %s AND workshop_id = %s", 
                   (data.user_email, data.workshop_id))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=409, detail="Ya tienes una reserva para este taller")

    # Insertar la nueva reserva
    cursor.execute("""
        INSERT INTO bookings (user_email, workshop_id)
        VALUES (%s, %s)
    """, (data.user_email, data.workshop_id))

    # Actualizar el número de participantes del taller
    cursor.execute("""
        UPDATE workshops
        SET current_participants = current_participants + 1
        WHERE id = %s
    """, (data.workshop_id,))

    # Confirmar cambios y devolver la reserva recién creada
    conn.commit()
    cursor.execute("SELECT * FROM bookings WHERE user_email = %s AND workshop_id = %s",
                   (data.user_email, data.workshop_id))
    reserva = cursor.fetchone()
    cursor.close()
    conn.close()
    return reserva

# Ruta para listar todas las reservas hechas por un usuario dado
@app.get("/api/booking/usuario/{email}", response_model=list[BookingResponse], summary="Listar reservas por usuario")
def listar_reservas(email: EmailStr):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bookings WHERE user_email = %s", (email,))
    reservas = cursor.fetchall()
    cursor.close()
    conn.close()
    if not reservas:
        raise HTTPException(status_code=404, detail="No se encontraron reservas")
    return reservas

# Ruta para verificar que el servicio está activo
@app.get("/api/booking/health")
def health():
    return {"status": "booking-service ok"}
