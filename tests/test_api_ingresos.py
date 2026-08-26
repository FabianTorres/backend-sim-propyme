"""Test de integracion del endpoint de Ingresos.

Simula una peticion HTTP POST real hacia /api/v1/simulador/ingresos usando
TestClient de FastAPI, enviando el mock de datos de entrada. Verifica el
codigo de estado 200 y que el totalizador 7.12 viaje correctamente.
"""
import json
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

MOCK_PATH = Path(__file__).resolve().parents[1] / "app" / "db" / "mocks" / "mock_ingresos.json"


def _cargar_mock() -> dict:
    with open(MOCK_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def test_endpoint_ingresos_ok():
    payload = _cargar_mock()

    with TestClient(app) as client:
        response = client.post("/api/v1/simulador/ingresos", json=payload)

    assert response.status_code == 200

    body = response.json()
    # El schema serializa Decimal como string dentro del JSON
    assert body["totales"]["fila_7_12"] == "4180000"
    assert Decimal(body["totales"]["fila_7_12"]) == Decimal("4180000")
    assert body["totales"]["fila_7_total"] == "5020000"

    # Nuevo campo de salida: Col. H por fila (montos adeudados AT anterior)
    filas = {f["codigo"]: f for f in body["filas"]}
    assert filas["7.1"]["ingresos_adeudados_at_anterior"] == "50000"
    assert filas["7.2"]["ingresos_adeudados_at_anterior"] == "20000"
    assert filas["7.9"]["ingresos_adeudados_at_anterior"] == "25000"
    # Fila sin monto de AT anterior -> null
    assert filas["7.11"]["ingresos_adeudados_at_anterior"] is None

    # Flags de visibilidad de columnas para el Frontend
    #  - Vx010042=1 (empresario individual) => columna patrimonio visible
    #  - CRRP=false (sin atributo renta presunta) => columna renta presunta oculta
    avisos = body["avisos"]
    assert avisos["mostrar_columna_patrimonio"] is True
    assert avisos["mostrar_columna_renta_presunta"] is False


def test_endpoint_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"