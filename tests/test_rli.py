"""Pruebas del modulo 'Determinacion RLI' (Pagina 4 del 14D1).

Cubre 9/9.1/9.2/9.21/9.3, max94, 9.4 (override recortado), 9.5, 9.6,
condicion 14E, seleccion de cuadro y modal.
"""
from decimal import Decimal

from app.schemas.egresos import EgresosResponse, FilaEgreso, TotalizadoresEgresos
from app.schemas.globales import Vectores
from app.schemas.ingresos import FilaIngreso, IngresosResponse, TotalizadoresIngresos
from app.schemas.rli import CamposDigitadosRLI
from app.services.rli import RLIService


def _f_ing(codigo, f):
    return FilaIngreso(codigo=codigo, concepto=codigo, monto_ingreso_percibido=f)


def _f_egr(codigo, f):
    return FilaEgreso(codigo=codigo, concepto=codigo, monto_egresos_pagados=f)


def _datos(acoge=None, deduccion=None, cond_vec=None, totales=None):
    """Caso sintetico: 7=1000, 8=400, 8.26=50, RET30=200, Vx013013=100."""
    v = Vectores(Vx013013=Decimal("100"), **(cond_vec or {}))
    ing = IngresosResponse(
        filas=[
            _f_ing("7.10", Decimal("100")),
            _f_ing("7.12", Decimal("600")),
            _f_ing("7.13", Decimal("0")),
            _f_ing("7.16", Decimal("0")),
            _f_ing("7.15", Decimal("50")),
            _f_ing("7.20", Decimal("50")),
            _f_ing("7.19", Decimal("200")),
            _f_ing("7.17", Decimal("10")),
            _f_ing("7.18", Decimal("20")),
            _f_ing("7.25", None),
            _f_ing("7.26", None),
        ],
        totales=TotalizadoresIngresos(fila_7_total=Decimal("1000")),
    )
    egr = EgresosResponse(
        filas=[_f_egr("8.26", Decimal("50"))],
        totales=TotalizadoresEgresos(fila_8_total=Decimal("400")),
    )
    t = totales or {}
    ing.totales.fila_7_total = t.get("siete", Decimal("1000"))
    egr.totales.fila_8_total = t.get("ocho", Decimal("400"))
    egr.filas[0].monto_egresos_pagados = t.get("ocho26", Decimal("50"))
    ret30 = t.get("ret30", Decimal("200"))
    dig = CamposDigitadosRLI(acoge_14e=acoge, deduccion_14e=deduccion or Decimal("0"))
    params = {"P02": Decimal("0.5"), "P22": Decimal("0.2"), "P103": Decimal("10000")}
    return v, ing, egr, ret30, dig, params


def _calc(**kwargs):
    v, ing, egr, ret30, dig, params = _datos(**kwargs)
    return RLIService().calcular(v, ing, egr, ret30, dig, params)


def test_base_9_1_y_9_2():
    r = _calc()
    assert r.v9 == Decimal("50")
    assert r.v9_1 == Decimal("650")  # 1000 - 400 + 50
    assert r.v9_2 == Decimal("0")
    assert r.v9_21 == Decimal("200")
    assert r.v9_3 == Decimal("400")  # 650 - 200 - 50
    assert r.max94 == Decimal("200")  # min(0.5*400, 10000)


def test_modal_pendiente_sin_respuesta():
    r = _calc(acoge=None)
    assert r.condicion_ok is True
    assert r.mostrar_modal_14e is True
    assert r.cuadro == "pendiente"
    assert r.v9_4 == Decimal("200")  # provisorio = maximo
    assert r.v9_5 == Decimal("100")  # min(100, 650-200)
    assert r.v9_6 == Decimal("350")


def test_acoge_si_sin_digitado():
    r = _calc(acoge=True)
    assert r.cuadro == "t1"
    assert r.mostrar_modal_14e is False
    assert r.v9_4 == Decimal("200")
    assert r.v9_6 == Decimal("350")


