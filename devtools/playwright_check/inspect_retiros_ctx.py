"""Muestra contexto de las variables derivadas dentro del HTML de Retiros."""
from __future__ import annotations

import re
from pathlib import Path


def main() -> None:
    html = Path("artefactos/10_retiros.html").read_text(encoding="utf-8")
    for kw in ["1044", "1045", "1040", "1041", "1049"]:
        print(f"\n===== {kw} =====")
        for m in re.finditer(re.escape(kw), html):
            ini = max(0, m.start() - 180)
            fin = min(len(html), m.end() + 180)
            print("  ...", re.sub(r"\s+", " ", html[ini:fin]))


if __name__ == "__main__":
    main()
