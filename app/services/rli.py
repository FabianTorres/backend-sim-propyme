"""Servicio de calculo del modulo 'Determinacion RLI' - Pagina 4 del 14D1.

Calcula 9/9.1/9.2/9.21/9.3, el maximo 9.4, la deduccion 9.4 (override recortado
a [0, maximo]), 9.5, 9.6, la condicion del incentivo al ahorro y la seleccion
de cuadro (t1/t2/t3/pendiente) con el flag del modal 14E.
"""

from decimal import Decimal

from app.core.motor_formulas import (
    Abs,
    Constante,
    MaxD,
    MinD,
    Negativo,
    Nodo,
    Pos,
    Si,
    Var,
)
from app.schemas.egresos import EgresosResponse
from app.schemas.globales import Vectores
from app.schemas.ingresos import IngresosResponse
from app.schemas.rli import AvisosRLI, CamposDigitadosRLI, RLIResponse
from app.services._helpers import (
    _a_inspector,
    _con_override,
    _con_valor_redondeado,
    clave_celda,
)
from app.utils.matematicas import CERO, redondear_monto

# Vectores de la condicion del incentivo al ahorro (sumando de la izquierda).
_VECTORES_CONDICION = [
    "Vx010357", "Vx010145", "Vx010059", "Vx010146", "Vx010358", "Vx010088",
    "Vx011930", "Vx011931", "Vx012832", "Vx012833",
    "Vx012946", "Vx012947", "Vx012948", "Vx012949",
    "Vx012836", "Vx012837",
    "Vx013663", "Vx013664", "Vx013665", "Vx013666",
    "Vx013719", "Vx013720", "Vx013721", "Vx013722",
    "Vx010118", "Vx010089", "Vx012830", "Vx012831",
]

# Filas de Ingresos (col. F) que componen cada codigo de la condicion.
_FILAS_CODIGOS = {
    "C1400": ["7.12"],
    "C1401": ["7.19"],
    "C1587": ["7.13", "7.16"],
    "C1588": ["7.15", "7.20"],
    "C1817": ["7.10"],
}


