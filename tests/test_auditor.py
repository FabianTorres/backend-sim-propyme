"""Pruebas del Modo Auditoria - inspectores por columna.

Verifica que mostrar_formulas=True incluya inspectores para B, H y F.
"""
from decimal import Decimal

from app.services.ingresos import IngresosService


def _fila(response, codigo):
    return next(f for f in response.filas if f.codigo == codigo)


def test_inspectores_fila_7_1(datos_ingresos):
    """7.1: MAX(Vx012188,...). Debe tener inspectores B, H y F."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=True)
    fila = _fila(response, "7.1")

    assert fila.inspectores is not None
    assert "ingresos_ano" in fila.inspectores
    assert "ingresos_adeudados_at_anterior" in fila.inspectores
    assert "monto_ingreso_percibido" in fila.inspectores

    insp = fila.inspectores["ingresos_ano"]
    assert insp.valor == Decimal("1000000")
    assert "MAX" in insp.literal
    assert "Vx012188" in insp.literal
    nombres = {v.nombre for v in insp.variables_usadas}
    assert "Vx012188" in nombres
    for vi in insp.variables_usadas:
        assert vi.origen == "vector"
    assert len(insp.pasos) > 0
    assert "MAX" in " ".join(insp.pasos)


def test_inspectores_fila_7_14_con_override(datos_ingresos):
    """7.14: sin override se usa la formula propuesta; con override se usa el digitado."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=True)
    fila = _fila(response, "7.14")

    # Sin override: el literal es la formula propuesta y el paso indica SII
    insp = fila.inspectores["ingresos_ano"]
    assert insp.valor == Decimal("90000")
    assert "Vx013639" in insp.literal
    pasos_texto = " ".join(insp.pasos)
    assert "Valor propuesto por el SII" in pasos_texto

    # Con override: prevalece el valor digitado
    d.ingresos_ano["7.14"] = Decimal("55555")
    r2 = IngresosService().calcular(v, e, d, mostrar_formulas=True)
    f2 = _fila(r2, "7.14")
    insp2 = f2.inspectores["ingresos_ano"]
    assert insp2.valor == Decimal("55555")
    assert insp2.literal == "Ingresos 7.14B"
    pasos_texto2 = " ".join(insp2.pasos)
    assert "Se utiliza el valor modificado por el contribuyente" in pasos_texto2
    nombres = {vi.nombre for vi in insp2.variables_usadas}
    assert "Ingresos 7.14B" in nombres
    for vi in insp2.variables_usadas:
        if vi.nombre == "Ingresos 7.14B":
            assert vi.origen == "digitado"


def test_inspectores_fila_7_15_condicional(datos_ingresos):
    """7.15: condicional Calc4064 > 0 => Calc4064, sino Vx012209."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=True)
    fila = _fila(response, "7.15")

    insp = fila.inspectores["ingresos_ano"]
    assert insp.valor == Decimal("0")
    assert "SI(" in insp.literal


def test_inspectores_sin_formulas_flag(datos_ingresos):
    """mostrar_formulas=False => inspectores es None."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=False)
    fila = _fila(response, "7.1")
    assert fila.inspectores is None
def test_inspectores_columna_h_presente(datos_ingresos):
    """Filas con override H deben tener inspector de Col. H."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=True)

    fila71 = _fila(response, "7.1")
    assert "ingresos_adeudados_at_anterior" in fila71.inspectores
    insp_h = fila71.inspectores["ingresos_adeudados_at_anterior"]
    assert insp_h.valor == Decimal("50000")
    assert insp_h.literal == "Vx014255"
    pasos_texto = " ".join(insp_h.pasos)
    assert "Valor propuesto por el SII" in pasos_texto

    # 7.8 NO tiene H
    fila78 = _fila(response, "7.8")
    assert "ingresos_adeudados_at_anterior" not in fila78.inspectores


def test_inspectores_columna_f_presente(datos_ingresos):
    """Toda fila con calculo F debe tener inspector de Col. F."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=True)

    fila71 = _fila(response, "7.1")
    assert "monto_ingreso_percibido" in fila71.inspectores
    insp_f = fila71.inspectores["monto_ingreso_percibido"]
    assert insp_f.valor == Decimal("1000000")
    assert "POS" in insp_f.literal

    # 7.25 NO tiene calculo F
    fila725 = _fila(response, "7.25")
    assert "monto_ingreso_percibido" not in fila725.inspectores


