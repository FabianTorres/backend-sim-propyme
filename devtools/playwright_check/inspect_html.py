"""Inspecciona un HTML guardado para detectar selectores (inputs, botones, forms, ids)."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def limpiar(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def main() -> None:
    archivo = sys.argv[1] if len(sys.argv) > 1 else "artefactos/02_ct_login.html"
    html = Path(archivo).read_text(encoding="utf-8")
    print("archivo:", archivo, "| longitud:", len(html))

    print("\n=== ocurrencias por keyword ===")
    for kw in ["rut", "clave", "password", "ingresar", "continuar", "tributaria", "usuario", "select", "option"]:
        print(f"  {kw}: {len(re.findall(re.escape(kw), html, re.IGNORECASE))}")

    print("\n=== inputs ===")
    for m in re.finditer(r"<input\b[^>]*>", html, re.IGNORECASE):
        print("  INPUT:", limpiar(m.group(0))[:320])

    print("\n=== selects/options ===")
    for m in re.finditer(r"<select\b[^>]*>", html, re.IGNORECASE):
        print("  SELECT:", limpiar(m.group(0))[:320])

    print("\n=== botones ===")
    for m in re.finditer(r"<button\b[^>]*>.*?</button>", html, re.IGNORECASE | re.DOTALL):
        print("  BTN:", limpiar(m.group(0))[:240])

    print("\n=== forms ===")
    for m in re.finditer(r"<form\b[^>]*>", html, re.IGNORECASE):
        print("  FORM:", limpiar(m.group(0))[:320])

    print("\n=== elementos con id ===")
    for m in re.finditer(r'<[^>]+\bid="[^"]*"[^>]*>', html, re.IGNORECASE):
        print("  ID:", limpiar(m.group(0))[:240])

    print("\n=== labels ===")
    for m in re.finditer(r"<label\b[^>]*>.*?</label>", html, re.IGNORECASE | re.DOTALL):
        print("  LABEL:", limpiar(m.group(0))[:240])


if __name__ == "__main__":
    main()
