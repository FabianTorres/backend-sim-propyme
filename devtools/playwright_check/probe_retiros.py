"""Explora la pantalla de Retiros (tras Egresos) para mapear su estructura."""
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
        web_scraper.continuar(page)  # -> Egresos
        web_scraper.aceptar_alertas(page)
        web_scraper.continuar(page)  # -> Retiros
        web_scraper.aceptar_alertas(page)

        print("URL:", page.url)
        print("TITULO:", page.title())

        print("\n=== TEXTO VISIBLE ===")
        print(page.locator("body").inner_text()[:9000])

        tablas = page.locator("table")
        print("\n=== TABLAS:", tablas.count(), "===")
        for ti, t in enumerate(tablas.all()):
            rows = t.locator("tr").all()
            print(f"\n-- tabla {ti}: {len(rows)} filas --")
            for ri, r in enumerate(rows[:15]):
                celdas = []
                for c in r.locator("th, td").all():
                    txt = (c.inner_text() or "").strip().replace("\n", " ")[:20]
                    inputs = c.locator("input").all()
                    vals = [i.get_attribute("value") for i in inputs]
                    celdas.append(f"{txt!r}{vals if vals else ''}")
                print(f"  {ri}: {celdas}")

        print("\n=== BOTONES ===")
        for b in page.locator("button").all():
            print(
                "  ",
                (b.inner_text() or "").strip()[:28],
                "| id=",
                b.get_attribute("id"),
                "| class=",
                (b.get_attribute("class") or "")[:34],
            )

        (config.ARTEFACTOS_DIR / "10_retiros.html").write_text(
            page.content(), encoding="utf-8"
        )
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "10_retiros.png"), full_page=True)
        print("\nguardado 10_retiros.html / .png")

        auth.guardar_sesion(context)
        browser.close()


if __name__ == "__main__":
    main()
