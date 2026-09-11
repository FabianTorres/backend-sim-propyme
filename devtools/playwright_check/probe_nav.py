"""Navega: selecciona periodo 2025 y Siguiente; captura la pagina siguiente."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import config


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        page.goto(config.QA_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)

        select = page.locator("select")
        print("selects:", select.count())
        for i in range(select.count()):
            s = select.nth(i)
            print(
                "select",
                i,
                "id=",
                s.get_attribute("id"),
                "name=",
                s.get_attribute("name"),
            )
            for o in s.locator("option").all():
                print(
                    "   option value=",
                    o.get_attribute("value"),
                    "texto=",
                    (o.inner_text() or "").strip(),
                )

        # elegir 2025 en el primer select que lo contenga
        select.nth(0).select_option(label="2025")
        page.wait_for_timeout(500)

        page.locator("button", has_text="Siguiente").click()
        page.wait_for_timeout(12000)

        print("\nURL:", page.url)
        print("Titulo:", page.title())
        print("\n=== texto visible ===")
        print(page.locator("body").inner_text()[:6000])

        (config.ARTEFACTOS_DIR / "04_despues_periodo.html").write_text(
            page.content(), encoding="utf-8"
        )
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "04_despues_periodo.png"), full_page=True)
        print("\nguardado 04_despues_periodo.html / .png")

        browser.close()


if __name__ == "__main__":
    main()
