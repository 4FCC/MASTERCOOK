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

# Ruta de prueba
@app.post("/api/v0/hello")
async def hello_world():
    return {"message": "Hello World"}
