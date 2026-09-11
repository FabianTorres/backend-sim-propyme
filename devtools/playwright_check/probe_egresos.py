"""Explora la pantalla de Egresos (tras Continuar) para mapear columnas y filas."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import config
import web_scraper


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        web_scraper.llegar_a_ingresos(page)
        web_scraper.aceptar_alertas(page)
        web_scraper.continuar(page)
        web_scraper.aceptar_alertas(page)

        print("URL:", page.url)
        print("Titulo:", page.title())
        print("\n=== texto visible (recortado) ===")
        print(page.locator("body").inner_text()[:4000])

        t = page.locator("table").nth(0)
        ths = t.locator("tr").nth(0).locator("th").all()
        print("\n=== encabezado (%d th) ===" % len(ths))
        for i, th in enumerate(ths):
            print(i, th.evaluate("e => e.outerHTML")[:240].replace("\n", " "))

        # volcar filas de datos con sus inputs
        filas = t.locator("tr").all()
        print("\n=== filas de datos (inputs) ===")
        for ri in range(1, min(len(filas), 6)):
            celdas = filas[ri].locator("td").all()
            print(f"\n-- fila {ri} ({len(celdas)} celdas) --")
            for ci, c in enumerate(celdas):
                txt = (c.inner_text() or "").strip().replace("\n", " ")[:40]
                inputs = c.locator("input").all()
                vals = [inp.get_attribute("value") for inp in inputs]
                if txt or inputs:
                    print(f"  celda {ci}: texto={txt!r} inputs_values={vals}")

        (config.ARTEFACTOS_DIR / "09_egresos.html").write_text(
            page.content(), encoding="utf-8"
        )
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "09_egresos.png"), full_page=True)
        print("\nguardado 09_egresos.html / .png")

        auth.guardar_sesion(context)
        browser.close()


if __name__ == "__main__":
    main()
