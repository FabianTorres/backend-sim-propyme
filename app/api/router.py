"""Router principal de la API v1.

Centraliza el registro de los routers de cada pagina del Asistente Propyme.
Ahora expone un unico endpoint /simulador/calcular a traves del Orquestador
Global, que internamente coordina todos los modulos de calculo.
"""
from fastapi import APIRouter

from app.api.endpoints import simulador

# Prefijo global de la version 1 de la API
api_v1 = APIRouter(prefix="/v1")

api_v1.include_router(simulador.router)