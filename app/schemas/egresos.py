"""Schemas Pydantic (v2) del modulo 'Egresos' - Pagina 2 del 14D1.

Define los contratos de salida (campos calculados) y los campos puros de
entrada digitados por el contribuyente. Espejo del modulo Ingresos.
"""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.schemas._helpers import normalizar_dict_decimal
from app.schemas.comunes import InspectorFormula


class CamposDigitadosEgresos(BaseModel):
    """Campos que el contribuyente digita (sin formula), agrupados por columna."""

    # Col. C: 'No Pagadas del anio'
    no_pagadas: dict[str, Decimal] = Field(default_factory=dict)
    # Col. D: 'No considerar es de Patrimonio Personal'
    no_considerar_patrimonio: dict[str, Decimal] = Field(default_factory=dict)
    # Col. E: 'Facturas de Actividad de Renta Presunta'
    factura_renta_presunta: dict[str, Decimal] = Field(default_factory=dict)
    # Col. B digitada en filas sin formula
    egresos_ano: dict[str, Decimal] = Field(default_factory=dict)
    # Col. H (Override): monto adeudados AT anterior pagados
    egresos_adeudados_at_anterior: dict[str, Decimal] = Field(default_factory=dict)

    @field_validator(
        "no_pagadas",
        "no_considerar_patrimonio",
        "factura_renta_presunta",
        "egresos_ano",
        "egresos_adeudados_at_anterior",
        mode="before",
    )
    @classmethod
    def _normalizar_diccionario(cls, value):
        return normalizar_dict_decimal(value)


class FilaEgreso(BaseModel):
    """Resultado de una fila de la tabla de Egresos."""

    codigo: str
    concepto: str
    codigo_f22: int | None = None
    # Col. B calculada (Egresos del anio); None si no posee formula
    egresos_ano: Decimal | None = None
    # Col. H: montos adeudados AT anterior pagados en el ejercicio
    egresos_adeudados_at_anterior: Decimal | None = None
    # Col. C: No Pagadas del anio
    no_pagadas: Decimal | None = None
    # Col. D: No considerar es de Patrimonio Personal
    no_considerar_patrimonio: Decimal | None = None
    # Col. E: Facturas de Actividad de Renta Presunta
    factura_renta_presunta: Decimal | None = None
    # Col. F calculada (Monto Compras o Egresos Pagados)
    monto_egresos_pagados: Decimal | None = None
    # Modo Auditoria: inspectores por columna (solo cuando mostrar_formulas=True)
    inspectores: dict[str, InspectorFormula] | None = Field(default=None)


class TotalizadoresEgresos(BaseModel):
    """Totalizadores de la tabla (fila 8)."""

    fila_8_total: Decimal = Field(default=Decimal("0"))


class AvisosEgresos(BaseModel):
    """Flags / avisos derivados (mensajes, validaciones)."""

    aviso_arriendos_pagados: bool = Field(default=False)
    mostrar_columna_patrimonio: bool = Field(default=False)
    mostrar_columna_renta_presunta: bool = Field(default=False)


class EgresosResponse(BaseModel):
    """Contrato de salida del modulo Egresos."""

    filas: list[FilaEgreso] = Field(default_factory=list)
    totales: TotalizadoresEgresos = Field(default_factory=TotalizadoresEgresos)
    avisos: AvisosEgresos = Field(default_factory=AvisosEgresos)
