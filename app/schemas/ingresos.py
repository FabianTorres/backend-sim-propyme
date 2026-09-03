"""Schemas Pydantic (v2) del modulo 'Ingresos' - Pagina 1 del 14D1.

Define los contratos de entrada/salida del Motor de Reglas.

Regla de negocio critica:
    Todo campo que posea una formula de calculo en el documento se trata
    estrictamente como un **Campo Calculado (Output)**. Por lo tanto el Request
    agrupa unicamente Vectores (Vx...), variables externas (Calc...) y campos
    puros de entrada digitados por el contribuyente. Ninguna formula aparece
    como editable en el request.
"""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas._helpers import coerce_to_decimal, normalizar_dict_decimal


# ---------------------------------------------------------------------------
# Vectores (Vx...) - Input
# ---------------------------------------------------------------------------
class VectoresIngresos(BaseModel):
    """Vectores Vx... de entrada del modulo Ingresos.

    Todos los montos se modelan como Decimal para evitar errores de redondeo
    en calculos tributarios.
    """

    # Control: empresario individual (1 = SI)
    Vx010042: int = Field(default=0)

    # --- Col. H: montos adeudados de AT anterior ---
    Vx014255: Decimal = Field(default=Decimal("0"))
    Vx014256: Decimal = Field(default=Decimal("0"))
    Vx014257: Decimal = Field(default=Decimal("0"))
    Vx014258: Decimal = Field(default=Decimal("0"))
    Vx014259: Decimal = Field(default=Decimal("0"))
    Vx014260: Decimal = Field(default=Decimal("0"))
    Vx014261: Decimal = Field(default=Decimal("0"))
    Vx014262: Decimal = Field(default=Decimal("0"))
    Vx014263: Decimal = Field(default=Decimal("0"))
    Vx014264: Decimal = Field(default=Decimal("0"))
    Vx014265: Decimal = Field(default=Decimal("0"))
    Vx014266: Decimal = Field(default=Decimal("0"))
    Vx014267: Decimal = Field(default=Decimal("0"))

    # --- 7.1 Exportaciones ---
    Vx012188: Decimal = Field(default=Decimal("0"))
    Vx013384: Decimal = Field(default=Decimal("0"))
    Vx013394: Decimal = Field(default=Decimal("0"))
    Vx013395: Decimal = Field(default=Decimal("0"))
    Vx013396: Decimal = Field(default=Decimal("0"))

    # --- 7.2 Facturas por ventas y servicios gravados ---
    Vx012194: Decimal = Field(default=Decimal("0"))
    Vx013257: Decimal = Field(default=Decimal("0"))
    Vx013372: Decimal = Field(default=Decimal("0"))
    Vx013381: Decimal = Field(default=Decimal("0"))
    Vx013387: Decimal = Field(default=Decimal("0"))
    Vx013382: Decimal = Field(default=Decimal("0"))
    Vx013383: Decimal = Field(default=Decimal("0"))

    # --- 7.3 Ventas Exentas / No Gravadas ---
    Vx012189: Decimal = Field(default=Decimal("0"))
    Vx013365: Decimal = Field(default=Decimal("0"))
    Vx013366: Decimal = Field(default=Decimal("0"))
    Vx013367: Decimal = Field(default=Decimal("0"))
    Vx013368: Decimal = Field(default=Decimal("0"))
    Vx013369: Decimal = Field(default=Decimal("0"))
    Vx013370: Decimal = Field(default=Decimal("0"))
    Vx013371: Decimal = Field(default=Decimal("0"))
    Vx013385: Decimal = Field(default=Decimal("0"))

    # --- 7.4 Ventas con retencion sobre margen de comercializacion ---
    Vx012191: Decimal = Field(default=Decimal("0"))

    # --- 7.5 Fact. compra Retencion total ---
    Vx012192: Decimal = Field(default=Decimal("0"))
    Vx013379: Decimal = Field(default=Decimal("0"))
    Vx013380: Decimal = Field(default=Decimal("0"))

    # --- 7.6 Fact. compra Retencion parcial ---
    Vx012193: Decimal = Field(default=Decimal("0"))
    Vx013378: Decimal = Field(default=Decimal("0"))

    # --- 7.7 Boletas / Transbank ---
    Vx012195: Decimal = Field(default=Decimal("0"))
    Vx013373: Decimal = Field(default=Decimal("0"))
    Vx013374: Decimal = Field(default=Decimal("0"))
    Vx013375: Decimal = Field(default=Decimal("0"))
    Vx013376: Decimal = Field(default=Decimal("0"))

    # --- 7.8 Notas de credito emitidas ---
    Vx012197: Decimal = Field(default=Decimal("0"))

    # --- 7.9 Notas de debito emitidas ---
    Vx013377: Decimal = Field(default=Decimal("0"))

    # --- 7.14 Mayor valor inversiones / bienes no depreciables ---
    Vx010118: Decimal = Field(default=Decimal("0"))
    Vx012830: Decimal = Field(default=Decimal("0"))
    Vx010240: Decimal = Field(default=Decimal("0"))
    Vx013639: Decimal = Field(default=Decimal("0"))

    # --- 7.15 Arriendos de bienes raices ---
    Vx012209: Decimal = Field(default=Decimal("0"))

    # --- 7.17 Intereses Directos ---
    Vx010145: Decimal = Field(default=Decimal("0"))
    Vx012210: Decimal = Field(default=Decimal("0"))
    Vx010357: Decimal = Field(default=Decimal("0"))
    Vx010974: Decimal = Field(default=Decimal("0"))
    Vx010358: Decimal = Field(default=Decimal("0"))
    Vx010059: Decimal = Field(default=Decimal("0"))
    Vx010088: Decimal = Field(default=Decimal("0"))
    Vx010985: Decimal = Field(default=Decimal("0"))

    # --- 7.18 Intereses Indirectos ---
    Vx010238: Decimal = Field(default=Decimal("0"))
    Vx010239: Decimal = Field(default=Decimal("0"))
    Vx010236: Decimal = Field(default=Decimal("0"))
    Vx010237: Decimal = Field(default=Decimal("0"))
    Vx010934: Decimal = Field(default=Decimal("0"))
    Vx011015: Decimal = Field(default=Decimal("0"))

    # --- 7.19 Renta de fuente extranjera ---
    Vx013633: Decimal = Field(default=Decimal("0"))
    Vx013634: Decimal = Field(default=Decimal("0"))
    Vx013635: Decimal = Field(default=Decimal("0"))
    Vx013636: Decimal = Field(default=Decimal("0"))
    Vx013637: Decimal = Field(default=Decimal("0"))
    Vx013638: Decimal = Field(default=Decimal("0"))

    # --- 7.20 Otros ingresos ---
    Vx013640: Decimal = Field(default=Decimal("0"))
    Vx013641: Decimal = Field(default=Decimal("0"))
    Vx013642: Decimal = Field(default=Decimal("0"))
    Vx013643: Decimal = Field(default=Decimal("0"))
    Vx013644: Decimal = Field(default=Decimal("0"))
    Vx013645: Decimal = Field(default=Decimal("0"))

    # --- Mensaje validacion / patrimonio personal (VALOR1_PCalc) ---
    Vx013601: Decimal = Field(default=Decimal("0"))
    Vx013602: Decimal = Field(default=Decimal("0"))
    Vx013603: Decimal = Field(default=Decimal("0"))
    Vx013604: Decimal = Field(default=Decimal("0"))
    Vx013506: Decimal = Field(default=Decimal("0"))
    Vx013507: Decimal = Field(default=Decimal("0"))
    Vx013508: Decimal = Field(default=Decimal("0"))
    Vx013509: Decimal = Field(default=Decimal("0"))
    Vx013510: Decimal = Field(default=Decimal("0"))
    Vx013511: Decimal = Field(default=Decimal("0"))
    Vx013512: Decimal = Field(default=Decimal("0"))
    Vx013513: Decimal = Field(default=Decimal("0"))
    Vx013560: Decimal = Field(default=Decimal("0"))
    Vx013561: Decimal = Field(default=Decimal("0"))
    Vx013562: Decimal = Field(default=Decimal("0"))
    Vx013563: Decimal = Field(default=Decimal("0"))
    Vx013564: Decimal = Field(default=Decimal("0"))
    Vx013565: Decimal = Field(default=Decimal("0"))
    Vx013566: Decimal = Field(default=Decimal("0"))
    Vx013567: Decimal = Field(default=Decimal("0"))
    Vx013568: Decimal = Field(default=Decimal("0"))
    Vx013569: Decimal = Field(default=Decimal("0"))
    Vx013570: Decimal = Field(default=Decimal("0"))
    Vx013571: Decimal = Field(default=Decimal("0"))
    Vx013605: Decimal = Field(default=Decimal("0"))
    Vx013606: Decimal = Field(default=Decimal("0"))
    Vx013607: Decimal = Field(default=Decimal("0"))
    Vx013608: Decimal = Field(default=Decimal("0"))
    Vx013588: Decimal = Field(default=Decimal("0"))
    Vx013589: Decimal = Field(default=Decimal("0"))
    Vx013590: Decimal = Field(default=Decimal("0"))
    Vx013591: Decimal = Field(default=Decimal("0"))
    Vx013592: Decimal = Field(default=Decimal("0"))
    Vx013609: Decimal = Field(default=Decimal("0"))
    Vx013610: Decimal = Field(default=Decimal("0"))
    Vx013611: Decimal = Field(default=Decimal("0"))
    Vx013612: Decimal = Field(default=Decimal("0"))
    Vx013613: Decimal = Field(default=Decimal("0"))
    Vx013614: Decimal = Field(default=Decimal("0"))
    Vx013615: Decimal = Field(default=Decimal("0"))
    Vx013616: Decimal = Field(default=Decimal("0"))
    Vx012420: Decimal = Field(default=Decimal("0"))
    Vx012424: Decimal = Field(default=Decimal("0"))
    Vx013750: Decimal = Field(default=Decimal("0"))

    # --- Mensaje validacion / patrimonio personal (VALOR2_PCalc) ---
    Vx013514: Decimal = Field(default=Decimal("0"))
    Vx013515: Decimal = Field(default=Decimal("0"))
    Vx013516: Decimal = Field(default=Decimal("0"))
    Vx013517: Decimal = Field(default=Decimal("0"))
    Vx013518: Decimal = Field(default=Decimal("0"))
    Vx013519: Decimal = Field(default=Decimal("0"))
    Vx013520: Decimal = Field(default=Decimal("0"))
    Vx013521: Decimal = Field(default=Decimal("0"))
    Vx013523: Decimal = Field(default=Decimal("0"))
    Vx013524: Decimal = Field(default=Decimal("0"))
    Vx013525: Decimal = Field(default=Decimal("0"))
    Vx013526: Decimal = Field(default=Decimal("0"))
    Vx013528: Decimal = Field(default=Decimal("0"))
    Vx013572: Decimal = Field(default=Decimal("0"))
    Vx013573: Decimal = Field(default=Decimal("0"))
    Vx013574: Decimal = Field(default=Decimal("0"))
    Vx013575: Decimal = Field(default=Decimal("0"))
    Vx013576: Decimal = Field(default=Decimal("0"))
    Vx013577: Decimal = Field(default=Decimal("0"))
    Vx013578: Decimal = Field(default=Decimal("0"))
    Vx013579: Decimal = Field(default=Decimal("0"))
    Vx013581: Decimal = Field(default=Decimal("0"))
    Vx013582: Decimal = Field(default=Decimal("0"))
    Vx013583: Decimal = Field(default=Decimal("0"))
    Vx013584: Decimal = Field(default=Decimal("0"))
    Vx013586: Decimal = Field(default=Decimal("0"))
    Vx013617: Decimal = Field(default=Decimal("0"))
    Vx013618: Decimal = Field(default=Decimal("0"))
    Vx013593: Decimal = Field(default=Decimal("0"))
    Vx013594: Decimal = Field(default=Decimal("0"))
    Vx013619: Decimal = Field(default=Decimal("0"))
    Vx013620: Decimal = Field(default=Decimal("0"))
    Vx013595: Decimal = Field(default=Decimal("0"))
    Vx013596: Decimal = Field(default=Decimal("0"))
    Vx013621: Decimal = Field(default=Decimal("0"))
    Vx013622: Decimal = Field(default=Decimal("0"))
    Vx013623: Decimal = Field(default=Decimal("0"))
    Vx013597: Decimal = Field(default=Decimal("0"))
    Vx013598: Decimal = Field(default=Decimal("0"))
    Vx013625: Decimal = Field(default=Decimal("0"))
    Vx012421: Decimal = Field(default=Decimal("0"))
    Vx012425: Decimal = Field(default=Decimal("0"))
    Vx012426: Decimal = Field(default=Decimal("0"))

    @field_validator("*", mode="before")
    @classmethod
    def _normalizar(cls, value):
        """Normaliza valores nulos / cadenas vacias a Decimal de cero."""
        if value is None:
            return Decimal("0")
        if isinstance(value, str) and value.strip() == "":
            return Decimal("0")
        return value


