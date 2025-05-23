# backend/API_GATEWAY/main.py
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import httpx

app = FastAPI(title="API Gateway", version="1.0")

# Permitimos sólo el frontend
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs de tus microservicios (ajusta puertos si cambian)
AUTH_URL      = os.getenv("AUTH_URL",      "http://auth-service:5000")
BOOKING_URL   = os.getenv("BOOKING_URL",   "http://booking-service:5000")
PAYMENT_URL   = os.getenv("PAYMENT_URL",   "http://payment-service:5000")
WORKSHOPS_URL = os.getenv("WORKSHOPS_URL", "http://workshops-service:5000")

# Cliente HTTP reutilizable
client = httpx.AsyncClient(timeout=30.0)

# Helper genérico para proxy
async def proxy(request: Request, target_base: str, strip_prefix: str):
    # Construyo la URL destino
    path = request.url.path.removeprefix(strip_prefix)
    url = httpx.URL(target_base + path).include_query_params(**request.query_params)
    # Copio método, cabeceras y body
    req = client.build_request(
        request.method,
        url,
        headers={key: value for key, value in request.headers.items() if key != "host"},
        content=await request.body()
    )
    resp = await client.send(req, stream=True)
    # Stream de vuelta al cliente
    return StreamingResponse(
        resp.aiter_raw(),
        status_code=resp.status_code,
        headers=resp.headers,
        media_type=resp.headers.get("content-type")
    )

# …y ahora las rutas proxy…

@app.api_route("/api/v0/auth/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def proxy_auth(request: Request, path: str):
    return await proxy(request, AUTH_URL, "/api/v0/auth")

@app.api_route("/api/v0/booking/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def proxy_booking(request: Request, path: str):
    return await proxy(request, BOOKING_URL, "/api/v0/booking")

@app.api_route("/api/v0/payment/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def proxy_payment(request: Request, path: str):
    return await proxy(request, PAYMENT_URL, "/api/v0/payment")

@app.api_route("/api/v0/workshops/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def proxy_workshops(request: Request, path: str):
    return await proxy(request, WORKSHOPS_URL, "/api/v0/workshops")

# Ruta de sanity-check del gateway
@app.get("/api/v0/hello")
async def hello_world():
    return {"message": "Hello desde el API Gateway"}
