"""Pruebas unitarias del modulo 'Ingresos' (Pagina 1 del 14D1).

Carga el mock de datos y verifica los calculos del servicio:
    - Fila 7.1 (Exportaciones)
    - Fila 7.15 (Arriendos de bienes raices)
    - Totalizador 7.12 (Total Ingresos por ventas y servicios)
    - Totalizador 7 (TOTAL INGRESOS)
    - Funcion POS()
"""
import json
from decimal import Decimal
from pathlib import Path

from app.schemas.ingresos import IngresosRequest
from app.services.ingresos import POS, IngresosService

MOCK_PATH = Path(__file__).resolve().parents[1] / "app" / "db" / "mocks" / "mock_ingresos.json"


def _construir_request() -> IngresosRequest:
    """Carga el mock JSON y lo valida contra el schema de entrada."""
    with open(MOCK_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    return IngresosRequest.model_validate(data)


def _fila(response, codigo):
    return next(f for f in response.filas if f.codigo == codigo)


def test_pos_funcion():
    assert POS(Decimal("500")) == Decimal("500")
    assert POS(Decimal("0")) == Decimal("0")
    assert POS(Decimal("-500")) == Decimal("0")
    assert POS(Decimal("100.50")) == Decimal("100.50")


def test_fila_7_1_exportaciones():
    """B = MAX(Vx012188; Vx013384+...) y F = POS(B-C-D-E)."""
    response = IngresosService().calcular(_construir_request())
    fila = _fila(response, "7.1")

    # MAX(1_000_000; 100_000) = 1_000_000
    assert fila.ingresos_ano == Decimal("1000000")
    # POS(1_000_000 - 0 - 0 - 0) = 1_000_000
    assert fila.monto_ingreso_percibido == Decimal("1000000")


def test_fila_7_15_arriendos_bienes_raices():
    """Con Calc4064=0 y Calc4075=0, B=Vx012209 y F sale 0."""
    response = IngresosService().calcular(_construir_request())
    fila = _fila(response, "7.15")

    assert fila.ingresos_ano == Decimal("0")
    assert fila.monto_ingreso_percibido == Decimal("0")


def test_totalizador_7_12():
    """= POS(7.1+7.2+7.3+7.4+7.5+7.6+7.7-7.8+7.9+7.11)."""
    response = IngresosService().calcular(_construir_request())
    assert response.totales.fila_7_12 == Decimal("4180000")


def test_total_7():
    """Total = 7.12 + 7.13 + ... + 7.27 + 7.10."""
    response = IngresosService().calcular(_construir_request())
    assert response.totales.fila_7_total == Decimal("5020000")