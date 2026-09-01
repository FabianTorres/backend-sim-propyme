# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints.health import router as health_router
from app.api.router import api_v1

app = FastAPI(
    title='API Simulador Asistente Propyme',
    description='Motor logico para la certificacion de calidad del SII',
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health_router)
app.include_router(api_v1, prefix='/api')
