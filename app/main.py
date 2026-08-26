# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_v1

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="API Simulador Asistente Propyme",
    description="Motor lógico para la certificación de calidad del SII",
    version="1.0.0"
)

# Configuración de CORS (Permitir que el Frontend en React se conecte)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, esto se cambia por la URL de React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de los routers de la API v1 bajo el prefijo global /api
app.include_router(api_v1, prefix="/api")

@app.get("/health", tags=["Health"])
def health_check():
    """
    Endpoint básico para verificar que el servidor está vivo.
    """
    return {"status": "ok", "message": "El motor de simulación SII está en línea."}