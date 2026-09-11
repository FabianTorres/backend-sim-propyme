"""Flujo completo hasta entrar al asistente y capturar la pagina del formulario."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import config


def _click_si_existe(page, texto: str, selector: str = "button") -> bool:
    loc = page.locator(selector, has_text=texto)
    if loc.count():
        loc.first.click()
        return True
    return False


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        # 1) Periodo
        page.goto(config.QA_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(7000)
        if page.locator("select#periodo").count():
            page.locator("select#periodo").select_option(label="2025")
            page.wait_for_timeout(300)
            _click_si_existe(page, "Siguiente")
            page.wait_for_timeout(8000)
        print("paso periodo ->", page.url)

        # 2) Recuperar datos
        if _click_si_existe(page, "Recuperar datos"):
            page.wait_for_timeout(9000)
        print("paso recuperar ->", page.url)

        # 3) Ir al Asistente
        if _click_si_existe(page, "Ir al Asistente"):
            page.wait_for_timeout(15000)
        print("paso al asistente ->", page.url)

        print("\nTitulo:", page.title())
        print("\n=== texto visible ===")
        print(page.locator("body").inner_text()[:8000])

        (config.ARTEFACTOS_DIR / "06_asistente.html").write_text(
            page.content(), encoding="utf-8"
        )
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "06_asistente.png"), full_page=True)
        print("\nguardado 06_asistente.html / .png")

        auth.guardar_sesion(context)
        browser.close()


if __name__ == "__main__":
    main()
