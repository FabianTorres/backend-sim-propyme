"""Schemas Pydantic del modulo 'RRE' - Registro Renta Empresarial (Pagina 7).

Por ahora solo se declaran los campos que OTRAS paginas necesitan consumir:
Retiros usa las variables temporales H2, H3, H6, H7, I4 e I17 para calcular
[1044] y [1045]. El resto del modulo RRE se implementara en su propia pagina.
"""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.schemas._helpers import coerce_to_decimal


class CamposDigitadosRRE(BaseModel):
    """Variables del RRE que alimentan [1044]/[1045] de Retiros.

    En el asistente real, tras pasar por RRE el contribuyente "vuelve a
    Retiros"; como nuestro backend es stateless, estos valores viajan en el
    request (bloque `digitados.rre`).
    """

    h2: Decimal = Field(default=Decimal("0"))
    h3: Decimal = Field(default=Decimal("0"))
    h6: Decimal = Field(default=Decimal("0"))
    h7: Decimal = Field(default=Decimal("0"))
    i4: Decimal = Field(default=Decimal("0"))
    i17: Decimal = Field(default=Decimal("0"))

    @field_validator("h2", "h3", "h6", "h7", "i4", "i17", mode="before")
    @classmethod
    def _normalizar(cls, value):
        return coerce_to_decimal(value)
