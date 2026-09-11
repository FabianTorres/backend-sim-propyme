"""Navegacion del asistente propyme (QA) y extraccion de celdas de Ingresos/Egresos.

Flujo real (ambiente QA, datos ficticios):
1. Seleccionar anio tributario 2026.
2. Elegir 'Nueva informacion'.
3. Home intermedio -> enlace 'Ir al Asistente'.
4. Primera pantalla del asistente (Ingresos) con alertas informativas (aceptar).
5. Para pasar a Egresos: boton 'Continuar'.
"""
from __future__ import annotations

from playwright.sync_api import Page

import config


def _login_si_hace_falta(page: Page) -> None:
    """Si aparece la bifurcacion de auth, hace login con Clave Tributaria."""
    if page.locator("#loginClaveTributaria").count():
        page.click("#loginClaveTributaria")
        page.wait_for_selector("#inputRut", timeout=30000)
        page.fill("#inputRut", config.RUT)
        page.fill("#inputPass", config.CLAVE)
        page.click("#bt_ingresar")
        page.wait_for_url("**asistente-propyme**", timeout=60000)
        page.wait_for_timeout(4000)


def seleccionar_periodo(page: Page) -> None:
    """Inicia sesion (si hace falta) y selecciona el anio tributario 2026."""
    page.goto(config.QA_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    _login_si_hace_falta(page)
    if page.locator("select#periodo").count():
        page.locator("select#periodo").select_option(label="2026")
        page.wait_for_timeout(300)
        page.locator("button", has_text="Siguiente").click()
        page.wait_for_timeout(6000)


def elegir_nueva_informacion(page: Page) -> None:
    """En la pantalla de recuperar informacion, elige 'Nueva informacion'."""
    loc = page.locator("button, a", has_text="Nueva")
    if loc.count():
        loc.first.click()
        page.wait_for_timeout(8000)


def ir_al_asistente(page: Page) -> None:
    """Desde el Home, presiona el enlace 'Ir al Asistente'."""
    page.locator("a", has_text="Ir al Asistente").first.click()
    page.wait_for_timeout(12000)


def cerrar_modal_informativo(page: Page) -> None:
    """Cierra modales informativos visibles (Cerrar / Aceptar / Entendido)."""
    try:
        modales = page.locator(".modal")
        for i in range(modales.count()):
            modal = modales.nth(i)
            if not modal.is_visible():
                continue
            for texto in ("Cerrar", "Aceptar", "Entendido"):
                boton = modal.locator(f"button, a", has_text=texto).first
                if boton.count() and boton.is_visible():
                    boton.click()
                    page.wait_for_timeout(800)
                    return
    except Exception:
        pass


def continuar(page: Page) -> None:
    """Avanza con el boton Continuar (hacia la siguiente pantalla del asistente)."""
    page.locator("button", has_text="Continuar").first.click()
    page.wait_for_timeout(10000)


def llegar_a_ingresos(page: Page) -> None:
    """Ejecuta el flujo completo hasta la pantalla de Ingresos."""
    seleccionar_periodo(page)
    elegir_nueva_informacion(page)
    ir_al_asistente(page)
    cerrar_modal_informativo(page)
    # Si aterriza en la sub-pantalla de ingreso diferido (parte de Ingresos), avanzar.
    if "ingreso-diferido" in page.url:
        continuar(page)
        cerrar_modal_informativo(page)


def aceptar_alertas(page: Page, veces: int = 5) -> None:
    """Acepta alertas SweetAlert2 (boton Aceptar) que puedan aparecer."""
    for _ in range(veces):
        confirm = page.locator(".swal2-confirm")
        if confirm.count() and confirm.first.is_visible():
            confirm.first.click()
            page.wait_for_timeout(900)
        else:
            break


def _leer_valor_celda(fila, celda_idx: int) -> str:
    """Lee el valor de una celda (input > texto). Vacio -> cadena vacia."""
    celdas = fila.locator("td").all()
    if celda_idx >= len(celdas):
        return ""
    celda = celdas[celda_idx]
    inp = celda.locator("input")
    if inp.count():
        return (inp.first.get_attribute("value") or "").strip()
    return (celda.inner_text() or "").strip()


def leer_tabla(page: Page, orden: list[str], columnas: dict[str, int]) -> dict:
    """Lee una tabla del asistente y devuelve {codigo: {columna: texto}}."""
    tabla = page.locator("table").nth(0)
    filas = tabla.locator("tr").all()
    resultado: dict = {}
    for idx, codigo in enumerate(orden):
        if idx + 1 >= len(filas):
            continue
        tr = filas[idx + 1]  # la fila 0 es el encabezado
        fila: dict = {}
        for col, celda_idx in columnas.items():
            fila[col] = _leer_valor_celda(tr, celda_idx)
        resultado[codigo] = fila
    return resultado


def leer_tabla_ingresos(page: Page) -> dict:
    """Lee la tabla de Ingresos y devuelve {codigo: {columna: texto}}."""
    from mapeo_campos import COLUMNAS_INGRESOS, ORDEN_INGRESOS

    return leer_tabla(page, ORDEN_INGRESOS, COLUMNAS_INGRESOS)


def leer_tabla_egresos(page: Page) -> dict:
    """Lee la tabla de Egresos y devuelve {codigo: {columna: texto}}."""
    from mapeo_campos import COLUMNAS_EGRESOS, ORDEN_EGRESOS

    return leer_tabla(page, ORDEN_EGRESOS, COLUMNAS_EGRESOS)
