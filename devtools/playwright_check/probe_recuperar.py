"""Continua el flujo: Recuperar datos -> captura la pagina del formulario."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import config


def _seleccionar_periodo(page) -> None:
    page.goto(config.QA_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)
    page.locator("select#periodo").select_option(label="2025")
    page.wait_for_timeout(300)
    page.locator("button", has_text="Siguiente").click()
    page.wait_for_timeout(8000)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        _seleccionar_periodo(page)
        print("URL antes de recuperar:", page.url)

        # Ubicar el control "Recuperar datos"
        for candidato in [
            page.locator("button", has_text="Recuperar datos"),
            page.get_by_text("Recuperar datos", exact=True),
        ]:
            if candidato.count():
                print("encontrado control Recuperar datos (count=%d)" % candidato.count())
                candidato.first.click()
                break
        else:
            print("NO se encontro 'Recuperar datos'")

        page.wait_for_timeout(15000)
        print("\nURL final:", page.url)
        print("Titulo:", page.title())
        print("\n=== texto visible ===")
        print(page.locator("body").inner_text()[:8000])

        (config.ARTEFACTOS_DIR / "05_formulario.html").write_text(
            page.content(), encoding="utf-8"
        )
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "05_formulario.png"), full_page=True)
        print("\nguardado 05_formulario.html / .png")

        browser.close()


if __name__ == "__main__":
    main()
