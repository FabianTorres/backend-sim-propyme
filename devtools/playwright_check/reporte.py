"""Reporte de diferencias en consola y archivo Markdown."""
from __future__ import annotations

from pathlib import Path


def generar(nombre: str, diferencias: list[dict], total_comparadas: int, ruta_md: Path) -> None:
    ok = total_comparadas - len(diferencias)
    print("\n" + "=" * 70)
    print(f"RESULTADO {nombre}: {ok} de {total_comparadas} celdas coinciden")
    print("=" * 70)
    if diferencias:
        print(f"\n{len(diferencias)} DIFERENCIAS:")
        for d in diferencias:
            print(
                f"  {d['codigo']:>6}.{d['columna']} ({d['campo']}): "
                f"web={d['valor_web']}  backend={d['valor_backend']}  [{d['tipo']}]"
            )
    else:
        print("Sin diferencias.")

    # Guardar Markdown
    lineas = [f"# Reporte {nombre}", ""]
    lineas.append(f"- Coinciden: {ok}")
    lineas.append(f"- Diferentes: {len(diferencias)}")
    lineas.append(f"- Total comparadas: {total_comparadas}")
    lineas.append("")
    if diferencias:
        lineas.append("| Fila | Col | Campo | Web | Backend | Tipo |")
        lineas.append("|---|---|---|---|---|---|")
        for d in diferencias:
            lineas.append(
                f"| {d['codigo']} | {d['columna']} | {d['campo']} | "
                f"{d['valor_web']} | {d['valor_backend']} | {d['tipo']} |"
            )
    else:
        lineas.append("Sin diferencias.")
    ruta_md.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\nReporte guardado en {ruta_md}")
