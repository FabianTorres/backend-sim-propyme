"""Inspeccion interactiva: texto visible y elementos interactivos de la pagina actual."""
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
        page.wait_for_timeout(9000)

        print("URL:", page.url)
        print("Titulo:", page.title())

        print("\n=== texto visible del body (recortado) ===")
        texto = page.locator("body").inner_text(timeout=10000)
        print(texto[:5000])

        print("\n=== elementos interactivos ===")
        elementos = page.locator("button, a, input, select").all()
        cont = 0
        for el in elementos:
            tag = el.evaluate("e => e.tagName").upper()
            txt = (el.inner_text() or "").strip()
            ident = el.get_attribute("id") or ""
            cls = el.get_attribute("class") or ""
            ph = el.get_attribute("placeholder") or ""
            href = el.get_attribute("href") or ""
            aria = el.get_attribute("aria-label") or ""
            rol = el.get_attribute("role") or ""
            print(
                f"[{tag}] id={ident} class={cls[:30]} text={txt[:40]!r} "
                f"ph={ph[:26]!r} href={href[:50]!r} aria={aria[:24]!r} role={rol}"
            )
            cont += 1
            if cont >= 150:
                print("  ... (cortado)")
                break

        browser.close()


if __name__ == "__main__":
    main()
