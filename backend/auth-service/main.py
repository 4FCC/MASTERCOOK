# Importación de módulos principales de FastAPI y herramientas relacionadas
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Pydantic para validación de datos de entrada
from pydantic import BaseModel, EmailStr, Field, validator

# Conector de MySQL y herramientas para hashing de contraseñas
import mysql.connector
import bcrypt
import time

# Herramientas para trabajar con JWT
from jose import JWTError, jwt
from datetime import datetime, timedelta

# --- CONFIGURACIÓN JWT ---

# Clave secreta para firmar los tokens (debe ser protegida en producción)
SECRET_KEY = "mysecretkey"

# Algoritmo de firma del token
ALGORITHM = "HS256"

# Tiempo de expiración del token (en minutos)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- INSTANCIA DE FASTAPI ---

# Inicializa la aplicación FastAPI con título y versión
app = FastAPI(title="Auth Service", version="2.0")

# Middleware CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Origen permitido
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS ---

# Esquema para registro de usuario con validaciones
class RegisterData(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    # Validador personalizado para asegurar que la contraseña sea fuerte
    @validator("password")
    def password_strength(cls, v):
        if not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe tener al menos una mayúscula, una minúscula y un número.")
        return v

# Modelo de respuesta para el token JWT
class Token(BaseModel):
    access_token: str
    token_type: str

# Modelo para retornar información básica del usuario autenticado
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

# Esquema para extraer el token JWT del encabezado Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- CONEXIÓN A BASE DE DATOS CON REINTENTOS ---

# Función para conectarse a MySQL con hasta 20 intentos
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
            print(f"[auth-service] Intento {attempt+1} fallido, esperando...")
            time.sleep(3)
    raise Exception("No se pudo conectar a la base de datos.")

# --- CREACIÓN DE LA TABLA EN EL INICIO DEL SERVICIO ---

@app.on_event("startup")
def create_table():
    # Crea la tabla users si no existe
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# --- FUNCIONES RELACIONADAS A JWT ---

# Genera un token JWT con tiempo de expiración
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Verifica que el token JWT sea válido y lo decodifica
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# --- REGISTRO DE USUARIO ---

@app.post("/api/auth/register", summary="Registrar un nuevo usuario")
def register_user(data: RegisterData):
    # Hash de la contraseña del usuario
    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    
    # Conexión a la base de datos
    conn = get_connection()
    cursor = conn.cursor()

    # Verifica si el correo ya está registrado
    cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Correo ya registrado")

    # Inserta el nuevo usuario
    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                   (data.name, data.email, hashed))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Usuario registrado exitosamente"}

# --- LOGIN DE USUARIO Y RETORNO DE TOKEN JWT ---

@app.post("/api/auth/login", response_model=Token, summary="Iniciar sesión y obtener token")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Busca el usuario por email
    cursor.execute("SELECT * FROM users WHERE email = %s", (form_data.username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Valida las credenciales
    if not user or not bcrypt.checkpw(form_data.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Genera el token para el usuario
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

# --- LOGOUT SIMULADO ---

@app.post("/api/auth/logout", summary="Cerrar sesión (simulado)")
def logout():
    # Logout en JWT se maneja en el cliente eliminando el token
    return {"message": "Logout exitoso. Elimina el token en el cliente."}

# --- PERFIL DEL USUARIO AUTENTICADO ---

@app.get("/api/auth/profile", response_model=UserOut, summary="Obtener perfil del usuario autenticado")
def get_profile(token_data=Depends(verify_token)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtiene el usuario según el correo en el token
    cursor.execute("SELECT id, name, email FROM users WHERE email = %s", (token_data["sub"],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user

# --- ENDPOINT DE SALUD DEL SERVICIO ---

@app.get("/api/auth/health", summary="Verifica si el microservicio está activo")
def health():
    return {"status": "auth-service ok"}
