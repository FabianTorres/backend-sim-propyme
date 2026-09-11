"""Diagnostico: valores de reajuste (payload vs web) para entender trunc/round."""
from __future__ import annotations

import json
import re
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from pathlib import Path


def main() -> None:
    p = json.loads(Path("casos/rut_69500400-1.json").read_text(encoding="utf-8"))
    v = p["vectores"]

    print("=== vectores reajuste ===")
    for k in [
        "Vx012214", "Vx013350", "Vx012216", "Vx013362", "Vx012221", "Vx013354",
        "Vx012220", "Vx013352", "Vx012217", "Vx013358", "Vx012218", "Vx013360",
    ]:
        print(k, v.get(k, "AUSENTE"))

    html = Path("artefactos/09_egresos.html").read_text(encoding="utf-8")
    rows = re.findall(r"<tr[^>]*>.*?</tr>", html, re.DOTALL)
    print("\n=== filas web (concepto + inputs) ===")
    for i, r in enumerate(rows[:20]):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL)
        concepto = ""
        if tds:
            concepto = re.sub(r"<[^>]+>", " ", tds[0])
            concepto = re.sub(r"\s+", " ", concepto).strip()[:46]
        vals = re.findall(r'value="([^"]*)"', r)
        print(i, "|", concepto, "|", vals)

    print("\n=== reajuste calculado (trunc vs round) ===")
    factor = Decimal("1.19")
    pares = {
        "8.4": ("Vx012214", "Vx013350"),
        "8.6": ("Vx012216", "Vx013362"),
        "8.7": ("Vx012217", "Vx013358"),
        "8.8": ("Vx012218", "Vx013360"),
        "8.10": ("Vx012221", "Vx013354"),
        "8.11": ("Vx012220", "Vx013352"),
    }
    for cod, (a, b) in pares.items():
        va = Decimal(str(v.get(a, 0)))
        vb = Decimal(str(v.get(b, 0)))
        m = va if va > vb else vb
        val = m * factor
        trunc = val.quantize(Decimal("1"), rounding=ROUND_DOWN)
        rond = val.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        print(cod, "max=", m, "reaj=", val, "trunc=", trunc, "round=", rond)


if __name__ == "__main__":
    main()
