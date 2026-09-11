"""Inspecciona los controles de seleccion de periodo (2025/2026 y Siguiente)."""
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

        for texto in ["2026", "2025", "Siguiente"]:
            locs = page.get_by_text(texto, exact=True)
            n = locs.count()
            print(f"\ntexto {texto!r}: {n} coincidencias")
            for i in range(min(n, 10)):
                el = locs.nth(i)
                tag = el.evaluate("e => e.tagName")
                ident = el.get_attribute("id") or ""
                cls = el.get_attribute("class") or ""
                rol = el.get_attribute("role") or ""
                print(f"   [{tag}] id={ident} class={cls[:50]} role={rol}")

        radios = page.locator("input[type=radio]").all()
        print("\nradios:", len(radios))
        for r in radios:
            print(
                "  radio id=",
                r.get_attribute("id"),
                "value=",
                r.get_attribute("value"),
                "checked=",
                r.is_checked(),
            )

        btn = page.locator("button", has_text="Siguiente")
        print("\nboton 'Siguiente':", btn.count())
        for i in range(btn.count()):
            b = btn.nth(i)
            print("  BTN id=", b.get_attribute("id"), "class=", b.get_attribute("class"))

        browser.close()


if __name__ == "__main__":
    main()
