"""Normalizacion de montos (texto web / string backend) a Decimal."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation


def a_decimal(texto) -> Decimal:
    """Convierte un valor de celda web o string del backend a Decimal.

    Maneja: vacio/None -> 0, simbolo $, separador de miles (punto chileno),
    coma decimal, y parentesis de negativos.
    """
    if texto is None:
        return Decimal("0")
    s = str(texto).strip()
    if s in ("", "-", "$"):
        return Decimal("0")

    negativo = False
    s = s.replace("$", "").replace("\u00a0", " ").replace(" ", "")
    if s.startswith("(") and s.endswith(")"):
        negativo = True
        s = s[1:-1]
    if s.startswith("-"):
        negativo = True
        s = s[1:]

    # Asumimos formato chileno: punto = separador de miles, coma = decimal.
    # Los montos del asistente vienen ya redondeados (enteros), pero se tolera coma.
    s = s.replace(".", "").replace(",", ".")
    if s == "":
        return Decimal("0")
    try:
        valor = Decimal(s)
    except InvalidOperation:
        return Decimal("0")
    return -valor if negativo else valor
