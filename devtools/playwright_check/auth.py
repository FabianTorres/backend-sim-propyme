"""Login en el SII QA con Clave Tributaria (sin captcha).

Flujo real observado:
1. /bifurcacion -> clic en #loginClaveTributaria
2. redirige a /oauthsii-v1 (formulario: #inputRut + #inputPass + #bt_ingresar)
3. vuelve al asistente propyme (originalUrl).
"""
from __future__ import annotations

from playwright.sync_api import Browser, BrowserContext, Page

import config


def nuevo_contexto(browser: Browser) -> BrowserContext:
    """Crea un contexto nuevo, SIN reusar sesion previa.

    No se reutiliza storage_state a proposito: el servidor del SII recuerda el
    paso del asistente y reusar cookies retoma la navegacion en una pagina
    intermedia (rompe el flujo). Se hace login limpio en cada corrida.
    """
    return browser.new_context(ignore_https_errors=True)


def login_clave_tributaria(page: Page) -> None:
    """Navega por el flujo completo de Clave Tributaria hasta volver al asistente."""
    # 1) Bifurcacion de autenticacion: elegir Clave Tributaria
    page.goto(config.QA_URL, wait_until="load", timeout=60000)
    page.wait_for_selector("#loginClaveTributaria", timeout=30000)
    page.wait_for_timeout(1200)
    page.click("#loginClaveTributaria")

    # 2) Formulario OAuth de Clave Tributaria (RUT + clave)
    page.wait_for_selector("#inputRut", timeout=30000)
    page.fill("#inputRut", config.RUT)
    page.fill("#inputPass", config.CLAVE)
    page.click("#bt_ingresar")

    # 3) Esperar a volver al asistente propyme
    page.wait_for_url("**asistente-propyme**", timeout=60000)
    page.wait_for_timeout(5000)


def guardar_sesion(context: BrowserContext) -> None:
    """Persiste cookies/localStorage para reutilizar en la proxima corrida."""
    config.ARTEFACTOS_DIR.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=str(config.STORAGE_STATE))
    print("sesion guardada en", config.STORAGE_STATE)
