"""Servicio Orquestador Global del Simulador Propyme.

Coordina la ejecucion de todos los modulos de calculo (Ingresos, Egresos,
Retiros, RLI, Recuadro 17). Cada modulo se ejecuta en orden respetando sus
dependencias. Este servicio es el unico punto de entrada desde el endpoint.

El Orquestador:
    1. Desempaqueta el SimuladorGlobalRequest.
    2. Invoca secuencialmente cada servicio de pagina.
    3. Consolida los resultados en SimuladorGlobalResponse.
"""

from app.schemas.ingresos import CamposDigitados
from app.schemas.orquestador import (
    SimuladorGlobalRequest,
    SimuladorGlobalResponse,
)
from app.services.ingresos import IngresosService


class OrquestadorService:
    """Motor central del Simulador. Orquesta todos los modulos."""

    def calcular_simulacion(
        self, request: SimuladorGlobalRequest,
    ) -> SimuladorGlobalResponse:
        """Calcula todos los modulos y retorna la respuesta global unificada."""

        # --- Modulo 1: Ingresos ---
        digitados_ingresos = (
            request.digitados.ingresos or CamposDigitados()
        )
        resultado_ingresos = IngresosService().calcular(
            vectores=request.vectores,
            externos=request.externos,
            digitados=digitados_ingresos,
        )

        # --- Modulos futuros van aqui ---
        # resultado_egresos = EgresosService().calcular(...)
        # resultado_retiros = RetirosService().calcular(...)
        # resultado_rli     = RLIService().calcular(...)

        return SimuladorGlobalResponse(
            ingresos=resultado_ingresos,
            # egresos=resultado_egresos,
            # retiros=resultado_retiros,
            # rli=resultado_rli,
        )