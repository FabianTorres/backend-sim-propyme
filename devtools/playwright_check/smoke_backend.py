"""Verifica que el payload del caso produce una respuesta valida del backend."""
from __future__ import annotations

from backend_client import calcular, cargar_caso


def main() -> None:
    payload = cargar_caso()
    resp = calcular(payload)
    print("claves de respuesta:", list(resp.keys()))
    for modulo in ("ingresos", "egresos"):
        nodo = resp.get(modulo)
        if not nodo:
            print(f"{modulo}: None")
            continue
        totales = nodo.get("totales")
        filas = nodo.get("filas", [])
        print(f"\n=== {modulo} ===")
        print("totales:", totales)
        print("num filas:", len(filas))
        for f in filas:
            b = f.get("ingresos_ano") if modulo == "ingresos" else f.get("egresos_ano")
            h = (
                f.get("ingresos_adeudados_at_anterior")
                if modulo == "ingresos"
                else f.get("egresos_adeudados_at_anterior")
            )
            fcol = (
                f.get("monto_ingreso_percibido")
                if modulo == "ingresos"
                else f.get("monto_egresos_pagados")
            )
            print(f"  {f['codigo']:>5} | B={b} H={h} F={fcol} | {f['concepto'][:44]}")


if __name__ == "__main__":
    main()
