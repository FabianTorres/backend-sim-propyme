"""Pruebas unitarias de los nodos MinD y Abs del motor de formulas.

Se usan en RLI (9.4, 9.5) y siguen las convenciones de MaxD/Pos.
"""
from decimal import Decimal

from app.core.motor_formulas import Abs, MaxD, MinD, Pos, Var


def test_mind_elige_menor():
    arbol = MinD(Var("A", "vector"), Var("B", "vector"))
    res = arbol.resolver({"A": Decimal("100"), "B": Decimal("60")})
    assert res.valor == Decimal("60")
    assert res.literal == "MIN(A, B)"
    assert "MIN(100, 60) = 60" in res.pasos


def test_mind_con_negativos():
    arbol = MinD(Var("A", "vector"), Var("B", "vector"))
    res = arbol.resolver({"A": Decimal("-5"), "B": Decimal("10")})
    assert res.valor == Decimal("-5")


def test_abs_positivo_y_negativo():
    assert Abs(Var("A", "vector")).resolver({"A": Decimal("7")}).valor == Decimal("7")
    res = Abs(Var("A", "vector")).resolver({"A": Decimal("-7")})
    assert res.valor == Decimal("7")
    assert res.literal == "ABS(A)"
    assert "ABS(-7) = 7" in res.pasos


def test_abs_cero():
    res = Abs(Var("A", "vector")).resolver({"A": Decimal("0")})
    assert res.valor == Decimal("0")


def test_combinacion_rli_max94():
    """Min(P02 * POS(X); P103): el tope manda si el calculo lo supera."""
    x = Var("X", "calculado")
    p02 = Var("P02", "parametro")
    p103 = Var("P103", "parametro")
    arbol = MinD(p02 * Pos(x), p103)
    ctx = {"X": Decimal("1000"), "P02": Decimal("0.5"), "P103": Decimal("100")}
    assert arbol.resolver(ctx).valor == Decimal("100")
    ctx2 = {"X": Decimal("100"), "P02": Decimal("0.5"), "P103": Decimal("100")}
    assert arbol.resolver(ctx2).valor == Decimal("50")
    # MaxD sigue disponible para la condicion (MAX(Vx010213; suma)).
    assert MaxD(Var("A", "vector"), Var("B", "vector")).resolver(
        {"A": Decimal("1"), "B": Decimal("2")}
    ).valor == Decimal("2")
