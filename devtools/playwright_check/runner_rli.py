r"""Runner dev: navega hasta RLI y compara web vs backend.

Uso:
    venv\Scripts\python.exe runner_rli.py si  [nueva|recuperar]  [caso.json]
    venv\Scripts\python.exe runner_rli.py no  [nueva|recuperar]  [caso.json]

La diferencia +/-2 se marca OK(+/-2): es el redondeo conocido del SII.
"""
from __future__ import annotations

import re
import sys
from decimal import Decimal

from playwright.sync_api import Page, sync_playwright

import auth
import backend_client
import config
import web_scraper
from normalizar import a_decimal

CAMPOS_RLI = {
    "9": "v9",
    "9.21": "v9_21",
    "9.1": "v9_1",
    "9.2": "v9_2",
    "9.3": "v9_3",
    "9.4": "v9_4",
    "9.5": "v9_5",
    "9.6": "v9_6",
}

TOLERANCIA = Decimal("2")


def limpiar(t: str) -> str:
    return " ".join((t or "").split())


def leer_rli(page: Page) -> dict:
    """Lee las tablas del cuadro RLI -> {codigo: monto_texto} (primer valor)."""
    out: dict = {}
    for t in page.locator("table").all():
        for r in t.locator("tr").all():
            celdas = r.locator("td").all()
            if len(celdas) < 2:
                continue
            concepto = limpiar(celdas[0].inner_text())
            m = re.match(r"(9(?:\.\d+)?)\b", concepto)
            if not m:
                continue
            codigo = m.group(1)
            monto = web_scraper._leer_valor_celda(r, len(celdas) - 1)
            if codigo not in out and monto != "":
                out[codigo] = monto
    return out


def _modal_14e_visible(page: Page):
    """Devuelve el Locator del modal 14E si esta VISIBLE, si no None."""
    for m in page.locator(".modal").all():
        try:
            if not m.is_visible():
                continue
            texto = m.inner_text()
            if "14 E" in texto or "acogerse" in texto:
                return m
        except Exception:
            continue
    return None


def responder_14e(page: Page, respuesta: str) -> None:
    """Responde el modal 14E visible con 'SI' o 'NO'."""
    modal = _modal_14e_visible(page)
    if modal is None:
        return
    modal.locator("button", has_text=respuesta).first.click()
    page.wait_for_timeout(6000)
    web_scraper.aceptar_alertas(page)


def main() -> None:
    args = [a.lower() for a in sys.argv[1:]]
    acoge = args[0] if len(args) > 0 else "si"
    modo = args[1] if len(args) > 1 else "recuperar"
    caso_path = next((a for a in sys.argv[2:] if a.lower().endswith(".json")), None)
    sinretiros = "sinretiros" in args
    respuesta = "SI" if acoge == "si" else "NO"

    caso = backend_client.cargar_caso(caso_path)
    if sinretiros:
        caso.setdefault("digitados", {}).setdefault("retiros", {})["filas"] = []
    resp = backend_client.calcular(caso)
    rli_be = resp["rli"]

    with sync_playwright() as p:
        browser = p.chromium.launch(channel=config.BROWSER_CHANNEL, headless=config.HEADLESS)
        context = auth.nuevo_contexto(browser)
        page = context.new_page()

        web_scraper.llegar_a_ingresos(page, modo=modo)
        web_scraper.cerrar_modal_informativo(page)
        web_scraper.ir_a_rli(page)
        web_scraper.aceptar_alertas(page)

        url = page.url
        web_prev = leer_rli(page)
        print("modo:", modo, "| URL RLI:", url)
        print("WEB provisional:", web_prev)

        if _modal_14e_visible(page) is not None:
            print("Modal 14E visible -> respondiendo", respuesta)
            responder_14e(page, respuesta)
        else:
            print("Modal 14E NO visible")

        web_post = leer_rli(page)
        print("WEB tras responder %s:" % respuesta, web_post)

        page.screenshot(path=str(config.ARTEFACTOS_DIR / ("13_rli_%s_%s.png" % (modo, acoge))), full_page=True)
        (config.ARTEFACTOS_DIR / ("13_rli_%s_%s.html" % (modo, acoge))).write_text(page.content(), encoding="utf-8")
        auth.guardar_sesion(context)
        browser.close()

    lineas = ["# RLI web(%s) vs backend  -  acoge_14e=%s" % (modo, acoge), ""]
    lineas.append("URL: %s" % url)
    lineas.append("")
    lineas.append("| Codigo | Web | Backend | dif | Estado |")
    lineas.append("|---|---|---|---|---|")
    ok_total = 0
    tot = 0
    for codigo, campo in CAMPOS_RLI.items():
        if codigo not in web_post:
            continue
        wd = a_decimal(web_post[codigo])
        bd = Decimal(str(rli_be[campo]))
        dif = wd - bd
        tot += 1
        if dif == 0:
            estado = "OK"
        elif abs(dif) <= TOLERANCIA:
            estado = "OK(+/-2)"
        else:
            estado = "DIF"
        ok_total += 1 if estado != "DIF" else 0
        lineas.append("| %s | %s | %s | %s | %s |" % (codigo, wd, bd, dif, estado))
    lineas.append("")
    lineas.append("Cuadro backend: %s | condicion_ok=%s" % (rli_be["cuadro"], rli_be["condicion_ok"]))
    lineas.append("Total coincidencias (tol +/-2): %d/%d" % (ok_total, tot))
    out = config.ARTEFACTOS_DIR / ("reporte_rli_%s_%s.md" % (modo, acoge))
    out.write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas))
    print("\nguardado", out.name)


if __name__ == "__main__":
    main()
