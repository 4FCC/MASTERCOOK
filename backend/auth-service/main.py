from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inicialización de la aplicación FastAPI
app = FastAPI()

# Orígenes permitidos para CORS
origins = ["http://localhost:5173"]

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de la API
@app.post("/api/v0/hello")
async def hello_world():
    return {"message": "Hello World"}


