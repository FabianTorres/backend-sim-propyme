"""Inspecciona la estructura de inputs de la tabla de Ingresos."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import config
import web_scraper


def aceptar_alertas(page) -> None:
    for _ in range(4):
        confirm = page.locator(".swal2-confirm")
        if confirm.count() and confirm.first.is_visible():
            confirm.first.click()
            page.wait_for_timeout(900)
        else:
            break


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        web_scraper.llegar_a_ingresos(page)
        aceptar_alertas(page)

        print("URL:", page.url)

        tabla = page.locator("table").nth(0)
        filas = tabla.locator("tr").all()
        print("num filas:", len(filas))
        for ri, r in enumerate(filas):
            celdas = r.locator("td, th").all()
            print(f"\n== fila {ri} ({len(celdas)} celdas) ==")
            for ci, c in enumerate(celdas):
                txt = (c.inner_text() or "").strip().replace("\n", " ")
                inputs = c.locator("input").all()
                infos = []
                for inp in inputs:
                    attrs = inp.evaluate(
                        "e => Array.from(e.attributes).reduce((o,a)=>(o[a.name]=a.value,o),{})"
                    )
                    infos.append(attrs)
                if txt or inputs:
                    print(f"  celda {ci}: texto={txt[:46]!r}")
                    for a in infos:
                        print(f"       input={a}")

        browser.close()


if __name__ == "__main__":
    main()
