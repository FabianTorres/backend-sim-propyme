"""Endpoint unico del Simulador Propyme (Orquestador Global).

Expone el Motor de Reglas completo hacia el exterior. Recibe un
SimuladorGlobalRequest, lo procesa con OrquestadorService y retorna un
SimuladorGlobalResponse con todos los modulos calculados.
"""

from fastapi import APIRouter

from app.schemas.orquestador import (
    SimuladorGlobalRequest,
    SimuladorGlobalResponse,
)
from app.services.orquestador import OrquestadorService

router = APIRouter(prefix="/simulador", tags=["Simulador"])

_servicio = OrquestadorService()


@router.post("/calcular", response_model=SimuladorGlobalResponse, status_code=200)
def calcular_simulacion(
    request: SimuladorGlobalRequest,
) -> SimuladorGlobalResponse:
    """Calcula todos los modulos del simulador en un solo paso."""
    return _servicio.calcular_simulacion(request)