def test_inspectores_pasos_detallados(datos_ingresos):
    """Los pasos deben narrar la resolucion bottom-up completa."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=True)

    fila71 = _fila(response, "7.1")
    pasos = fila71.inspectores["ingresos_ano"].pasos
    assert len(pasos) >= 2
    assert any("+" in p for p in pasos)
    assert any("MAX" in p for p in pasos)

    fila717 = _fila(response, "7.17")
    pasos717 = fila717.inspectores["ingresos_ano"].pasos
    pos_count = sum(1 for p in pasos717 if p.startswith("POS("))
    assert pos_count >= 3


def test_inspectores_pasos_formato(datos_ingresos):
    """Cada paso debe tener formato 'expresion = resultado'."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=True)
    fila = _fila(response, "7.2")
    pasos = fila.inspectores["ingresos_ano"].pasos

    for paso in pasos:
        if "=" in paso:
            izquierda, derecha = paso.rsplit("=", 1)
            assert izquierda.strip(), f"Paso sin expresion: {paso}"
            assert derecha.strip(), f"Paso sin resultado: {paso}"


def test_inspectores_variables_f(datos_ingresos):
    """Col. F debe exponer sus variables (B + digitados C,D,E)."""
    v, e, d = datos_ingresos
    response = IngresosService().calcular(v, e, d, mostrar_formulas=True)
    fila = _fila(response, "7.2")

    insp_f = fila.inspectores["monto_ingreso_percibido"]
    nombres_f = {vi.nombre for vi in insp_f.variables_usadas}
    assert "Ingresos 7.2B" in nombres_f
    for vi in insp_f.variables_usadas:
        assert vi.origen in ("vector", "externo", "digitado", "calculado")


def test_inspectores_fila_7_12_cde(datos_ingresos):
    """7.12 debe exponer inspectores de C, D y E con la sumatoria POS."""
    v, e, d = datos_ingresos
    # Controlamos explicitamente los digitados de 7.1 a 7.11 para C, D y E
    for fila in ("7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9", "7.11"):
        d.monto_no_percibido[fila] = Decimal("0")
        d.no_considerar_patrimonio[fila] = Decimal("0")
        d.factura_renta_presunta[fila] = Decimal("0")

    d.monto_no_percibido["7.1"] = Decimal("10000")
    d.monto_no_percibido["7.3"] = Decimal("20000")
    d.no_considerar_patrimonio["7.2"] = Decimal("5000")
    d.factura_renta_presunta["7.4"] = Decimal("15000")
    d.factura_renta_presunta["7.8"] = Decimal("5000")

    response = IngresosService().calcular(v, e, d, mostrar_formulas=True)
    fila = _fila(response, "7.12")

    assert fila.inspectores is not None
    assert "monto_no_percibido" in fila.inspectores
    assert "no_considerar_patrimonio" in fila.inspectores
    assert "factura_renta_presunta" in fila.inspectores

    insp_c = fila.inspectores["monto_no_percibido"]
    assert insp_c.valor == Decimal("30000")
    assert "POS" in insp_c.literal
    assert "Ingresos 7.1C" in insp_c.literal
    assert "Ingresos 7.3C" in insp_c.literal
    assert any(vi.origen == "digitado" for vi in insp_c.variables_usadas)

    insp_d = fila.inspectores["no_considerar_patrimonio"]
    assert insp_d.valor == Decimal("5000")
    assert "POS" in insp_d.literal

    insp_e = fila.inspectores["factura_renta_presunta"]
    assert insp_e.valor == Decimal("10000")
    assert "POS" in insp_e.literal

    # Los valores de salida deben coincidir con los inspectores
    assert fila.monto_no_percibido == Decimal("30000")
    assert fila.no_considerar_patrimonio == Decimal("5000")
    assert fila.factura_renta_presunta == Decimal("10000")