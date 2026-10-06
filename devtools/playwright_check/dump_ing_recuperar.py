"""Dump completo de la tabla de Ingresos recuperada (para hallar el valor gigante)."""
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
        web_scraper.llegar_a_ingresos(page, modo="recuperar")
        web_scraper.aceptar_alertas(page)
        t = page.locator("table").nth(0)
        for ri, r in enumerate(t.locator("tr").all()):
            celdas = r.locator("td").all()
            if not celdas:
                continue
            concepto = " ".join(celdas[0].inner_text().split())[:34]
            vals = []
            for c in celdas[1:]:
                inp = c.locator("input")
                if inp.count():
                    vals.append(inp.first.get_attribute("value"))
            print(ri, repr(concepto), vals)
        browser.close()


if __name__ == "__main__":
    main()
