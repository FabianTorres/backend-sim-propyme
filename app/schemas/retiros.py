"""Schemas Pydantic (v2) del modulo 'Retiros' - Pagina 3 del 14D1.

Retiros es una pagina casi de solo ingreso: el contribuyente ingresa los socios
y sus retiros (RET1..RET12). El backend calcula variables internas ([1044] y
[1045], las derivadas 1040..1052 y los totales RET30/RET14/RET15) que validan
la pantalla y alimentan la pagina RRE.

Los RUT de socios provienen del RIAC en el asistente real; como no accedemos al
RIAC, el frontend los envia en `filas` (el analista los ingresa). Las variables
H2..I17 del RRE llegan en `digitados.rre` (ver app/schemas/rre.py).
"""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.schemas._helpers import coerce_to_decimal
from app.schemas.comunes import InspectorFormula


class FilaRetiroDigitada(BaseModel):
    """Una fila del recuadro Retiros (un socio + una fecha de retiro)."""

    rut: str = Field(default="")                              # RET1
    usufructuario: int | None = Field(default=None)           # RET2 (1 o 2)
    acciones: Decimal = Field(default=Decimal("0"))           # RET3
    f1_fecha: str = Field(default="")                         # RET4
    f1_monto: Decimal = Field(default=Decimal("0"))           # RET5
    f1_isfut_h: Decimal = Field(default=Decimal("0"))         # RET6
    f1_isfut_a: Decimal = Field(default=Decimal("0"))         # RET7
    saldo: Decimal = Field(default=Decimal("0"))              # RET8
    f2_fecha: str = Field(default="")                         # RET9
    f2_monto: Decimal = Field(default=Decimal("0"))           # RET10
    f2_isfut_h: Decimal = Field(default=Decimal("0"))         # RET11
    f2_isfut_a: Decimal = Field(default=Decimal("0"))         # RET12
    es_registro_nuevo: bool = Field(default=False)

    @field_validator(
        "acciones",
        "f1_monto",
        "f1_isfut_h",
        "f1_isfut_a",
        "saldo",
        "f2_monto",
        "f2_isfut_h",
        "f2_isfut_a",
        mode="before",
    )
    @classmethod
    def _normalizar(cls, value):
        return coerce_to_decimal(value)


class CamposDigitadosRetiros(BaseModel):
    """Filas digitadas del recuadro Retiros."""

    filas: list[FilaRetiroDigitada] = Field(default_factory=list)


class FilaRetiro(BaseModel):
    """Fila de salida (echo de la entrada, numerada)."""

    fila: int
    rut: str
    usufructuario: int | None = None
    acciones: Decimal
    f1_fecha: str
    f1_monto: Decimal
    f1_isfut_h: Decimal
    f1_isfut_a: Decimal
    saldo: Decimal
    f2_fecha: str
    f2_monto: Decimal
    f2_isfut_h: Decimal
    f2_isfut_a: Decimal
    es_registro_nuevo: bool
    validacion_f1: bool = True
    validacion_f2: bool = True


class VariableDerivada(BaseModel):
    """Variable generada para usos posteriores (RRE/RLI)."""

    codigo: str
    rut: str
    fecha: str | None = None
    valor: Decimal


class CalculoRetiros(BaseModel):
    """Variables internas de validacion."""

    v1044: Decimal = Field(default=Decimal("0"))
    v1045: Decimal = Field(default=Decimal("0"))


class TotalizadoresRetiros(BaseModel):
    """Totales derivados."""

    ret30: Decimal = Field(default=Decimal("0"))          # suma de RET5
    ret15: Decimal = Field(default=Decimal("0"))          # suma de RET6
    ret14: dict[str, Decimal] = Field(default_factory=dict)  # suma RET6 por socio


class AvisosRetiros(BaseModel):
    """Habilitaciones y validaciones de la pantalla."""

    ret3_habilitado: bool = False
    ret6_habilitado: bool = False
    ret7_habilitado: bool = False
    ret11_habilitado: bool = False
    ret12_habilitado: bool = False
    validacion_1044_ok: bool = True
    validacion_1045_ok: bool = True


class RetirosResponse(BaseModel):
    """Contrato de salida del modulo Retiros."""

    filas: list[FilaRetiro] = Field(default_factory=list)
    calculo: CalculoRetiros = Field(default_factory=CalculoRetiros)
    derivadas: list[VariableDerivada] = Field(default_factory=list)
    totales: TotalizadoresRetiros = Field(default_factory=TotalizadoresRetiros)
    avisos: AvisosRetiros = Field(default_factory=AvisosRetiros)
    inspectores: dict[str, InspectorFormula] | None = Field(default=None)
