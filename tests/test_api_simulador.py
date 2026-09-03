"""Test de integracion del endpoint unico del Simulador (Orquestador Global).

Simula una peticion HTTP POST real hacia /api/v1/simulador/calcular usando
TestClient de FastAPI y el fixture compartido mock_payload desde conftest.
Verifica el codigo de estado 200 y que los totalizadores de ingresos viajen
correctamente dentro del nodo 'ingresos' de la respuesta.
"""
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app


def test_endpoint_simulador_ok(mock_payload):
    with TestClient(app) as client:
        response = client.post("/api/v1/simulador/calcular", json=mock_payload)

    assert response.status_code == 200

    body = response.json()
    # La respuesta ahora tiene un nodo 'ingresos' con los datos calculados
    ingresos = body["ingresos"]
    totales = ingresos["totales"]

    # El schema serializa Decimal como string dentro del JSON
    assert totales["fila_7_12"] == "4080000"
    assert Decimal(totales["fila_7_12"]) == Decimal("4080000")
    assert totales["fila_7_total"] == "4920000"

    # Nuevo campo de salida: Col. H por fila (montos adeudados AT anterior)
    filas = {f["codigo"]: f for f in ingresos["filas"]}
    assert filas["7.1"]["ingresos_adeudados_at_anterior"] == "50000"
    assert filas["7.2"]["ingresos_adeudados_at_anterior"] == "20000"
    assert filas["7.9"]["ingresos_adeudados_at_anterior"] == "25000"
    # Fila sin monto de AT anterior -> null
    assert filas["7.11"]["ingresos_adeudados_at_anterior"] is None

    # Columnas C, D y E de la fila totalizadora 7.12
    assert filas["7.12"]["monto_no_percibido"] == "100000"
    assert filas["7.12"]["no_considerar_patrimonio"] == "0"
    assert filas["7.12"]["factura_renta_presunta"] == "0"

    # Flags de visibilidad de columnas para el Frontend
    avisos = ingresos["avisos"]
    assert avisos["mostrar_columna_patrimonio"] is True
    assert avisos["mostrar_columna_renta_presunta"] is False


def test_endpoint_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"