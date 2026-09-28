"""Chequeo visual hasta Retiros: estructura web vs doc vs backend (caso QA)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from playwright.sync_api import sync_playwright

import auth
import config
import web_scraper
from app.schemas.orquestador import SimuladorGlobalRequest
from app.services.orquestador import OrquestadorService


def limpiar(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def main() -> None:
    # 1) Backend (oraculo) con el caso QA.
    payload = json.loads((config.CASOS_DIR / "rut_69500400-1.json").read_text(encoding="utf-8"))
    req = SimuladorGlobalRequest.model_validate(payload)
    resp = OrquestadorService().calcular_simulacion(req)
    r = resp.retiros
    print("BACKEND [1044] =", r.calculo.v1044)
    print("BACKEND [1045] =", r.calculo.v1045)
    print("BACKEND RET30 =", r.totales.ret30, "| RET15 =", r.totales.ret15)
    print("BACKEND avisos =", r.avisos.model_dump())

    # 2) Navegacion en vivo hasta Retiros.
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()
        web_scraper.llegar_a_ingresos(page)
        web_scraper.aceptar_alertas(page)
        web_scraper.continuar(page)  # -> Egresos
        web_scraper.aceptar_alertas(page)
        web_scraper.continuar(page)  # -> Retiros
        web_scraper.aceptar_alertas(page)

        print("\nURL:", page.url)
        print("TITULO:", page.title())
        body = page.locator("body").inner_text()
        print("\n=== TEXTO (primeros 2500) ===")
        print(limpiar(body)[:2500])

        # Estructura de la tabla.
        tablas = page.locator("table")
        print("\n=== TABLAS:", tablas.count(), "===")
        if tablas.count():
            tabla = tablas.nth(0)
            headers = [limpiar(h.inner_text()) for h in tabla.locator("th").all()]
            print("HEADERS:", headers)
            filas = tabla.locator("tr").all()
            print("FILAS (incl. header):", len(filas))
            for ri, row in enumerate(filas[1:6]):
                celdas = []
                for c in row.locator("td").all()[:13]:
                    txt = limpiar(c.inner_text())[:18]
                    vals = [i.get_attribute("value") for i in c.locator("input").all()]
                    dis = c.locator("input[disabled], select[disabled]").count()
                    celdas.append(f"{txt!r}{vals if vals else ''}{' dis' if dis else ''}")
                print(f"  fila{ri}: {celdas}")

        # Totales ISFUT visibles en el texto (mensajes de validacion).
        m_h = re.search(r"monto total ISFUT_H:\s*\$?([\d\.\,]+)", body)
        m_a = re.search(r"monto total ISFUT_A:\s*\$?([\d\.\,]+)", body)
        print("\nWEB total ISFUT_H texto:", m_h.group(1) if m_h else "NO ENCONTRADO")
        print("WEB total ISFUT_A texto:", m_a.group(1) if m_a else "NO ENCONTRADO")

        # Botones y acciones.
        print("\n=== BOTONES ===")
        vistos = set()
        for b in page.locator("button, a.btn, input[type=button]").all():
            t = limpiar(b.inner_text())[:30]
            if t and t not in vistos:
                vistos.add(t)
                print("  ", repr(t))

        # Guardar evidencia fresca.
        out_html = config.ARTEFACTOS_DIR / "11_retiros_check.html"
        out_png = config.ARTEFACTOS_DIR / "11_retiros_check.png"
        out_html.write_text(page.content(), encoding="utf-8")
        page.screenshot(path=str(out_png), full_page=True)
        print("\nguardado", out_html.name, "/", out_png.name)
        auth.guardar_sesion(context)
        browser.close()

    # 3) Comparacion de totales.
    print("\n=== COMPARACION ===")
    print(f"backend 1044={r.calculo.v1044} | backend 1045={r.calculo.v1045}")


if __name__ == "__main__":
    main()
