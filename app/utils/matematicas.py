"""Utilidades matematicas compartidas por todos los modulos del Simulador.

Define las funciones puras de calculo que se usan en Ingresos, Egresos, RLI y
el resto de paginas. Centralizarlas evita duplicacion y acoplamiento cruzado
entre servicios (ej. Egresos importando de Ingresos).
"""

from decimal import Decimal

CERO = Decimal("0")


def POS(valor: Decimal) -> Decimal:
    """Parte Positiva: devuelve max(valor, 0).

    Equivale a MAX(0, valor). Se aplica sobre valores monetarios (Decimal)
    en formulas tributarias donde los resultados negativos se truncan a cero.
    """
    return valor if valor > CERO else CERO


def max_d(a: Decimal, b: Decimal) -> Decimal:
    """Equivalente a MAX(a, b) con Decimal.

    Util en formulas del SII del tipo MAX(Vx012188; Vx013384+...).
    """
    return a if a > b else b