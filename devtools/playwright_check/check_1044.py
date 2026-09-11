"""Calcula [1044] y [1045] desde el payload (con H2..I4 = 0) para el caso QA."""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path


def main() -> None:
    v = json.loads(Path("casos/rut_69500400-1.json").read_text(encoding="utf-8"))["vectores"]

    def g(k: str) -> Decimal:
        return Decimal(str(v.get(k, 0)))

    # Variables del RRE (H2, H3, H6, H7, I4, I17): aun no implementado -> 0.
    rre = Decimal(0)

    base1044 = g("Vx014301") + g("Vx013509") + g("Vx013567") + g("Vx013591") + rre
    v1044 = base1044 if base1044 > 0 else Decimal(0)

    base45 = g("Vx014661") - g("Vx014662") - g("Vx014663")
    v1045 = (base45 if base45 > 0 else Decimal(0)) + g("Vx013510") + g("Vx013568") + g("Vx012951") + rre

    print("Vx014301 =", g("Vx014301"))
    print("Vx013509 =", g("Vx013509"), "| Vx013567 =", g("Vx013567"), "| Vx013591 =", g("Vx013591"))
    print("[1044] =", v1044)
    print("Vx014661 =", g("Vx014661"), "Vx014662 =", g("Vx014662"), "Vx014663 =", g("Vx014663"))
    print("Vx013510 =", g("Vx013510"), "| Vx013568 =", g("Vx013568"), "| Vx012951 =", g("Vx012951"))
    print("[1045] =", v1045)


if __name__ == "__main__":
    main()
