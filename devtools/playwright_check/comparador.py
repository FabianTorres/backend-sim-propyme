"""Comparacion de valores web vs backend por celda."""
from __future__ import annotations

from decimal import Decimal

from normalizar import a_decimal


def comparar_modulo(
    filas_backend: list,
    lectura_web: dict,
    campos: dict,
    reajuste: set[str] | None = None,
    total: str | None = None,
) -> list[dict]:
    """Compara la lectura web contra las filas del backend.

    Devuelve una lista de diferencias:
        {codigo, columna, campo, valor_web, valor_backend, tipo}
    donde 'tipo' clasifica la causa de la diferencia.
    """
    indice_backend = {f["codigo"]: f for f in filas_backend}
    diferencias: list[dict] = []
    for codigo, cols_web in lectura_web.items():
        fb = indice_backend.get(codigo)
        if not fb:
            continue
        for col, campo in campos.items():
            valor_backend = fb.get(campo)
            if valor_backend is None:
                continue  # columna no aplica a esta fila
            bd = Decimal(str(valor_backend))
            wd = a_decimal(cols_web.get(col, ""))
            if bd != wd:
                if total and codigo == total:
                    tipo = "propaga-redondeo"
                elif reajuste and codigo in reajuste:
                    tipo = "redondeo-SII"
                else:
                    tipo = "revisar"
                diferencias.append(
                    {
                        "codigo": codigo,
                        "columna": col,
                        "campo": campo,
                        "valor_web": wd,
                        "valor_backend": bd,
                        "tipo": tipo,
                    }
                )
    return diferencias


def contar_comparadas(filas_backend: list, lectura_web: dict, campos: dict) -> int:
    """Cantidad de celdas comparables (backend no None y fila presente en web)."""
    indice_backend = {f["codigo"]: f for f in filas_backend}
    total = 0
    for codigo, cols_web in lectura_web.items():
        fb = indice_backend.get(codigo)
        if not fb:
            continue
        for col, campo in campos.items():
            if fb.get(campo) is not None:
                total += 1
    return total