# ---------------------------------------------------------------------------
# Variables externas (Calc)
# ---------------------------------------------------------------------------
class ExternosIngresos(BaseModel):
    """Variables externas provenientes de otros asistentes (ej. BR).

    Calc4064: monto proveniente del asistente de Bienes Raices. Puede ser un
              monto (>0) o el literal 'N'. Se modela como Decimal | Literal['N'].
    Calc4075: flag 0/1 del asistente de Bienes Raices.
    """

    Calc4064: Decimal | Literal["N"] = Field(default=Decimal("0"))
    Calc4075: int = Field(default=0)
    CRRP: bool = Field(default=False, description="Atributo de Renta Presunta")

    @field_validator("Calc4064", mode="before")
    @classmethod
    def _norm_calc4064(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if value.upper() == "N":
                return "N"
            if value == "":
                return Decimal("0")
            return Decimal(value)
        return value


# ---------------------------------------------------------------------------
# Campos puros de entrada (digitados, sin formula) - Input
# ---------------------------------------------------------------------------
class CamposDigitados(BaseModel):
    """Campos que el contribuyente digita obligatoriamente (sin formula).

    Se agrupan por columna y se indexan por codigo de fila ('7.1', '7.12', ...).
    """

    # Col. C: 'Monto No Percibido del anio (Neto)'
    monto_no_percibido: dict[str, Decimal] = Field(default_factory=dict)
    # Col. D: 'No considerar es de Patrimonio Personal'
    no_considerar_patrimonio: dict[str, Decimal] = Field(default_factory=dict)
    # Col. E: 'Facturas de Actividad de Renta Presunta'
    factura_renta_presunta: dict[str, Decimal] = Field(default_factory=dict)
    # Col. B digitada en filas sin formula (7.11, 7.13, 7.16, 7.27)
    ingresos_ano: dict[str, Decimal] = Field(default_factory=dict)
    # Col. H (Override): el usuario puede ajustar los montos adeudados AT anterior
    ingresos_adeudados_at_anterior: dict[str, Decimal] = Field(default_factory=dict)

    @field_validator(
        "monto_no_percibido",
        "no_considerar_patrimonio",
        "factura_renta_presunta",
        "ingresos_ano",
        "ingresos_adeudados_at_anterior",
        mode="before",
    )
    @classmethod
    def _normalizar_diccionario(cls, value):
        return normalizar_dict_decimal(value)


# ---------------------------------------------------------------------------
# Inspector de Formulas (Modo Auditoria)
# ---------------------------------------------------------------------------


class VariableInfo(BaseModel):
    """Una variable usada en una formula, con metadata de auditoria."""

    nombre: str
    valor: Decimal
    origen: str  # 'vector' | 'externo' | 'digitado' | 'calculado'


class InspectorFormula(BaseModel):
    """Desglose completo de una formula para el Modo Auditoria.

    Se genera en una sola pasada bottom-up desde el arbol de expresiones.
    """

    valor: Decimal
    literal: str = Field(description="Formula con nombres de variables")
    evaluado: str = Field(description="Formula con valores numericos reales")
    variables_usadas: list[VariableInfo] = Field(default_factory=list)
    pasos: list[str] = Field(
        default_factory=list, description="Paso a paso de la resolucion matematica"
    )


# ---------------------------------------------------------------------------
# Response (modelos de salida)
# ---------------------------------------------------------------------------
class FilaIngreso(BaseModel):
    """Resultado de una fila de la tabla de Ingresos."""

    codigo: str
    concepto: str
    codigo_f22: int | None = None
    # Col. B calculada (Ingresos del anio neto); None si no posee formula
    ingresos_ano: Decimal | None = None
    # Col. H: montos adeudados por fila (Ingresos percibidos de AT anterior)
    ingresos_adeudados_at_anterior: Decimal | None = None
    # Col. C: Monto No Percibido del anio (digitado o calculado en totalizador 7.12)
    monto_no_percibido: Decimal | None = None
    # Col. D: No considerar es de Patrimonio Personal (digitado o calculado en 7.12)
    no_considerar_patrimonio: Decimal | None = None
    # Col. E: Facturas de Actividad de Renta Presunta (digitado o calculado en 7.12)
    factura_renta_presunta: Decimal | None = None
    # Col. F calculada (Monto Ingreso Percibido)
    monto_ingreso_percibido: Decimal | None = None
    # Modo Auditoria: inspectores por columna (solo cuando mostrar_formulas=True)
    #   llaves: "ingresos_ano", "ingresos_adeudados_at_anterior", "monto_ingreso_percibido",
    #   "monto_no_percibido", "no_considerar_patrimonio", "factura_renta_presunta"
    inspectores: dict[str, InspectorFormula] | None = Field(default=None)


class TotalizadoresIngresos(BaseModel):
    """Totalizadores de la tabla (fila 7.12 y fila 7)."""

    fila_7_12: Decimal = Field(default=Decimal("0"))
    fila_7_total: Decimal = Field(default=Decimal("0"))


class AvisosIngresos(BaseModel):
    """Flags / avisos derivados (mensajes, validaciones)."""

    aviso_montos_propuestos_7_10: bool = Field(default=False)
    aviso_arriendos_bienes_raices: bool = Field(default=False)
    # Visibilidad de columnas segun reglas de negocio (para el Frontend)
    mostrar_columna_patrimonio: bool = Field(default=False)
    mostrar_columna_renta_presunta: bool = Field(default=False)
    # Valores calculados para el mensaje de Empresario Individual
    valor1_pcalc: Decimal = Field(default=Decimal("0"))
    valor2_pcalc: Decimal = Field(default=Decimal("0"))


class IngresosResponse(BaseModel):
    """Contrato de salida. Contiene unicamente campos calculados."""

    filas: list[FilaIngreso] = Field(default_factory=list)
    totales: TotalizadoresIngresos = Field(default_factory=TotalizadoresIngresos)
    avisos: AvisosIngresos = Field(default_factory=AvisosIngresos)
