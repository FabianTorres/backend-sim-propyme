"""Helpers compartidos entre los servicios de calculo de cada pagina.

Centraliza logica generica que toda pagina necesita para construir formulas
con el Arbol de Expresiones y exponer su desglose en Modo Auditoria. Evita que
cada servicio duplique la conversion ResultadoNodo -> InspectorFormula o el
patron de override manual.
"""

from app.core.motor_formulas import Nodo, ReemplazoManual, ResultadoNodo
from app.schemas.comunes import InspectorFormula, VariableInfo


def _con_override(digitado: Nodo, formula: Nodo) -> Nodo:
    """Override: si el contribuyente ingreso un valor (>0), se usa; sino la formula."""
    return ReemplazoManual(digitado, formula)


def _a_inspector(r: ResultadoNodo) -> InspectorFormula:
    """Convierte un ResultadoNodo en InspectorFormula (schema Pydantic)."""
    return InspectorFormula(
        valor=r.valor,
        literal=r.literal,
        evaluado=r.evaluado,
        variables_usadas=[
            VariableInfo(
                nombre=v["nombre"],
                valor=v["valor"],
                origen=v["origen"],
            )
            for v in r.variables_usadas
        ],
        pasos=list(r.pasos),
    )


def clave_celda(modulo: str, fila: str, col: str) -> str:
    """Construye la clave canonica de una celda para el contexto y el inspector.

    Convencion: '<Modulo> <fila><col>' (ej. 'Ingresos 7.1B', 'Egresos 3.2C').
    Usar esta funcion en todas las paginas garantiza que las variables_usadas
    del inspector sean legibles y consistentes para QA y contadores.
    """
    return f"{modulo} {fila}{col}"
