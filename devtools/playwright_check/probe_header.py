"""Inspecciona colspan e inputs del encabezado y de filas representativas de Ingresos."""
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

        web_scraper.llegar_a_ingresos(page)
        for _ in range(4):
            c = page.locator(".swal2-confirm")
            if c.count() and c.first.is_visible():
                c.first.click()
                page.wait_for_timeout(900)
            else:
                break

        t = page.locator("table").nth(0)
        ths = t.locator("tr").nth(0).locator("th").all()
        print("TH cantidad:", len(ths))
        for i, th in enumerate(ths):
            print(i, th.evaluate("e => e.outerHTML")[:300].replace("\n", " "))

        for ri in (1, 12, 16):
            tds = t.locator("tr").nth(ri).locator("td").all()
            print(f"\n=== fila {ri} ({len(tds)} td) ===")
            for ci, td in enumerate(tds):
                print(ci, td.evaluate("e => e.outerHTML")[:260].replace("\n", " "))

        browser.close()


if __name__ == "__main__":
    main()
