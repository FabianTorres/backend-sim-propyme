"""Pruebas unitarias del modulo 'Retiros' (Pagina 3 del 14D1)."""

from decimal import Decimal

from app.schemas.globales import Vectores
from app.schemas.retiros import CamposDigitadosRetiros, FilaRetiroDigitada
from app.schemas.rre import CamposDigitadosRRE
from app.services.retiros import RetirosService


def _datos():
    vectores = Vectores(
        Vx014301=Decimal("1000000"),
        Vx013509=Decimal("50000"),
        Vx013567=Decimal("2000"),
        Vx013591=Decimal("3000"),
        Vx014661=Decimal("10000"),
        Vx014662=Decimal("2000"),
        Vx014663=Decimal("1000"),
        Vx013510=Decimal("400"),
        Vx013568=Decimal("600"),
        Vx012951=Decimal("800"),
        Vx010599=213,
    )
    rre = CamposDigitadosRRE(
        h2=Decimal("10"),
        h3=Decimal("20"),
        h6=Decimal("30"),
        h7=Decimal("40"),
        i4=Decimal("50"),
        i17=Decimal("60"),
    )
    digitados = CamposDigitadosRetiros(
        filas=[
            FilaRetiroDigitada(
                rut="1-9",
                usufructuario=1,
                f1_fecha="02/01/2025",
                f1_monto=Decimal("100"),
                f1_isfut_h=Decimal("10"),
                f1_isfut_a=Decimal("5"),
                saldo=Decimal("20"),
            ),
            FilaRetiroDigitada(
                rut="1-9",
                f1_fecha="02/02/2025",
                f1_monto=Decimal("50"),
                f1_isfut_h=Decimal("8"),
            ),
        ]
    )
    return vectores, digitados, rre


def test_calculo_1044():
    v, d, rre = _datos()
    resp = RetirosService().calcular(v, d, rre)
    # 1000000 + 50000 + 2000 + 3000 + 10 + 20 + 30 + 40 = 1055100
    assert resp.calculo.v1044 == Decimal("1055100")


def test_calculo_1045():
    v, d, rre = _datos()
    resp = RetirosService().calcular(v, d, rre)
    # POS(10000 - 2000 - 1000) = 7000 ; +400 +600 +800 +60 +50 = 8910
    assert resp.calculo.v1045 == Decimal("8910")


def test_totales():
    v, d, rre = _datos()
    resp = RetirosService().calcular(v, d, rre)
    assert resp.totales.ret30 == Decimal("150")  # 100 + 50
    assert resp.totales.ret15 == Decimal("18")   # 10 + 8
    assert resp.totales.ret14["1-9"] == Decimal("18")


def test_derivadas_por_fecha():
    v, d, rre = _datos()
    resp = RetirosService().calcular(v, d, rre)
    por_codigo = {}
    for var in resp.derivadas:
        por_codigo.setdefault(var.codigo, []).append(var)
    assert len(por_codigo["1040"]) == 2
    assert por_codigo["1040"][0].valor == Decimal("100")
    assert por_codigo["1041"][1].valor == Decimal("8")
    assert por_codigo["1043"][0].valor == Decimal("20")


def test_habilitaciones_y_validaciones():
    v, d, rre = _datos()
    resp = RetirosService().calcular(v, d, rre)
    assert resp.avisos.ret3_habilitado is True   # Vx010599 = 213
    assert resp.avisos.ret6_habilitado is True   # [1044] > 0
    assert resp.avisos.ret7_habilitado is True   # [1045] > 0
    assert resp.avisos.validacion_1044_ok is True
    assert resp.avisos.validacion_1045_ok is True


def test_validacion_1044_falla():
    v, d, rre = _datos()
    v.Vx014301 = Decimal("0")
    v.Vx013509 = Decimal("0")
    v.Vx013567 = Decimal("0")
    v.Vx013591 = Decimal("0")
    rre.h2 = rre.h3 = rre.h6 = rre.h7 = Decimal("0")
    d.filas[0].f1_isfut_h = Decimal("100000")
    resp = RetirosService().calcular(v, d, rre)
    assert resp.avisos.validacion_1044_ok is False


def test_inspectores_auditoria():
    v, d, rre = _datos()
    resp = RetirosService().calcular(v, d, rre, mostrar_formulas=True)
    insp = resp.inspectores
    assert insp is not None
    for clave in [
        "1044",
        "1045",
        "ret30",
        "ret15",
        "validacion_1044",
        "validacion_1045",
        "ret14.1-9",
    ]:
        assert clave in insp
    # El literal de [1044] usa arbol de expresiones (nombres de variables).
    assert "Vx014301" in insp["1044"].literal
    assert insp["ret30"].valor == Decimal("150")
    # Auditoria de la validacion por fila: RET6 + RET7 = 10 + 5 = 15
    assert insp["fila1_validacion_f1"].valor == Decimal("15")


def test_sin_mostrar_formulas_no_hay_inspectores():
    v, d, rre = _datos()
    resp = RetirosService().calcular(v, d, rre, mostrar_formulas=False)
    assert resp.inspectores is None


def test_validacion_por_fila():
    v, d, rre = _datos()
    resp = RetirosService().calcular(v, d, rre)
    assert resp.filas[0].validacion_f1 is True   # 100 >= 10 + 5
    assert resp.filas[0].validacion_f2 is True
    d.filas[0].f1_monto = Decimal("1")
    resp = RetirosService().calcular(v, d, rre)
    assert resp.filas[0].validacion_f1 is False  # 1 < 10 + 5


def test_endpoint_retiros(mock_payload):
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as client:
        response = client.post("/api/v1/simulador/calcular", json=mock_payload)

    assert response.status_code == 200
    body = response.json()
    # El nodo retiros viene poblado (vacio si no hay filas digitadas).
    assert body["retiros"] is not None
    assert "calculo" in body["retiros"]
    assert "filas" in body["retiros"]
