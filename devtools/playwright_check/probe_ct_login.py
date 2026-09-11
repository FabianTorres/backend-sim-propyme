"""Segundo paso: clic en Clave Tributaria y captura de la pagina resultante."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import config


def main() -> None:
    config.ARTEFACTOS_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        page.goto(config.QA_URL, wait_until="load", timeout=60000)
        page.wait_for_selector("#loginClaveTributaria", timeout=30000)
        page.wait_for_timeout(1500)  # asegura que el handler 'load' ya seteo originalUrl

        page.click("#loginClaveTributaria")
        page.wait_for_timeout(12000)

        print("URL tras click CT:", page.url)
        print("Titulo:", page.title())
        print("Paginas abiertas:", len(context.pages))

        (config.ARTEFACTOS_DIR / "02_ct_login.html").write_text(
            page.content(), encoding="utf-8"
        )
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "02_ct_login.png"), full_page=True)
        print("guardado 02_ct_login.html / 02_ct_login.png")

        browser.close()


if __name__ == "__main__":
    main()
