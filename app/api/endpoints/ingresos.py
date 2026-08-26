"""Endpoint del modulo 'Ingresos' (Pagina 1 del 14D1).

Expone el Motor de Reglas de Ingresos hacia el exterior. Recibe un
IngresosRequest, lo procesa con IngresosService y retorna un IngresosResponse.
"""
from fastapi import APIRouter

from app.schemas.ingresos import IngresosRequest, IngresosResponse
from app.services.ingresos import IngresosService

router = APIRouter(prefix="/ingresos", tags=["Ingresos"])

_servicio = IngresosService()


@router.post("", response_model=IngresosResponse, status_code=200)
def calcular_ingresos(request: IngresosRequest) -> IngresosResponse:
    """Calcula los campos de ingresos (Columnas B, F, totalizadores y avisos)."""
    return _servicio.calcular(request)