"""Sonda de login y DOM para descubrir selectores del SII QA.

Guarda el HTML y un screenshot de la pagina de login para poder definir,
en una pasada posterior, los selectores de "clave tributaria", RUT y clave.

Usa el navegador del sistema (Edge/Chrome) para no requerir descargar Chromium.
"""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

import config


def _guardar_archivo(ruta: Path, contenido: str) -> None:
    ruta.write_text(contenido, encoding="utf-8")
    print(f"guardado: {ruta}")


def main() -> None:
    config.ARTEFACTOS_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        page.goto(config.QA_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(6000)

        print("Titulo:", page.title())
        print("URL final:", page.url)

        _guardar_archivo(config.ARTEFACTOS_DIR / "01_login.html", page.content())
        page.screenshot(path=str(config.ARTEFACTOS_DIR / "01_login.png"), full_page=True)

        browser.close()


if __name__ == "__main__":
    main()
