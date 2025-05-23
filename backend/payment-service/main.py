from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import mysql.connector
import time
import uuid
import random
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(title="Payment Mock Service", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class PaymentRequest(BaseModel):
    user_email: EmailStr
    workshop_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    payment_method: str  # "credit_card", "debit_card", "paypal", etc.
    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    expiry_date: Optional[str] = None
    cvv: Optional[str] = None

class PaymentResponse(BaseModel):
    payment_id: str
    status: str  # "approved", "declined", "pending"
    transaction_id: str
    amount: float
    timestamp: datetime
    message: str

class RefundRequest(BaseModel):
    payment_id: str
    reason: Optional[str] = None

# Conexión a la base de datos (igual que tu booking service)
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
            print(f"[payment-service] Intento {attempt+1} fallido, esperando...")
            time.sleep(3)
    raise Exception("No se pudo conectar a la base de datos.")

# Función para validar si existe la reserva
def validate_booking(user_email: str, workshop_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT * FROM bookings WHERE user_email = %s AND workshop_id = %s",
            (user_email, workshop_id)
        )
        booking = cursor.fetchone()
        return booking
    finally:
        cursor.close()
        conn.close()

# Función para actualizar el estado de pago
def update_payment_status(user_email: str, workshop_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE bookings SET payment_status = %s WHERE user_email = %s AND workshop_id = %s",
            (status, user_email, workshop_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# Ruta de prueba
@app.get("/api/payment/hello")
async def hello_world():
    return {"message": "Hello World - Payment Mock Service"}

# Endpoint para procesar pagos
@app.post("/api/payment/process", response_model=PaymentResponse, summary="Procesar pago de reserva")
async def process_payment(payment_request: PaymentRequest):
    # Validar que existe la reserva
    booking = validate_booking(payment_request.user_email, payment_request.workshop_id)
    if not booking:
        raise HTTPException(
            status_code=404, 
            detail="Booking not found for this user and workshop"
        )
    
    # Verificar si ya está pagado
    if booking['payment_status'] == 'Pagado':
        raise HTTPException(
            status_code=400, 
            detail="This booking is already paid"
        )
    
    # Generar IDs únicos
    payment_id = str(uuid.uuid4())
    transaction_id = f"TXN_{random.randint(100000, 999999)}"
    
    # Simular diferentes escenarios de pago basados en datos de entrada
    payment_status = "approved"
    message = "Payment processed successfully"
    
    # Simular fallos basados en ciertos patrones (para testing)
    if payment_request.card_number and payment_request.card_number.endswith("0000"):
        payment_status = "declined"
        message = "Insufficient funds"
    elif payment_request.card_number and payment_request.card_number.endswith("1111"):
        payment_status = "declined" 
        message = "Card expired"
    elif payment_request.card_number and payment_request.card_number.endswith("2222"):
        payment_status = "pending"
        message = "Payment under review"
    elif payment_request.amount > 1000:
        # Pagos grandes tienen más chance de revisión
        if random.random() < 0.3:
            payment_status = "pending"
            message = "High amount payment under review"
    elif random.random() < 0.05:  # 5% de chance de fallo aleatorio
        payment_status = "declined"
        message = "Transaction declined by bank"
    
    # Actualizar el estado en la base de datos
    if payment_status == "approved":
        update_payment_status(payment_request.user_email, payment_request.workshop_id, "Pagado")
    
    response = PaymentResponse(
        payment_id=payment_id,
        status=payment_status,
        transaction_id=transaction_id,
        amount=payment_request.amount,
        timestamp=datetime.now(),
        message=message
    )
    
    return response

# Endpoint para consultar estado de pago
@app.get("/api/payment/status/{payment_id}", summary="Consultar estado de pago")
async def get_payment_status(payment_id: str):
    if len(payment_id) < 10:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Simular diferentes estados basados en el último dígito del UUID
    last_char = payment_id[-1]
    if last_char in ['0', '1', '2']:
        status = "declined"
        message = "Payment was declined"
    elif last_char in ['3', '4']:
        status = "pending"
        message = "Payment is being processed"
    else:
        status = "approved"
        message = "Payment completed successfully"
    
    return {
        "payment_id": payment_id,
        "status": status,
        "message": message,
        "timestamp": datetime.now() - timedelta(hours=random.randint(1, 48))
    }

# Endpoint para reembolsos
@app.post("/api/payment/refund", summary="Procesar reembolso")
async def process_refund(refund_request: RefundRequest):
    refund_id = str(uuid.uuid4())
    
    # Simular diferentes resultados de reembolso
    if random.random() < 0.9:  # 90% de éxito
        status = "approved"
        message = "Refund processed successfully"
    else:
        status = "declined"
        message = "Refund cannot be processed at this time"
    
    return {
        "refund_id": refund_id,
        "original_payment_id": refund_request.payment_id,
        "status": status,
        "message": message,
        "processed_at": datetime.now(),
        "reason": refund_request.reason or "Customer request"
    }

# Endpoint para obtener métodos de pago disponibles
@app.get("/api/payment/methods", summary="Obtener métodos de pago disponibles")
async def get_payment_methods():
    return {
        "methods": [
            {
                "id": "credit_card",
                "name": "Credit Card",
                "supported_brands": ["visa", "mastercard", "amex"],
                "fees": 2.9
            },
            {
                "id": "debit_card", 
                "name": "Debit Card",
                "supported_brands": ["visa", "mastercard"],
                "fees": 1.5
            },
            {
                "id": "paypal",
                "name": "PayPal",
                "fees": 3.4
            },
            {
                "id": "bank_transfer",
                "name": "Bank Transfer",
                "fees": 0.5
            }
        ]
    }

# Endpoint para validar tarjeta (sin procesar pago)
@app.post("/api/payment/validate-card", summary="Validar datos de tarjeta")
async def validate_card(card_data: dict):
    card_number = card_data.get("card_number", "")
    
    # Simulaciones básicas de validación
    if len(card_number) < 13:
        return {"valid": False, "message": "Card number too short"}
    
    if card_number.startswith("4"):
        brand = "visa"
    elif card_number.startswith("5"):
        brand = "mastercard"
    elif card_number.startswith("3"):
        brand = "amex"
    else:
        brand = "unknown"
    
    # Simular tarjetas inválidas
    if card_number.endswith("9999"):
        return {"valid": False, "message": "Invalid card number"}
    
    return {
        "valid": True,
        "brand": brand,
        "message": "Card is valid"
    }

# Endpoint para obtener historial de pagos de un usuario
@app.get("/api/payment/history/{user_email}", summary="Obtener historial de pagos")
async def get_payment_history(user_email: EmailStr):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT b.*, w.title as workshop_title, w.date as workshop_date 
            FROM bookings b 
            JOIN workshops w ON b.workshop_id = w.id 
            WHERE b.user_email = %s
        """, (user_email,))
        bookings = cursor.fetchall()
        
        # Simular datos de pago para cada reserva
        payment_history = []
        for booking in bookings:
            if booking['payment_status'] == 'Pagado':
                payment_history.append({
                    "booking_id": booking['id'],
                    "workshop_title": booking['workshop_title'],
                    "workshop_date": booking['workshop_date'],
                    "amount": random.uniform(50, 200),  # Monto simulado
                    "payment_date": booking['workshop_date'] - timedelta(days=random.randint(1, 30)),
                    "status": "completed",
                    "payment_method": random.choice(["credit_card", "debit_card", "paypal"])
                })
        
        return {"payments": payment_history}
        
    finally:
        cursor.close()
        conn.close()

# Endpoint para verificar el estado de pago de una reserva específica
@app.get("/api/payment/booking/{user_email}/{workshop_id}", summary="Verificar estado de pago de reserva")
async def get_booking_payment_status(user_email: EmailStr, workshop_id: int):
    booking = validate_booking(user_email, workshop_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {
        "booking_id": booking['id'],
        "user_email": booking['user_email'],
        "workshop_id": booking['workshop_id'],
        "booking_status": booking['status'],
        "payment_status": booking['payment_status'],
        "can_pay": booking['payment_status'] == 'Pendiente'
    }

# Health check
@app.get("/api/payment/health")
def health():
    return {"status": "payment-service ok"}

# Ejecutar en puerto 5005 (diferente al booking service que está en 5004)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003, reload=True)