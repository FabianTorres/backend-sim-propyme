"""Servicio Orquestador Global del Simulador Propyme.

Coordina la ejecucion de todos los modulos de calculo (Ingresos, Egresos,
Retiros, Determinacion RLI, Base Imponible, Capital Propio Tributario, RRE y
Confirmacion de resultados). Cada modulo se ejecuta en orden respetando sus
dependencias. Este servicio es el unico punto de entrada desde el endpoint.

El Orquestador:
    1. Desempaqueta el SimuladorGlobalRequest.
    2. Crea un ContextoSimulacion para transportar totales entre paginas.
    3. Invoca secuencialmente cada servicio de pagina.
    4. Consolida los resultados en SimuladorGlobalResponse.
"""

from app.core.parametros import cargar_parametros
from app.schemas.egresos import CamposDigitadosEgresos
from app.schemas.ingresos import CamposDigitados
from app.schemas.orquestador import (
    SimuladorGlobalRequest,
    SimuladorGlobalResponse,
)
from app.schemas.retiros import CamposDigitadosRetiros
from app.schemas.rre import CamposDigitadosRRE
from app.services.contexto import ContextoSimulacion
from app.services.egresos import EgresosService
from app.services.ingresos import IngresosService
from app.services.retiros import RetirosService


class OrquestadorService:
    """Motor central del Simulador. Orquesta todos los modulos."""

    def calcular_simulacion(
        self, request: SimuladorGlobalRequest,
    ) -> SimuladorGlobalResponse:
        """Calcula todos los modulos y retorna la respuesta global unificada."""

        # Contexto compartido: transporta totales y el flag CDEICalc global.
        contexto = ContextoSimulacion(
            patrimonio_personal=request.patrimonio_personal,
        )
        mostrar_formulas = getattr(request, "mostrar_formulas", False)

        # --- Modulo 1: Ingresos (Pagina 1) ---
        digitados_ingresos = request.digitados.ingresos or CamposDigitados()
        resultado_ingresos = IngresosService().calcular(
            vectores=request.vectores,
            externos=request.externos,
            digitados=digitados_ingresos,
            mostrar_formulas=mostrar_formulas,
        )
        # Totales que otras paginas consumiran (ej. RLI).
        contexto.set_total(
            "Ingresos.TotalIngresos", resultado_ingresos.totales.fila_7_total
        )
        contexto.set_total(
            "Ingresos.TotalVentasYServicios", resultado_ingresos.totales.fila_7_12
        )

        # --- Modulo 2: Egresos (Pagina 2) ---
        parametros = cargar_parametros(request.at)
        digitados_egresos = request.digitados.egresos or CamposDigitadosEgresos()
        resultado_egresos = EgresosService().calcular(
            vectores=request.vectores,
            externos=request.externos,
            digitados=digitados_egresos,
            parametros=parametros,
            mostrar_formulas=mostrar_formulas,
        )
        contexto.set_total(
            "Egresos.TotalEgresos", resultado_egresos.totales.fila_8_total
        )

        # --- Modulo 3: Retiros (Pagina 3) ---
        # Recibe las variables H2..I17 del RRE (digitados.rre) para [1044]/[1045].
        digitados_retiros = request.digitados.retiros or CamposDigitadosRetiros()
        digitados_rre = request.digitados.rre or CamposDigitadosRRE()
        resultado_retiros = RetirosService().calcular(
            vectores=request.vectores,
            digitados=digitados_retiros,
            rre=digitados_rre,
            mostrar_formulas=mostrar_formulas,
        )
        contexto.set_total("Retiros.1044", resultado_retiros.calculo.v1044)
        contexto.set_total("Retiros.1045", resultado_retiros.calculo.v1045)
        contexto.set_total("Retiros.RET30", resultado_retiros.totales.ret30)
        contexto.set_total("Retiros.RET15", resultado_retiros.totales.ret15)

        # --- Modulo 4: Determinacion RLI (Pagina 4 - TODO) ---
        #   Depende de Ingresos y Egresos: lee contexto.get_total(...).
        # --- Modulo 5: Base Imponible (Pagina 5 - TODO) ---
        # --- Modulo 6: Capital Propio Tributario (Pagina 6 - TODO) ---
        # --- Modulo 7: Registro Renta Empresarial RRE (Pagina 7 - TODO) ---
        # --- Modulo 8: Confirmacion de resultados (Pagina 8 - TODO) ---

        return SimuladorGlobalResponse(
            ingresos=resultado_ingresos,
            egresos=resultado_egresos,
            retiros=resultado_retiros,
        )