"""Motor de Formulas basado en Arbol de Expresiones (Composite Pattern).

Permite el Modo Auditoria: ademas del resultado numerico, cada nodo produce
su formula literal (nombres de variables), su formula evaluada (valores reales)
y la lista de variables usadas con su origen.

El diseno usa un unico recorrido bottom-up en resolver(contexto) para generar
toda la metadata de auditoria en una sola pasada.

Uso:
    arbol = Var("Vx012188", "vector") + Var("Vx013384", "vector")
    resultado = arbol.resolver({"Vx012188": 1000000, "Vx013384": 100000})
    # resultado.valor == 1100000
    # resultado.literal == "Vx012188 + Vx013384"
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Callable

from app.utils.matematicas import CERO

# ---------------------------------------------------------------------------
# Resultado de una evaluacion (una sola pasada bottom-up)
# ---------------------------------------------------------------------------


@dataclass
class ResultadoNodo:
    """Producto de resolver un arbol de expresiones en un solo recorrido."""

    valor: Decimal
    literal: str
    evaluado: str
    variables_usadas: list[dict[str, Any]] = field(default_factory=list)
    # Cada dict: {"nombre": str, "valor": Decimal, "origen": str}
    pasos: list[str] = field(default_factory=list)
    # Paso a paso de la resolucion bottom-up para el Modo Auditoria


# ---------------------------------------------------------------------------
# Nodo base (Composite) con sobrecarga de operadores
# ---------------------------------------------------------------------------


class Nodo(ABC):
    """Nodo abstracto del arbol de expresiones."""

    def __add__(self, other: Nodo | Decimal | int) -> "Suma":
        return Suma(self, _a_nodo(other))

    def __radd__(self, other: Nodo | Decimal | int) -> "Suma":
        return Suma(_a_nodo(other), self)

    def __sub__(self, other: Nodo | Decimal | int) -> "Resta":
        return Resta(self, _a_nodo(other))

    def __rsub__(self, other: Nodo | Decimal | int) -> "Resta":
        return Resta(_a_nodo(other), self)

    def __mul__(self, other: Nodo | Decimal | int) -> "Multiplicacion":
        return Multiplicacion(self, _a_nodo(other))

    def __rmul__(self, other: Nodo | Decimal | int) -> "Multiplicacion":
        return Multiplicacion(_a_nodo(other), self)

    def __neg__(self) -> "Negativo":
        return Negativo(self)

    @abstractmethod
    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        """Evalua este sub-arbol en un solo recorrido bottom-up."""
        ...


# ---------------------------------------------------------------------------
# Helper: convierte escalares a Nodo
# ---------------------------------------------------------------------------
def _a_nodo(valor: Nodo | Decimal | int | float) -> Nodo:
    if isinstance(valor, Nodo):
        return valor
    return Constante(Decimal(str(valor)))


# ---------------------------------------------------------------------------
# Nodos hoja
# ---------------------------------------------------------------------------


class Constante(Nodo):
    """Valor literal fijo (ej. 100, CERO)."""

    def __init__(self, valor: Decimal) -> None:
        self._valor = valor

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        texto = _fmt(self._valor)
        return ResultadoNodo(valor=self._valor, literal=texto, evaluado=texto)


class Var(Nodo):
    """Variable referenciada por nombre en el contexto.

    Args:
        nombre: Clave en el diccionario contexto.
        origen: 'vector', 'externo', 'digitado' o 'calculado'.
        default: Valor si la clave no existe en el contexto.
    """

    def __init__(
        self,
        nombre: str,
        origen: str = "vector",
        default: Decimal = CERO,
    ) -> None:
        self.nombre = nombre
        self.origen = origen
        self.default = default

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        valor = contexto.get(self.nombre, self.default)
        if not isinstance(valor, Decimal):
            valor = Decimal(str(valor))
        return ResultadoNodo(
            valor=valor,
            literal=self.nombre,
            evaluado=_fmt(valor),
            variables_usadas=[
                {"nombre": self.nombre, "valor": valor, "origen": self.origen},
            ],
        )


# ---------------------------------------------------------------------------
# Nodos operadores binarios
# ---------------------------------------------------------------------------


class Suma(Nodo):
    """Suma de dos sub-arboles."""

    def __init__(self, izquierdo: Nodo, derecho: Nodo) -> None:
        self.izq = izquierdo
        self.der = derecho

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        ri = self.izq.resolver(contexto)
        rd = self.der.resolver(contexto)
        pasos = ri.pasos + rd.pasos
        pasos.append(f"{_fmt(ri.valor)} + {_fmt(rd.valor)} = {_fmt(ri.valor + rd.valor)}")
        return ResultadoNodo(
            valor=ri.valor + rd.valor,
            literal=f"({ri.literal} + {rd.literal})",
            evaluado=f"({ri.evaluado} + {rd.evaluado})",
            variables_usadas=_merge_vars(ri.variables_usadas, rd.variables_usadas),
            pasos=pasos,
        )


class Resta(Nodo):
    """Resta de dos sub-arboles."""

    def __init__(self, izquierdo: Nodo, derecho: Nodo) -> None:
        self.izq = izquierdo
        self.der = derecho

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        ri = self.izq.resolver(contexto)
        rd = self.der.resolver(contexto)
        pasos = ri.pasos + rd.pasos
        pasos.append(f"{_fmt(ri.valor)} - {_fmt(rd.valor)} = {_fmt(ri.valor - rd.valor)}")
        return ResultadoNodo(
            valor=ri.valor - rd.valor,
            literal=f"({ri.literal} - {rd.literal})",
            evaluado=f"({ri.evaluado} - {rd.evaluado})",
            variables_usadas=_merge_vars(ri.variables_usadas, rd.variables_usadas),
            pasos=pasos,
        )


class Multiplicacion(Nodo):
    """Multiplicacion de dos sub-arboles."""

    def __init__(self, izquierdo: Nodo, derecho: Nodo) -> None:
        self.izq = izquierdo
        self.der = derecho

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        ri = self.izq.resolver(contexto)
        rd = self.der.resolver(contexto)
        pasos = ri.pasos + rd.pasos
        pasos.append(f"{_fmt(ri.valor)} * {_fmt(rd.valor)} = {_fmt(ri.valor * rd.valor)}")
        return ResultadoNodo(
            valor=ri.valor * rd.valor,
            literal=f"({ri.literal} * {rd.literal})",
            evaluado=f"({ri.evaluado} * {rd.evaluado})",
            variables_usadas=_merge_vars(ri.variables_usadas, rd.variables_usadas),
            pasos=pasos,
        )


class Negativo(Nodo):
    """Negacion unaria (-x)."""

    def __init__(self, operando: Nodo) -> None:
        self.operando = operando

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        ro = self.operando.resolver(contexto)
        pasos = list(ro.pasos)
        pasos.append(f"-({_fmt(ro.valor)}) = {_fmt(-ro.valor)}")
        return ResultadoNodo(
            valor=-ro.valor,
            literal=f"(-{ro.literal})",
            evaluado=f"(-{ro.evaluado})",
            variables_usadas=list(ro.variables_usadas),
            pasos=pasos,
        )


# ---------------------------------------------------------------------------
# Nodos de funcion del dominio SII
# ---------------------------------------------------------------------------


class MaxD(Nodo):
    """MAX(a, b) - maximo entre dos sub-arboles."""

    def __init__(self, izquierdo: Nodo, derecho: Nodo) -> None:
        self.izq = izquierdo
        self.der = derecho

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        ri = self.izq.resolver(contexto)
        rd = self.der.resolver(contexto)
        ganador = ri.valor if ri.valor > rd.valor else rd.valor
        pasos = ri.pasos + rd.pasos
        pasos.append(f"MAX({_fmt(ri.valor)}, {_fmt(rd.valor)}) = {_fmt(ganador)}")
        return ResultadoNodo(
            valor=ganador,
            literal=f"MAX({ri.literal}, {rd.literal})",
            evaluado=f"MAX({ri.evaluado}, {rd.evaluado})",
            variables_usadas=_merge_vars(ri.variables_usadas, rd.variables_usadas),
            pasos=pasos,
        )


class Pos(Nodo):
    """POS(x) = MAX(0, x) - parte positiva."""

    def __init__(self, operando: Nodo) -> None:
        self.operando = operando

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        ro = self.operando.resolver(contexto)
        valor = ro.valor if ro.valor > CERO else CERO
        pasos = list(ro.pasos)
        pasos.append(f"POS({_fmt(ro.valor)}) = {_fmt(valor)}")
        return ResultadoNodo(
            valor=valor,
            literal=f"POS({ro.literal})",
            evaluado=f"POS({ro.evaluado})",
            variables_usadas=list(ro.variables_usadas),
            pasos=pasos,
        )


class Si(Nodo):
    """Condicional: SI(condicion, verdadero, falso).

    Args:
        cond_fn: Callable(contexto) -> bool.
        verdadero: Nodo si condicion es True.
        falso: Nodo si condicion es False.
        descripcion: Etiqueta legible (ej. "Calc4064 > 0").
    """

    def __init__(
        self,
        cond_fn: Callable[[dict[str, Any]], bool],
        verdadero: Nodo,
        falso: Nodo,
        descripcion: str = "condicion",
    ) -> None:
        self._cond = cond_fn
        self.verdadero = verdadero
        self.falso = falso
        self.descripcion = descripcion

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        if self._cond(contexto):
            r = self.verdadero.resolver(contexto)
            pasos = list(r.pasos)
            pasos.append(f"SI({self.descripcion}) => {_fmt(r.valor)}")
            return ResultadoNodo(
                valor=r.valor,
                literal=f"SI({self.descripcion} => {r.literal})",
                evaluado=f"SI({self.descripcion} => {r.evaluado})",
                variables_usadas=list(r.variables_usadas),
                pasos=pasos,
            )
        r = self.falso.resolver(contexto)
        pasos = list(r.pasos)
        pasos.append(f"SI(NO {self.descripcion}) => {_fmt(r.valor)}")
        return ResultadoNodo(
            valor=r.valor,
            literal=f"SI(NO {self.descripcion} => {r.literal})",
            evaluado=f"SI(NO {self.descripcion} => {r.evaluado})",
            variables_usadas=list(r.variables_usadas),
            pasos=pasos,
        )


class ReemplazoManual(Nodo):
    """Override manual del contribuyente sobre valor propuesto por el SII.

    Representa: si el contribuyente edito un campo (digitado > 0), se usa
    ese valor. Si no, se usa el valor propuesto por formula.
    """

    def __init__(
        self,
        nodo_digitado: Nodo,
        nodo_propuesto: Nodo,
    ) -> None:
        self.digitado = nodo_digitado
        self.propuesto = nodo_propuesto

    def resolver(self, contexto: dict[str, Any]) -> ResultadoNodo:
        rd = self.digitado.resolver(contexto)

        if rd.valor > CERO:
            # Si hay override, omitimos por completo el propuesto
            pasos = list(rd.pasos)
            pasos.append(
                f"Se utiliza el valor modificado por el contribuyente = {_fmt(rd.valor)}",
            )
            return ResultadoNodo(
                valor=rd.valor,
                literal=rd.literal,
                evaluado=rd.evaluado,
                variables_usadas=list(rd.variables_usadas),
                pasos=pasos,
            )

        # Si no hay override, usamos 100% el propuesto
        rp = self.propuesto.resolver(contexto)
        pasos = list(rp.pasos)
        pasos.append(
            f"Valor propuesto por el SII (sin edicion manual) = {_fmt(rp.valor)}",
        )
        return ResultadoNodo(
            valor=rp.valor,
            literal=rp.literal,
            evaluado=rp.evaluado,
            variables_usadas=list(rp.variables_usadas),
            pasos=pasos,
        )


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------


def _fmt(valor: Decimal) -> str:
    """Formatea Decimal sin decimales innecesarios para el inspector."""
    return str(
        valor.quantize(Decimal("1")) if valor == valor.to_integral_value() else valor.normalize()
    )


def _merge_vars(
    a: list[dict[str, Any]],
    b: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Combina dos listas de variables usadas sin duplicar por nombre."""
    seen: dict[str, dict[str, Any]] = {}
    for v in a:
        seen[v["nombre"]] = v
    for v in b:
        if v["nombre"] not in seen:
            seen[v["nombre"]] = v
    return list(seen.values())
