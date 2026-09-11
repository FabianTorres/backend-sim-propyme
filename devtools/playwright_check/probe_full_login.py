"""Prueba el login completo y captura la pagina de destino del asistente."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import config


def main() -> None:
    config.ARTEFACTOS_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        auth.login_clave_tributaria(page)

        print("URL final:", page.url)
        print("Titulo:", page.title())

        (config.ARTEFACTOS_DIR / "03_asistente.html").write_text(
            page.content(), encoding="utf-8"
        )
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "03_asistente.png"), full_page=True)

        auth.guardar_sesion(context)

        browser.close()


if __name__ == "__main__":
    main()