class RLIService:
    """Motor de reglas de la Determinacion RLI (14D1, Pagina 4)."""

    def calcular(
        self,
        vectores: Vectores,
        ingresos: IngresosResponse,
        egresos: EgresosResponse,
        ret30,
        digitados: CamposDigitadosRLI,
        parametros: dict | None = None,
        mostrar_formulas: bool = False,
    ) -> RLIResponse:
        v = vectores
        params = parametros or {}
        contexto: dict = {}
        for nombre, valor in v.model_dump().items():
            contexto[nombre] = valor
        for clave in ("P02", "P22", "P103"):
            contexto[clave] = params.get(clave, CERO)
        contexto["RLI.deduccion_digitada"] = digitados.deduccion_14e
        contexto["RLI.total_ingresos"] = ingresos.totales.fila_7_total
        contexto["RLI.total_egresos"] = egresos.totales.fila_8_total
        f_egr = {f.codigo: (f.monto_egresos_pagados or CERO) for f in egresos.filas}
        contexto["RLI.ajuste_826"] = f_egr.get("8.26", CERO)
        contexto["RLI.ret30"] = ret30
        f_ing = {f.codigo: (f.monto_ingreso_percibido or CERO) for f in ingresos.filas}
        for filas in _FILAS_CODIGOS.values():
            for codigo in filas:
                contexto[clave_celda("Ingresos", codigo, "F")] = f_ing.get(codigo, CERO)

        res = {}

        # Fase 1: base, 9, 9.1, 9.2, 9.21, 9.3, C-codigos y condicion.
        arbol_base = (
            Var("RLI.total_ingresos", "calculado")
            - Var("RLI.total_egresos", "calculado")
            + Var("RLI.ajuste_826", "calculado")
        )
        res["base"] = _con_valor_redondeado(arbol_base.resolver(contexto))
        contexto["RLI.base"] = res["base"].valor

        res["9"] = _con_valor_redondeado(
            Var("RLI.ajuste_826", "calculado").resolver(contexto)
        )
        res["9.1"] = _con_valor_redondeado(
            Si(
                lambda ctx: ctx["RLI.base"] > CERO,
                Var("RLI.base", "calculado"),
                Constante(CERO),
                "RLI.base > 0",
            ).resolver(contexto)
        )
        contexto["RLI.9.1"] = res["9.1"].valor
        res["9.2"] = _con_valor_redondeado(
            Si(
                lambda ctx: ctx["RLI.base"] < CERO,
                Abs(Var("RLI.base", "calculado")),
                Constante(CERO),
                "RLI.base < 0",
            ).resolver(contexto)
        )
        contexto["RLI.9.2"] = res["9.2"].valor
        res["9.21"] = _con_valor_redondeado(
            Var("RLI.ret30", "calculado").resolver(contexto)
        )
        res["9.3"] = _con_valor_redondeado(
            (
                Var("RLI.9.1", "calculado")
                - Var("RLI.ret30", "calculado")
                - Var("RLI.ajuste_826", "calculado")
            ).resolver(contexto)
        )
        contexto["RLI.9.3"] = res["9.3"].valor

        # C-codigos (insumo interno de la condicion, con auditoria).
        for codigo, filas in _FILAS_CODIGOS.items():
            arbol: Nodo = _suma([Var(clave_celda("Ingresos", f, "F"), "calculado") for f in filas])
            res[codigo] = _con_valor_redondeado(arbol.resolver(contexto))
            contexto[f"RLI.{codigo}"] = res[codigo].valor

        # Condicion 14E: POS(suma Vx) <= MAX(Vx010213; C-suma) * P22.
        suma_vx: Nodo = _suma([Var(nombre, "vector") for nombre in _VECTORES_CONDICION[:6]])
        suma_vx = suma_vx - Var("Vx010146", "vector") - Var("Vx010358", "vector")
        suma_vx = suma_vx - Var("Vx010088", "vector")
        suma_vx = suma_vx + Var("Vx011930", "vector") - Var("Vx011931", "vector")
        suma_vx = suma_vx + Var("Vx012832", "vector") - Var("Vx012833", "vector")
        suma_vx = (
            suma_vx
            + Var("Vx012946", "vector") + Var("Vx012947", "vector")
            + Var("Vx012948", "vector") + Var("Vx012949", "vector")
            + Var("Vx012836", "vector") - Var("Vx012837", "vector")
        )
        suma_vx = (
            suma_vx
            + Var("Vx013663", "vector") + Var("Vx013664", "vector")
            + Var("Vx013665", "vector") + Var("Vx013666", "vector")
            + Var("Vx013719", "vector") + Var("Vx013720", "vector")
            + Var("Vx013721", "vector") + Var("Vx013722", "vector")
            + Var("Vx010118", "vector") - Var("Vx010089", "vector")
            + Var("Vx012830", "vector") - Var("Vx012831", "vector")
        )
        res["cond_izq"] = _con_valor_redondeado(Pos(suma_vx).resolver(contexto))
        contexto["RLI.cond_izq"] = res["cond_izq"].valor
        suma_c: Nodo = _suma([Var(f"RLI.{c}", "calculado") for c in _FILAS_CODIGOS])
        arbol_der = MaxD(Var("Vx010213", "vector"), suma_c) * Var("P22", "parametro")
        res["cond_der"] = _con_valor_redondeado(arbol_der.resolver(contexto))
        contexto["RLI.cond_der"] = res["cond_der"].valor
        res["condicion"] = Si(
            lambda ctx: ctx["RLI.cond_izq"] <= ctx["RLI.cond_der"],
            Constante(Decimal("1")),
            Constante(CERO),
            "POS(suma Vx) <= MAX(Vx010213; C1400+C1401+C1587+C1588+C1817) * P22",
        ).resolver(contexto)
        condicion_ok = res["condicion"].valor == 1

        # Fase 2: max94 y 9.4 (override recortado a [0, maximo]).
        res["max94"] = _con_valor_redondeado(
            MinD(
                Var("P02", "parametro") * Pos(Var("RLI.9.3", "calculado")),
                Var("P103", "parametro"),
            ).resolver(contexto)
        )
        contexto["RLI.max94"] = res["max94"].valor

        elegible = res["9.1"].valor > CERO and res["9.2"].valor == CERO and condicion_ok
        acoge = digitados.acoge_14e
        if elegible and acoge is True:
            arbol_94: Nodo = MinD(
                MaxD(
                    _con_override(
                        Var("RLI.deduccion_digitada", "digitado"),
                        Var("RLI.max94", "calculado"),
                    ),
                    Constante(CERO),
                ),
                Var("RLI.max94", "calculado"),
            )
            res["9.4"] = _con_valor_redondeado(arbol_94.resolver(contexto))
        elif elegible and acoge is None:
            # Modal aun sin responder: provisorio = maximo.
            res["9.4"] = _con_valor_redondeado(
                Var("RLI.max94", "calculado").resolver(contexto)
            )
        else:
            res["9.4"] = _con_valor_redondeado(Constante(CERO).resolver(contexto))
        contexto["RLI.9.4"] = res["9.4"].valor

        # Fase 3: 9.5, 9.6 y subtotal.
        res["9.5"] = _con_valor_redondeado(
            MinD(
                Var("Vx013013", "vector"),
                Var("RLI.9.1", "calculado")
                - Var("RLI.9.4", "calculado"),
            ).resolver(contexto)
        )
        contexto["RLI.9.5"] = res["9.5"].valor
        arbol_96: Nodo = (
            Var("RLI.9.1", "calculado")
            - Var("RLI.9.4", "calculado")
            - Var("RLI.9.5", "calculado")
        )
        res["9.6"] = _con_valor_redondeado(
            Si(
                lambda ctx: ctx["RLI.9.1"] - ctx["RLI.9.4"] - ctx["RLI.9.5"] > CERO,
                arbol_96,
                Negativo(Var("RLI.9.2", "calculado")),
                "9.1 - 9.4 - 9.5 > 0",
            ).resolver(contexto)
        )
        res["subtotal"] = _con_valor_redondeado(
            Pos(
                Var("RLI.9.1", "calculado")
                - Var("RLI.ret30", "calculado")
                - Var("RLI.ajuste_826", "calculado")
            ).resolver(contexto)
        )

        # Cuadro y modal.
        if res["9.2"].valor > CERO:
            cuadro = "t2"
            mostrar_modal = False
        elif elegible and acoge is True:
            cuadro = "t1"
            mostrar_modal = False
        elif elegible and acoge is None:
            cuadro = "pendiente"
            mostrar_modal = True
        else:
            cuadro = "t3"
            mostrar_modal = False

        avisos = AvisosRLI(
            mostrar_9_1=res["9.1"].valor > CERO,
            mostrar_9_2=res["9.2"].valor > CERO,
            mostrar_9_5=res["9.5"].valor > CERO,
        )

        inspectores = None
        if mostrar_formulas:
            inspectores = {clave: _a_inspector(res[clave]) for clave in res}

        return RLIResponse(
            v9=res["9"].valor,
            v9_1=res["9.1"].valor,
            v9_2=res["9.2"].valor,
            v9_21=res["9.21"].valor,
            v9_3=res["9.3"].valor,
            max94=res["max94"].valor,
            v9_4=res["9.4"].valor,
            v9_5=res["9.5"].valor,
            v9_6=res["9.6"].valor,
            subtotal=redondear_monto(res["subtotal"].valor),
            condicion_ok=condicion_ok,
            cuadro=cuadro,
            mostrar_modal_14e=mostrar_modal,
            codigos={c: res[c].valor for c in _FILAS_CODIGOS},
            avisos=avisos,
            inspectores=inspectores,
        )


def _suma(nodos: list[Nodo]) -> Nodo:
    """Suma n sub-arboles con el motor de formulas (sin operadores nativos)."""
    if not nodos:
        return Constante(CERO)
    total = nodos[0]
    for nodo in nodos[1:]:
        total = total + nodo
    return total
