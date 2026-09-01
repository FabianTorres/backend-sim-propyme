"""Endpoint de health check para monitoreo de disponibilidad del servicio."""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Verifica que el servidor esta vivo y respondiendo."""
    return {"status": "ok", "message": "El motor de simulacion SII esta en linea."}