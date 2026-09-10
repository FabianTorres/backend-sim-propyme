"""Pruebas unitarias del modulo 'Egresos' (Pagina 2 del 14D1).

Verifica los calculos del servicio usando construccion directa de datos con
valores conocidos (golden master).
"""

from decimal import Decimal

from app.schemas.egresos import CamposDigitadosEgresos
from app.schemas.globales import Externos, Vectores
from app.services.egresos import EgresosService


def _fila(response, codigo):
    return next(f for f in response.filas if f.codigo == codigo)


def _datos():
    vectores = Vectores(
        Vx010042=1,
        Vx014022=0,
        Vx014021=Decimal("50000"),
        Vx014237=Decimal("-100000"),
        Vx014350=Decimal("10000"),
        Vx014351=Decimal("2000"),
        Vx014352=Decimal("3000"),
        Vx014353=Decimal("4000"),
        Vx014354=Decimal("5000"),
        Vx012214=Decimal("100000"),
        Vx013350=Decimal("0"),
        Vx012222=Decimal("1000"),
    )
    externos = Externos(
        Calc4064=Decimal("0"), Calc4075=0, CRRP=False, Calc4066=Decimal("0")
    )
    digitados = CamposDigitadosEgresos()
    parametros = {"P77": Decimal("0.19"), "P179": Decimal("1")}
    return vectores, externos, digitados, parametros


def test_fila_8_4_max():
    v, e, d, p = _datos()
    response = EgresosService().calcular(v, e, d, parametros=p)
    fila = _fila(response, "8.4")
    assert fila.egresos_ano == Decimal("100000")
    assert fila.monto_egresos_pagados == Decimal("100000")


def test_fila_8_12_perdidas():
    v, e, d, p = _datos()
    response = EgresosService().calcular(v, e, d, parametros=p)
    fila = _fila(response, "8.12")
    # ABS(-100000) = 100000
    assert fila.egresos_ano == Decimal("100000")
    assert fila.monto_egresos_pagados == Decimal("100000")


def test_fila_8_17_arriendos():
    v, e, d, p = _datos()
    response = EgresosService().calcular(v, e, d, parametros=p)
    assert _fila(response, "8.17").egresos_ano == Decimal("50000")


def test_fila_8_31_suma_h():
    v, e, d, p = _datos()
    response = EgresosService().calcular(v, e, d, parametros=p)
    # 10000 + 2000 + 3000 + 4000 + 5000 = 24000
    assert _fila(response, "8.31").egresos_ano == Decimal("24000")


def test_total_8():
    v, e, d, p = _datos()
    response = EgresosService().calcular(v, e, d, parametros=p)
    # 8.4(100000) + 8.12(100000) + 8.14(1000) + 8.17(50000) + 8.31(24000)
    assert response.totales.fila_8_total == Decimal("275000")


def test_aviso_arriendos_pagados():
    v, e, d, p = _datos()
    response = EgresosService().calcular(v, e, d, parametros=p)
    # Vx014022=0 -> no hay aviso
    assert response.avisos.aviso_arriendos_pagados is False
    assert response.avisos.mostrar_columna_patrimonio is True


def test_reajuste_vx014022():
    v, e, d, p = _datos()
    v.Vx014022 = 1
    response = EgresosService().calcular(v, e, d, parametros=p)
    fila = _fila(response, "8.4")
    # MAX(100000, 0) * (0.19 + 1) = 119000
    assert fila.egresos_ano == Decimal("119000")
    assert response.avisos.aviso_arriendos_pagados is True
