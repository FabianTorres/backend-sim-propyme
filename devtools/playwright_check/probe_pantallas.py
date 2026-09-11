"""Sonda de pantallas del asistente: botones, modales y tablas (para mapear selectores)."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import config
import web_scraper


def dump_botones(page) -> None:
    print("\n=== botones <button> ===")
    for b in page.locator("button").all():
        txt = (b.inner_text() or "").strip().replace("\n", " ")
        print(
            f"  id={b.get_attribute('id')} class={(b.get_attribute('class') or '')[:30]} "
            f"text={txt[:40]!r}"
        )


def dump_modales(page) -> None:
    print("\n=== modales ===")
    for m in page.locator(".modal").all():
        vis = "visible" if m.is_visible() else "oculto"
        txt = (m.inner_text() or "").strip().replace("\n", " ")[:300]
        print(f"  [{vis}] {txt}")


def dump_tablas(page) -> None:
    print("\n=== tablas ===")
    for ti, t in enumerate(page.locator("table").all()):
        rows = t.locator("tr").all()
        print(f"\n--- tabla {ti}: {len(rows)} filas ---")
        for ri, r in enumerate(rows[:50]):
            celdas = [(c.inner_text() or "").strip().replace("\n", " ") for c in r.locator("th, td").all()]
            print(f"  {ri}: {celdas}")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        web_scraper.llegar_a_ingresos(page)

        print("URL:", page.url)
        print("Titulo:", page.title())
        print("\n=== texto visible (recortado) ===")
        print(page.locator("body").inner_text()[:4000])

        dump_botones(page)
        dump_modales(page)
        dump_tablas(page)

        (config.ARTEFACTOS_DIR / "08_ingresos.html").write_text(
            page.content(), encoding="utf-8"
        )
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "08_ingresos.png"), full_page=True)
        print("\nguardado 08_ingresos.html / .png")

        auth.guardar_sesion(context)
        browser.close()


if __name__ == "__main__":
    main()
