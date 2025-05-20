from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from fastapi.responses import JSONResponse

# Inicialización de la aplicación FastAPI
app = FastAPI()

# Orígenes permitidos para CORS
origins = ["http://localhost:3000"]

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos para el login
class LoginData(BaseModel):
    username: str
    password: str

# Ruta de prueba
@app.post("/api/v0/hello")
async def hello_world():
    return {"message": "Hello World"}

# Ruta de login
@app.post("/login")
async def login(data: LoginData):
    try:
        # Conexión a la base de datos
        db = mysql.connector.connect(
            host="db",  # o "localhost" si no está en contenedor
            user="root",
            password="12345",
            database="users_db"
        )

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (data.username, data.password)
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            return {"message": "Login exitoso"}
        else:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
