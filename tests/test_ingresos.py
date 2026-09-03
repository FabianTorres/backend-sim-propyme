"""Pruebas unitarias del modulo 'Ingresos' (Pagina 1 del 14D1).

Verifica los calculos del servicio usando fixtures compartidos desde conftest:
    - Fila 7.1 (Exportaciones)
    - Fila 7.15 (Arriendos de bienes raices)
    - Totalizador 7.12 (Total Ingresos por ventas y servicios)
    - Totalizador 7 (TOTAL INGRESOS)
    - Funcion POS()
"""
from decimal import Decimal

from app.services.ingresos import IngresosService
from app.utils.matematicas import POS


def _fila(response, codigo):
    return next(f for f in response.filas if f.codigo == codigo)


def test_pos_funcion():
    assert POS(Decimal("500")) == Decimal("500")
    assert POS(Decimal("0")) == Decimal("0")
    assert POS(Decimal("-500")) == Decimal("0")
    assert POS(Decimal("100.50")) == Decimal("100.50")


def test_fila_7_1_exportaciones(datos_ingresos):
    """B = MAX(Vx012188; Vx013384+...) y F = POS(B-C-D-E)."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=False)
    fila = _fila(response, "7.1")

    # MAX(1_000_000; 100_000) = 1_000_000
    assert fila.ingresos_ano == Decimal("1000000")
    # POS(1_000_000 - 0 - 0 - 0) = 1_000_000
    assert fila.monto_ingreso_percibido == Decimal("1000000")


def test_fila_7_15_arriendos_bienes_raices(datos_ingresos):
    """Con Calc4064=0 y Calc4075=0, B=Vx012209 y F sale 0."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=False)
    fila = _fila(response, "7.15")

    assert fila.ingresos_ano == Decimal("0")
    assert fila.monto_ingreso_percibido == Decimal("0")


def test_totalizador_7_12(datos_ingresos):
    """= POS(7.1+7.2+7.3+7.4+7.5+7.6+7.7-7.8+7.9+7.11) sobre Columna F (Monto Ingreso Percibido)."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=False)
    assert response.totales.fila_7_12 == Decimal("4080000")


def test_total_7(datos_ingresos):
    """Total = 7.12 + 7.13 + ... + 7.27 + 7.10 sobre Columna F (Monto Ingreso Percibido)."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=False)
    assert response.totales.fila_7_total == Decimal("4920000")


def test_override_columna_h(datos_ingresos):
    """El override manual de la Col. H prevalece sobre el vector original."""
    v, e, d = datos_ingresos
    # Vx014255 = 50000, pero el usuario sobreescribe 7.1 a 99999
    d.ingresos_adeudados_at_anterior["7.1"] = Decimal("99999")
    d.ingresos_adeudados_at_anterior["7.2"] = Decimal("88888")

    response = IngresosService().calcular(v, e, d, mostrar_formulas=False)
    fila71 = _fila(response, "7.1")
    fila72 = _fila(response, "7.2")

    assert fila71.ingresos_adeudados_at_anterior == Decimal("99999")
    assert fila72.ingresos_adeudados_at_anterior == Decimal("88888")
    # Fila sin override conserva el vector original
    fila73 = _fila(response, "7.3")
    assert fila73.ingresos_adeudados_at_anterior == Decimal("0")


def test_override_col_b(datos_ingresos):
    """Override de filas editables de Col. B prevalece sobre la formula."""
    v, e, d = datos_ingresos
    # Base 90000 (7.14); override a 55555
    d.ingresos_ano["7.14"] = Decimal("55555")
    d.ingresos_ano["7.19"] = Decimal("44444")
    d.ingresos_ano["7.20"] = Decimal("66666")

    response = IngresosService().calcular(v, e, d, mostrar_formulas=False)
    assert _fila(response, "7.14").ingresos_ano == Decimal("55555")
    assert _fila(response, "7.19").ingresos_ano == Decimal("44444")
    assert _fila(response, "7.20").ingresos_ano == Decimal("66666")

    # Ruta no editable: la formula original se mantiene


def test_totalizador_7_12_columnas_cde(datos_ingresos):
    """7.12 suma C, D y E de las filas 7.1 a 7.11 usando POS(...)."""
    v, e, d = datos_ingresos
    d.monto_no_percibido["7.1"] = Decimal("10000")
    d.monto_no_percibido["7.2"] = Decimal("20000")
    d.monto_no_percibido["7.8"] = Decimal("50000")
    d.no_considerar_patrimonio["7.1"] = Decimal("5000")
    d.no_considerar_patrimonio["7.9"] = Decimal("15000")
    d.factura_renta_presunta["7.3"] = Decimal("25000")
    d.factura_renta_presunta["7.8"] = Decimal("10000")

    response = IngresosService().calcular(v, e, d, mostrar_formulas=False)
    fila = _fila(response, "7.12")

    # C = 10000 + 20000 - 50000 = -20000 => POS = 0
    assert fila.monto_no_percibido == Decimal("0")
    # D = 5000 + 15000 = 20000
    assert fila.no_considerar_patrimonio == Decimal("20000")
    # E = 25000 - 10000 = 15000
    assert fila.factura_renta_presunta == Decimal("15000")


def test_fila_7_sin_columnas_cde(datos_ingresos):
    """La fila total 7 no expone columnas C, D ni E."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=False)
    fila = _fila(response, "7")
    assert fila.monto_no_percibido is None
    assert fila.no_considerar_patrimonio is None
    assert fila.factura_renta_presunta is None
    assert _fila(response, "7.1").ingresos_ano == Decimal("1000000")