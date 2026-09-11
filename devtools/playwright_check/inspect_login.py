"""Inspecciona el HTML guardado del login para detectar selectores."""
from __future__ import annotations

import re
from pathlib import Path


def _limpiar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


def main() -> None:
    html = Path("artefactos/01_login.html").read_text(encoding="utf-8")
    print("longitud html:", len(html))

    print("\n=== ocurrencias por keyword ===")
    for kw in ["tributaria", "unica", "clave", "rut", "bifurcacion", "ingresar", "continuar", "button", "input", "href"]:
        n = len(re.findall(re.escape(kw), html, re.IGNORECASE))
        print(f"  {kw}: {n}")

    print("\n=== snippets alrededor de tributaria/unica/bifurcacion ===")
    for m in re.finditer(r".{0,60}(?:tributaria|unica|bifurcacion).{0,200}", html, re.IGNORECASE | re.DOTALL):
        print("  ...", _limpiar(m.group(0))[:400])
        print()

    print("\n=== enlaces <a> / botones <button> con texto ===")
    cont = 0
    for m in re.finditer(r"<(a|button)\b[^>]*>(.*?)</\1>", html, re.IGNORECASE | re.DOTALL):
        inner = _limpiar(re.sub(r"<[^>]+>", " ", m.group(2)))
        if not inner:
            continue
        attrs = _limpiar(m.group(0))[:140]
        print(f"  [{m.group(1)}] {inner[:60]}  => {attrs}")
        cont += 1
        if cont >= 60:
            print("  ... (cortado)")
            break

    print("\n=== inputs ===")
    for m in re.finditer(r"<input\b[^>]*>", html, re.IGNORECASE):
        print("  input:", _limpiar(m.group(0))[:220])


if __name__ == "__main__":
    main()
