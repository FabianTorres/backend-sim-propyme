"""Runner del checker de desarrollo: compara web QA vs backend (Ingresos y Egresos)."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import backend_client
import comparador
import config
import reporte
import web_scraper
from mapeo_campos import (
    CAMPOS_EGRESOS,
    CAMPOS_INGRESOS,
    FILAS_REAJUSTE_EGRESOS,
)


def main() -> None:
    # 1) Valores esperados del backend (oraculo)
    payload = backend_client.cargar_caso()
    resp = backend_client.calcular(payload)

    # 2) Lectura de la web QA (una sola sesion: ingresos luego egresos)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        web_scraper.llegar_a_ingresos(page)
        web_scraper.aceptar_alertas(page)
        lectura_ingresos = web_scraper.leer_tabla_ingresos(page)

        web_scraper.continuar(page)
        web_scraper.aceptar_alertas(page)
        lectura_egresos = web_scraper.leer_tabla_egresos(page)

        auth.guardar_sesion(context)
        browser.close()

    # 3) Comparar y reportar Ingresos
    dif_ing = comparador.comparar_modulo(
        resp["ingresos"]["filas"], lectura_ingresos, CAMPOS_INGRESOS
    )
    tot_ing = comparador.contar_comparadas(resp["ingresos"]["filas"], lectura_ingresos, CAMPOS_INGRESOS)
    reporte.generar("Ingresos", dif_ing, tot_ing, config.ARTEFACTOS_DIR / "reporte_ingresos.md")

    # 4) Comparar y reportar Egresos
    dif_egr = comparador.comparar_modulo(
        resp["egresos"]["filas"],
        lectura_egresos,
        CAMPOS_EGRESOS,
        reajuste=FILAS_REAJUSTE_EGRESOS,
        total="8",
    )
    tot_egr = comparador.contar_comparadas(resp["egresos"]["filas"], lectura_egresos, CAMPOS_EGRESOS)
    reporte.generar("Egresos", dif_egr, tot_egr, config.ARTEFACTOS_DIR / "reporte_egresos.md")


if __name__ == "__main__":
    main()

