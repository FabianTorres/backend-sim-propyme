"""Schemas Pydantic (v2) del modulo 'Ingresos' - Pagina 1 del 14D1.

Define los contratos de salida del Motor de Reglas (campos calculados) y los
campos puros de entrada digitados por el contribuyente.

Los vectores (Vx...) y las variables externas (Calc...) son globales a todo el
simulador y viven en app.schemas.globales. Los artefactos de auditoria
compartidos viven en app.schemas.comunes.
"""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.schemas._helpers import normalizar_dict_decimal
from app.schemas.comunes import InspectorFormula


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