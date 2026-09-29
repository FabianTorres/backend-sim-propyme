"""Schemas Pydantic (v2) del modulo 'Determinacion RLI' - Pagina 4 del 14D1.

La RLI se calcula desde los totales de Ingresos (7) y Egresos (8, 8.26) y el
RET30 de Retiros. El frontend solo envia la respuesta al incentivo al ahorro
(`acoge_14e`) y el eventual 9.4 digitado (recortado a [0, maximo]).
"""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas._helpers import coerce_to_decimal
from app.schemas.comunes import InspectorFormula


class CamposDigitadosRLI(BaseModel):
    """Digitados de la pantalla RLI (mensaje 14E y deduccion editable)."""

    # Respuesta al modal "Desea acogerse al incentivo al ahorro": None = aun
    # no responde (cuadro pendiente si califica).
    acoge_14e: bool | None = Field(default=None)
    # 9.4 digitado por el contribuyente; se recorta a [0, max94].
    deduccion_14e: Decimal = Field(default=Decimal("0"))

    @field_validator("deduccion_14e", mode="before")
    @classmethod
    def _normalizar(cls, value):
        return coerce_to_decimal(value)


class AvisosRLI(BaseModel):
    """Reglas de despliegue de filas para el frontend."""

    mostrar_9_1: bool = False
    mostrar_9_2: bool = False
    mostrar_9_5: bool = False


class RLIResponse(BaseModel):
    """Contrato de salida del modulo RLI.

    `cuadro` indica que tabla exhibir: t1 (con 14E), t2 (perdida), t3
    (sin 14E) o pendiente (modal aun sin responder). 9.7 (Cuadro 2, F22 1440)
    comparte el valor de `v9_6`; el cuadro indica que codigo rotular.
    """

    v9: Decimal = Field(default=Decimal("0"))
    v9_1: Decimal = Field(default=Decimal("0"))
    v9_2: Decimal = Field(default=Decimal("0"))
    v9_21: Decimal = Field(default=Decimal("0"))
    v9_3: Decimal = Field(default=Decimal("0"))
    max94: Decimal = Field(default=Decimal("0"))
    v9_4: Decimal = Field(default=Decimal("0"))
    v9_5: Decimal = Field(default=Decimal("0"))
    v9_6: Decimal = Field(default=Decimal("0"))
    subtotal: Decimal = Field(default=Decimal("0"))
    condicion_ok: bool = False
    cuadro: Literal["t1", "t2", "t3", "pendiente"] = "t3"
    mostrar_modal_14e: bool = False
    codigos: dict[str, Decimal] = Field(default_factory=dict)
    avisos: AvisosRLI = Field(default_factory=AvisosRLI)
    inspectores: dict[str, InspectorFormula] | None = Field(default=None)
