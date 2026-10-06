"""Diagnostico: compara Ingresos/Egresos de la web (Recuperar datos) vs backend."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

import auth
import backend_client
import comparador
import config
import web_scraper
from mapeo_campos import CAMPOS_EGRESOS, CAMPOS_INGRESOS


def main() -> None:
    resp = backend_client.calcular(backend_client.cargar_caso())
    filtros_ing = {f["codigo"]: f for f in resp["ingresos"]["filas"]}
    filtros_egr = {f["codigo"]: f for f in resp["egresos"]["filas"]}
    print("BACKEND total7 =", resp["ingresos"]["totales"]["fila_7_total"])
    print("BACKEND total8 =", resp["egresos"]["totales"]["fila_8_total"])

    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()
        web_scraper.llegar_a_ingresos(page, modo="recuperar")
        web_scraper.aceptar_alertas(page)
        ing = web_scraper.leer_tabla_ingresos(page)
        web_scraper.continuar(page)
        web_scraper.aceptar_alertas(page)
        egr = web_scraper.leer_tabla_egresos(page)
        browser.close()

    dif_ing = comparador.comparar_modulo(resp["ingresos"]["filas"], ing, CAMPOS_INGRESOS)
    print("\n=== INGRESOS diffs:", len(dif_ing))
    for d in dif_ing:
        print("  ", d["codigo"], d["columna"], "web=", d["valor_web"], "back=", d["valor_backend"], d["tipo"])
    dif_egr = comparador.comparar_modulo(resp["egresos"]["filas"], egr, CAMPOS_EGRESOS)
    print("\n=== EGRESOS diffs:", len(dif_egr))
    for d in dif_egr:
        print("  ", d["codigo"], d["columna"], "web=", d["valor_web"], "back=", d["valor_backend"], d["tipo"])


if __name__ == "__main__":
    main()
