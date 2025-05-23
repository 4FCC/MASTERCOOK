# Importación de librerías necesarias
from fastapi import FastAPI, HTTPException, Depends, status                     # Herramientas principales de FastAPI
from fastapi.middleware.cors import CORSMiddleware                             # Middleware para habilitar CORS (Cross-Origin Resource Sharing)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm   # Seguridad con tokens tipo OAuth2
from pydantic import BaseModel, EmailStr, Field, validator                      # Validación de datos con Pydantic
import mysql.connector                                                          # Conexión con base de datos MySQL
import bcrypt                                                                   # Cifrado de contraseñas
import time                                                                     # Esperas entre intentos de conexión
from jose import JWTError, jwt                                                  # Manejo de tokens JWT (Json Web Token)
from datetime import datetime, timedelta                                        # Manejo de fechas y tiempos

# Configuración del sistema de autenticación con JWT
SECRET_KEY = "mysecretkey"                          # Clave secreta usada para firmar los tokens JWT
ALGORITHM = "HS256"                                 # Algoritmo de encriptación utilizado
ACCESS_TOKEN_EXPIRE_MINUTES = 30                    # Tiempo que durará el token activo (en minutos)

# Instancia principal de la aplicación FastAPI
app = FastAPI(title="Auth Service", version="2.0")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos para el registro de un usuario
class RegisterData(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    # Validación personalizada de la contraseña para garantizar seguridad mínima
    @validator("password")
    def password_strength(cls, v):
        if not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe tener al menos una mayúscula, una minúscula y un número.")
        return v

# Modelo que representa el token generado al iniciar sesión
class Token(BaseModel):
    access_token: str
    token_type: str

# Modelo para mostrar información básica de un usuario
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

# Esquema para extraer el token enviado por el cliente y usarlo en rutas protegidas
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Función para obtener una conexión activa con la base de datos
# Intenta conectarse hasta 20 veces con pausas de 3 segundos entre intentos
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

# Evento que se ejecuta cuando el servidor inicia
# Se asegura de que la tabla de usuarios exista
@app.on_event("startup")
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255)
        )
    """)                    # Crea la tabla solo si no existe
    conn.commit()
    cursor.close()
    conn.close()

# Función para crear un token JWT válido con una fecha de expiración
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})         # Agrega el campo "exp" que define cuándo expira el token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Verifica que el token JWT sea válido. Si no lo es, lanza un error 401
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload                          # Retorna el contenido decodificado del token
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Ruta para registrar un nuevo usuario
@app.post("/api/auth/register")
def register_user(data: RegisterData):
    # Cifrar la contraseña antes de guardarla
    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

    # Conectarse a la base de datos
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar si ya existe un usuario con ese correo
    cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Correo ya registrado")

    # Insertar el nuevo usuario
    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                   (data.name, data.email, hashed))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Usuario registrado exitosamente"}

# Ruta para iniciar sesión. Devuelve un token JWT si las credenciales son válidas
@app.post("/api/auth/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Buscar al usuario por correo electrónico
    cursor.execute("SELECT * FROM users WHERE email = %s", (form_data.username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Verificar si el usuario existe y si la contraseña es correcta
    if not user or not bcrypt.checkpw(form_data.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Crear y devolver el token JWT
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

# Ruta para cerrar sesión (informativa, el token debe eliminarse en el cliente)
@app.post("/api/auth/logout")
def logout():
    return {"message": "Logout exitoso. Elimina el token en el cliente."}

# Ruta para obtener los datos del perfil de usuario autenticado
@app.get("/api/auth/profile", response_model=UserOut)
def get_profile(token_data=Depends(verify_token)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Buscar al usuario por el correo que está en el token
    cursor.execute("SELECT id, name, email FROM users WHERE email = %s", (token_data["sub"],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Si no se encuentra, se lanza un error
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Ruta para probar si el servicio está activo
@app.get("/api/auth/health")
def health():
    return {"status": "auth-service ok"}
