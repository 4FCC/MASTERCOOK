
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import mysql.connector
import time

app = FastAPI(title="Booking Service", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookingRequest(BaseModel):
    user_email: EmailStr
    workshop_id: int = Field(..., gt=0)

class BookingResponse(BaseModel):
    id: int
    user_email: EmailStr
    workshop_id: int
    status: str
    payment_status: str

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
            print(f"[booking-service] Intento {attempt+1} fallido, esperando...")
            time.sleep(3)
    raise Exception("No se pudo conectar a la base de datos.")

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
            UNIQUE(user_email, workshop_id)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.post("/api/booking/reservar", summary="Reservar un taller con validación completa")
def reservar_taller(data: BookingRequest):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email = %s", (data.user_email,))
    usuario = cursor.fetchone()
    if not usuario:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="El usuario no está registrado")

    cursor.execute("SELECT * FROM workshops WHERE id = %s", (data.workshop_id,))
    taller = cursor.fetchone()
    if not taller:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    if taller["current_participants"] >= taller["max_participants"]:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="No hay cupos disponibles para este taller")

    cursor.execute("SELECT * FROM bookings WHERE user_email = %s AND workshop_id = %s", 
                   (data.user_email, data.workshop_id))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=409, detail="Ya tienes una reserva para este taller")

    cursor.execute("""
        INSERT INTO bookings (user_email, workshop_id)
        VALUES (%s, %s)
    """, (data.user_email, data.workshop_id))

    cursor.execute("""
        UPDATE workshops
        SET current_participants = current_participants + 1
        WHERE id = %s
    """, (data.workshop_id,))

    conn.commit()
    cursor.execute("SELECT * FROM bookings WHERE user_email = %s AND workshop_id = %s",
                   (data.user_email, data.workshop_id))
    reserva = cursor.fetchone()
    cursor.close()
    conn.close()
    return reserva

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

@app.get("/api/booking/health")
def health():
    return {"status": "booking-service ok"}
