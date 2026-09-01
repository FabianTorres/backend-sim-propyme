"""Fixtures compartidos para todos los tests del Simulador Propyme.

Centraliza la carga de mocks y la construccion de objetos de dominio para
evitar duplicacion de helpers privados (_cargar_datos, _cargar_mock) entre
archivos de test.
"""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.schemas.ingresos import CamposDigitados, ExternosIngresos, VectoresIngresos
from app.schemas.orquestador import SimuladorGlobalRequest

MOCK_PATH = Path(__file__).resolve().parent.parent / "app" / "db" / "mocks" / "mock_simulador_global.json"


@pytest.fixture(scope="session")
def mock_payload() -> dict:
    """Carga el mock JSON como diccionario puro (sin validar)."""
    with open(MOCK_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def mock_global_request(mock_payload: dict) -> SimuladorGlobalRequest:
    """Carga y valida el mock contra SimuladorGlobalRequest."""
    return SimuladorGlobalRequest.model_validate(mock_payload)


@pytest.fixture
def datos_ingresos(
    mock_global_request: SimuladorGlobalRequest,
) -> tuple[VectoresIngresos, ExternosIngresos, CamposDigitados]:
    """Extrae los datos especificos del modulo Ingresos desde el request global.

    Retorna (vectores, externos, digitados) listos para pasar a IngresosService.
    Se usa function scope (por defecto) para que las mutaciones de un test no
    contaminen a otros tests.
    """
    # Se crea una copia fresca de CamposDigitados para cada test
    digitados_original = mock_global_request.digitados.ingresos or CamposDigitados()
    digitados_copia = CamposDigitados(
        monto_no_percibido=dict(digitados_original.monto_no_percibido),
        no_considerar_patrimonio=dict(digitados_original.no_considerar_patrimonio),
        factura_renta_presunta=dict(digitados_original.factura_renta_presunta),
        ingresos_ano=dict(digitados_original.ingresos_ano),
        ingresos_adeudados_at_anterior=dict(digitados_original.ingresos_adeudados_at_anterior),
    )
    return (
        mock_global_request.vectores,
        mock_global_request.externos,
        digitados_copia,
    )