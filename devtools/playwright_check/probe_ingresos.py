"""Captura la primera pantalla del flujo 14D1 (ingreso-diferido-14D1)."""
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

        web_scraper.llegar_al_asistente(page)
        print("URL:", page.url)
        print("Titulo:", page.title())
        print("\n=== texto visible ===")
        print(page.locator("body").inner_text()[:8000])

        (config.ARTEFACTOS_DIR / "07_pantalla_14d1.html").write_text(
            page.content(), encoding="utf-8"
        )
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "07_pantalla_14d1.png"), full_page=True)
        print("\nguardado 07_pantalla_14d1.html / .png")

        browser.close()


if __name__ == "__main__":
    main()
