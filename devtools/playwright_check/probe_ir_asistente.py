"""Inspecciona y prueba el boton 'Ir al Asistente' (posible nueva pestana)."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import config


def _llegar_home(page) -> None:
    page.goto(config.QA_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(7000)
    if page.locator("select#periodo").count():
        page.locator("select#periodo").select_option(label="2025")
        page.wait_for_timeout(300)
        page.locator("button", has_text="Siguiente").click()
        page.wait_for_timeout(8000)
    if page.locator("button", has_text="Recuperar datos").count():
        page.locator("button", has_text="Recuperar datos").first.click()
        page.wait_for_timeout(9000)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        _llegar_home(page)
        print("URL home:", page.url)

        btn = page.locator("button", has_text="Ir al Asistente")
        print("boton count:", btn.count())
        if btn.count():
            b = btn.first
            print("tag:", b.evaluate("e => e.tagName"))
            print("type:", b.get_attribute("type"))
            print("disabled:", b.is_disabled())
            print("outerHTML:", b.evaluate("e => e.outerHTML")[:800])

        links = page.locator("a", has_text="Ir al Asistente")
        print("enlaces a count:", links.count())
        for a in links.all():
            print("  a href:", a.get_attribute("href"), "| html:", a.evaluate("e => e.outerHTML")[:400])

        # Probar clic y ver si abre nueva pestana
        target = btn.first if btn.count() else links.first
        target.click()
        page.wait_for_timeout(9000)
        print("\npaginas abiertas:")
        for pg in context.pages:
            print("  -", pg.url)

        browser.close()


if __name__ == "__main__":
    main()