def test_acoge_si_con_digitado_dentro_de_cota():
    r = _calc(acoge=True, deduccion=Decimal("150"))
    assert r.v9_4 == Decimal("150")
    assert r.v9_5 == Decimal("100")  # min(100, 650-150)
    assert r.v9_6 == Decimal("400")  # 650-150-100


def test_acoge_si_con_digitado_sobre_maximo_recorta():
    r = _calc(acoge=True, deduccion=Decimal("500"))
    assert r.v9_4 == Decimal("200")
    assert r.v9_6 == Decimal("350")


def test_acoge_no_va_a_tabla3():
    r = _calc(acoge=False)
    assert r.cuadro == "t3"
    assert r.v9_4 == Decimal("0")
    assert r.v9_5 == Decimal("100")  # min(100, 650)
    assert r.v9_6 == Decimal("550")


def test_perdida_tributaria_tabla2():
    r = _calc(totales={"siete": Decimal("100"), "ocho": Decimal("400"),
                       "ocho26": Decimal("50"), "ret30": Decimal("0")})
    assert r.v9_1 == Decimal("0")
    assert r.v9_2 == Decimal("250")  # ABS(100-400+50)
    assert r.cuadro == "t2"
    assert r.mostrar_modal_14e is False
    assert r.v9_6 == Decimal("-250")


def test_base_cero_tabla3():
    r = _calc(totales={"siete": Decimal("350"), "ocho": Decimal("400"),
                       "ocho26": Decimal("50"), "ret30": Decimal("0")})
    assert r.v9_1 == Decimal("0")
    assert r.v9_2 == Decimal("0")
    assert r.cuadro == "t3"


def test_condicion_falla_sin_modal():
    r = _calc(acoge=None, cond_vec={"Vx010357": Decimal("100000")})
    assert r.condicion_ok is False
    assert r.mostrar_modal_14e is False
    assert r.cuadro == "t3"


def test_avisos_display():
    r = _calc(acoge=True)
    assert r.avisos.mostrar_9_1 is True
    assert r.avisos.mostrar_9_2 is False
    assert r.avisos.mostrar_9_5 is True
    r2 = _calc(totales={"siete": Decimal("100"), "ocho": Decimal("400"),
                        "ocho26": Decimal("50"), "ret30": Decimal("0")})
    assert r2.avisos.mostrar_9_1 is False
    assert r2.avisos.mostrar_9_2 is True


def test_inspectores_auditoria():
    v, ing, egr, ret30, dig, params = _datos(acoge=True)
    r = RLIService().calcular(v, ing, egr, ret30, dig, params, mostrar_formulas=True)
    assert r.inspectores is not None
    for clave in ["9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "condicion", "C1400"]:
        assert clave in r.inspectores
    assert "MIN" in r.inspectores["9.4"].literal


def test_sin_mostrar_formulas_no_hay_inspectores():
    assert _calc().inspectores is None


def test_endpoint_rli_presente(mock_payload):
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as client:
        response = client.post("/api/v1/simulador/calcular", json=mock_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["rli"] is not None
    assert "v9_1" in body["rli"]


def test_caso_qa_cuadro_3():
    """Caso RUT 69500400-1 (AT2026): base 23063230, condicion falla -> t3."""
    import json
    from pathlib import Path

    from app.schemas.orquestador import SimuladorGlobalRequest
    from app.services.orquestador import OrquestadorService

    caso = Path(__file__).resolve().parent.parent / "devtools" / "playwright_check" / "casos" / "rut_69500400-1.json"
    req = SimuladorGlobalRequest.model_validate(json.loads(caso.read_text(encoding="utf-8")))
    rli = OrquestadorService().calcular_simulacion(req).rli

    assert rli.v9_1 == Decimal("23063230")
    assert rli.v9_2 == Decimal("0")
    assert rli.v9_3 == Decimal("8233330")
    assert rli.max94 == Decimal("4116665")
    assert rli.condicion_ok is False
    assert rli.mostrar_modal_14e is False
    assert rli.cuadro == "t3"
    assert rli.v9_4 == Decimal("0")
    assert rli.v9_5 == Decimal("1075360")
    assert rli.v9_6 == Decimal("21987870")
