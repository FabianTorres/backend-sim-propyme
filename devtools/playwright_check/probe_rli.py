"""Sonda: navega con Recuperar datos hasta la pantalla RLI y vuelca su estructura."""
from __future__ import annotations

from playwright.sync_api import Page, sync_playwright

import auth
import config
import web_scraper


def limpiar(t: str) -> str:
    return " ".join((t or "").split())


def dump(page: Page, etiqueta: str) -> None:
    print("\n==============================", etiqueta)
    print("URL:", page.url)
    print("TITULO:", page.title())
    body = ""
    try:
        body = limpiar(page.locator("body").inner_text())
    except Exception:
        pass
    print("TEXTO:", body[:1800])
    tablas = page.locator("table")
    print("TABLAS:", tablas.count())
    for ti, t in enumerate(tablas.all()[:3]):
        rows = t.locator("tr").all()
        print("  tabla", ti, "filas", len(rows))
        for ri, r in enumerate(rows[:12]):
            celdas = []
            for c in r.locator("th, td").all():
                txt = limpiar(c.inner_text())[:16]
                vals = [i.get_attribute("value") for i in c.locator("input").all()]
                celdas.append(txt + (str(vals) if vals else ""))
            print("   ", ri, celdas)
    print("BOTONES:", [limpiar(b.inner_text())[:24] for b in page.locator("button").all() if limpiar(b.inner_text())])
    print("MODALES visibles:")
    for m in page.locator(".modal, .swal2-popup, [role=dialog]").all():
        if m.is_visible():
            print("   *", limpiar(m.inner_text())[:300])


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        web_scraper.seleccionar_periodo(page)
        web_scraper.elegir_recuperar_datos(page)
        web_scraper.ir_al_asistente(page)
        web_scraper.cerrar_modal_informativo(page)

        for paso in range(7):
            web_scraper.aceptar_alertas(page)
            web_scraper.cerrar_modal_informativo(page)
            dump(page, f"PASO {paso}")
            if web_scraper._es_pantalla_rli(page):
                print("\n>>> RLI DETECTADA en paso", paso)
                break
            try:
                web_scraper.continuar(page)
            except Exception as exc:
                print("no se pudo continuar:", exc)
                break

        (config.ARTEFACTOS_DIR / "12_rli.html").write_text(page.content(), encoding="utf-8")
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "12_rli.png"), full_page=True)
        print("\nguardado 12_rli.html / .png")
        auth.guardar_sesion(context)
        browser.close()


if __name__ == "__main__":
    main()
