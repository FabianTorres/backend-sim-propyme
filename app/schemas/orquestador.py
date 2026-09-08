"""Schemas del Orquestador Global del Simulador Propyme.

Define los contratos de entrada/salida unificados. Los vectores (Vx...) y las
variables externas (Calc...) son globales y planos; los digitados se agrupan
por pagina. El orquestador compone todo en un solo request/response global.

El Frontend envia un solo JSON y recibe un solo JSON con todos los modulos
calculados. Esto permite dependencias cruzadas (ej. RLI depende de Ingresos y
Egresos) sin que el Frontend tenga que orquestar nada.
"""

from pydantic import BaseModel, Field

from app.schemas.globales import Externos, Vectores
from app.schemas.ingresos import CamposDigitados, IngresosResponse


# ---------------------------------------------------------------------------
# Digitados Globales (sub-nodos por modulo)
# ---------------------------------------------------------------------------
class DigitadosGlobal(BaseModel):
    """Agrupa los campos digitados por pagina/modulo.

    Cada sub-nodo contiene los digitados especificos de esa pagina.
    Si una pagina aun no se ha implementado, su nodo es None.
    """

    # TODO: Al agregar nueva pagina, agregar su nodo aqui, ej:
    # egresos: CamposDigitadosEgresos | None = Field(default=None)
    ingresos: CamposDigitados | None = Field(default=None)


# ---------------------------------------------------------------------------
# Request Global
# ---------------------------------------------------------------------------
class SimuladorGlobalRequest(BaseModel):
    """Contrato de entrada unico del Simulador.

    El Frontend construye este payload y lo envia al endpoint /calcular.
    Los vectores y externos son globales (compartidos por todos los modulos).
    Los digitados van agrupados por pagina dentro de un sub-nodo.
    """

    at: str = Field(default="2025", description="Anio tributario")
    mostrar_formulas: bool = Field(default=False, description="Activa el Modo Auditoria con desglose de formulas")
    # Vectores y externos globales: cada pagina consume el subconjunto que usa.
    vectores: Vectores = Field(default_factory=Vectores)
    externos: Externos = Field(default_factory=Externos)
    # Flag global CDEICalc (se detona en Ingresos, impacta en RLI/Retiros).
    patrimonio_personal: bool | None = Field(default=None)
    digitados: DigitadosGlobal = Field(default_factory=DigitadosGlobal)


# ---------------------------------------------------------------------------
# Response Global
# ---------------------------------------------------------------------------
class SimuladorGlobalResponse(BaseModel):
    """Contrato de salida unico del Simulador.

    Cada pagina calculada puebla su sub-nodo correspondiente.
    Las paginas aun no implementadas aparecen como None.
    """

    # TODO: Al agregar nueva pagina, agregar su nodo aqui, ej:
    # egresos: EgresosResponse | None = Field(default=None)
    ingresos: IngresosResponse | None = Field(default=None)