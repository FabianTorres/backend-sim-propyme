"""Schemas Pydantic compartidos por todos los modulos del Simulador.

Centraliza los artefactos de auditoria (Modo Auditoria / "Caja de Cristal")
que usan todas las paginas. Evita duplicacion entre modulos y acoplamiento
cruzado entre schemas de paginas.
"""

from decimal import Decimal

from pydantic import BaseModel, Field


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
