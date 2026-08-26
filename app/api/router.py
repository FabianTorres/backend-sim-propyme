"""Router principal de la API v1.

Centraliza el registro de los routers de cada pagina del Asistente Propyme.
A medida que se agreguen nuevas paginas (Egresos, Retiros, RLI, Recuadro 17),
basta con importar su APIRouter aqui.
"""
from fastapi import APIRouter

from app.api.endpoints import ingresos

# Prefijo global de la version 1 de la API
api_v1 = APIRouter(prefix="/v1")

api_v1.include_router(ingresos.router, prefix="/simulador")