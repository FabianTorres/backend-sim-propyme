"""Inspecciona el HTML guardado de Retiros: inputs, selects y referencias."""
from __future__ import annotations

import re
from pathlib import Path


def limpiar(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def main() -> None:
    html = Path("artefactos/10_retiros.html").read_text(encoding="utf-8")
    print("len:", len(html))

    print("\n=== keywords ===")
    for kw in [
        "1044", "1045", "1040", "1041", "1042", "1043", "1049", "1051", "1052",
        "RET30", "RET14", "RET15", "Rut socio", "Usufructuario", "Duplicar",
        "Importar", "Nuevo", "is-usufructuario", "opciones_rut",
    ]:
        print(f"  {kw}: {len(re.findall(re.escape(kw), html))}")

    print("\n=== inputs ===")
    for m in re.finditer(r"<input\b[^>]*>", html, re.IGNORECASE):
        print("  ", limpiar(m.group(0))[:230])

    print("\n=== selects (tipo) ===")
    for m in re.finditer(r"<select\b[^>]*>", html, re.IGNORECASE):
        print("  ", limpiar(m.group(0))[:230])

    print("\n=== options ===")
    for m in re.finditer(r"<option\b[^>]*>.*?</option>", html, re.IGNORECASE | re.DOTALL):
        print("  ", limpiar(m.group(0))[:150])


if __name__ == "__main__":
    main()
