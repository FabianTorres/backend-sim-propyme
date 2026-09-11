"""Servicio de calculo del modulo 'Retiros' - Pagina 3 del 14D1.

Pagina casi de solo ingreso: calcula [1044]/[1045] (con variables del RRE), las
derivadas 1040..1052 y los totales RET30/RET14/RET15.
"""

from app.core.motor_formulas import Constante, Nodo, Pos, Var
from app.schemas.globales import Vectores
from app.schemas.retiros import (
    AvisosRetiros,
    CalculoRetiros,
    CamposDigitadosRetiros,
    FilaRetiro,
    RetirosResponse,
    TotalizadoresRetiros,
    VariableDerivada,
)
from app.schemas.rre import CamposDigitadosRRE
from app.services._helpers import _a_inspector, clave_celda
from app.utils.matematicas import CERO, redondear_monto

VX010599_HABILITA_RET3 = {213, 214, 216, 222, 223, 227}


class RetirosService:
    """Motor de reglas del recuadro Retiros (14D1, Pagina 3)."""

    def calcular(
        self,
        vectores: Vectores,
        digitados: CamposDigitadosRetiros,
        rre: CamposDigitadosRRE,
        mostrar_formulas: bool = False,
    ) -> RetirosResponse:
        v = vectores
        d = digitados
        filas_dig = d.filas
        n = len(filas_dig)

        contexto: dict = {}
        for nombre, valor in v.model_dump().items():
            contexto[nombre] = valor
        contexto["RRE.H2"] = rre.h2
        contexto["RRE.H3"] = rre.h3
        contexto["RRE.H6"] = rre.h6
        contexto["RRE.H7"] = rre.h7
        contexto["RRE.I4"] = rre.i4
        contexto["RRE.I17"] = rre.i17

        def var(i: int, col: str) -> Nodo:
            """Variable de una celda de fila: 'Retiros <fila><col>'."""
            return Var(clave_celda("Retiros", str(i), col), origen="digitado")

        # Las filas quedan en el contexto con nombre canonico "Retiros <fila><col>".
        for i, f in enumerate(filas_dig, start=1):
            contexto[clave_celda("Retiros", str(i), "E")] = f.f1_monto
            contexto[clave_celda("Retiros", str(i), "F")] = f.f1_isfut_h
            contexto[clave_celda("Retiros", str(i), "G")] = f.f1_isfut_a
            contexto[clave_celda("Retiros", str(i), "H")] = f.saldo
            contexto[clave_celda("Retiros", str(i), "J")] = f.f2_monto
            contexto[clave_celda("Retiros", str(i), "K")] = f.f2_isfut_h
            contexto[clave_celda("Retiros", str(i), "L")] = f.f2_isfut_a

        idxs = list(range(1, n + 1))
        ruts = list(dict.fromkeys(f.rut for f in filas_dig))
        idx_por_rut = {rut: [i for i in idxs if filas_dig[i - 1].rut == rut] for rut in ruts}

        # Todos los calculos se construyen con el motor de formulas (arboles).
        arboles = {
            "1044": self._arbol_1044(),
            "1045": self._arbol_1045(),
            "ret30": self._suma([var(i, "E") for i in idxs]),
            "ret15": self._suma([var(i, "F") for i in idxs]),
            "validacion_1044": self._suma([var(i, "F") + var(i, "K") for i in idxs]),
            "validacion_1045": self._suma([var(i, "G") + var(i, "L") for i in idxs]),
        }
        arboles_ret14 = {
            rut: self._suma([var(i, "F") for i in idx]) for rut, idx in idx_por_rut.items()
        }
        arboles_1043 = {
            rut: self._suma([var(i, "H") for i in idx]) for rut, idx in idx_por_rut.items()
        }

        res = {clave: arbol.resolver(contexto) for clave, arbol in arboles.items()}
        res_ret14 = {rut: arbol.resolver(contexto) for rut, arbol in arboles_ret14.items()}
        res_1043 = {rut: arbol.resolver(contexto) for rut, arbol in arboles_1043.items()}

        v1044 = redondear_monto(res["1044"].valor)
        v1045 = redondear_monto(res["1045"].valor)
        # Filas (echo) + validacion por fila (RET5>=RET6+RET7 ; RET10>=RET11+RET12).
        filas: list[FilaRetiro] = []
        tops: dict[int, tuple] = {}
        for i, f in enumerate(filas_dig, start=1):
            res_f1 = (var(i, "F") + var(i, "G")).resolver(contexto)
            res_f2 = (var(i, "K") + var(i, "L")).resolver(contexto)
            tops[i] = (res_f1, res_f2)
            filas.append(
                FilaRetiro(
                    fila=i,
                    rut=f.rut,
                    usufructuario=f.usufructuario,
                    acciones=f.acciones,
                    f1_fecha=f.f1_fecha,
                    f1_monto=f.f1_monto,
                    f1_isfut_h=f.f1_isfut_h,
                    f1_isfut_a=f.f1_isfut_a,
                    saldo=f.saldo,
                    f2_fecha=f.f2_fecha,
                    f2_monto=f.f2_monto,
                    f2_isfut_h=f.f2_isfut_h,
                    f2_isfut_a=f.f2_isfut_a,
                    es_registro_nuevo=f.es_registro_nuevo,
                    validacion_f1=f.f1_monto >= res_f1.valor,
                    validacion_f2=f.f2_monto >= res_f2.valor,
                )
            )

        derivadas: list[VariableDerivada] = []
        for f in filas_dig:
            fecha1 = f.f1_fecha or None
            fecha2 = f.f2_fecha or None
            derivadas.append(VariableDerivada(codigo="1040", rut=f.rut, fecha=fecha1, valor=f.f1_monto))
            derivadas.append(VariableDerivada(codigo="1041", rut=f.rut, fecha=fecha1, valor=f.f1_isfut_h))
            derivadas.append(VariableDerivada(codigo="1042", rut=f.rut, fecha=fecha1, valor=f.f1_isfut_a))
            derivadas.append(VariableDerivada(codigo="1049", rut=f.rut, fecha=fecha2, valor=f.f2_monto))
            derivadas.append(VariableDerivada(codigo="1051", rut=f.rut, fecha=fecha2, valor=f.f2_isfut_h))
            derivadas.append(VariableDerivada(codigo="1052", rut=f.rut, fecha=fecha2, valor=f.f2_isfut_a))
        for rut in ruts:
            derivadas.append(VariableDerivada(codigo="1043", rut=rut, fecha=None, valor=res_1043[rut].valor))

        avisos = AvisosRetiros(
            ret3_habilitado=v.Vx010599 in VX010599_HABILITA_RET3,
            ret6_habilitado=v1044 > CERO,
            ret7_habilitado=v1045 > CERO,
            ret11_habilitado=v1044 > CERO,
            ret12_habilitado=v1045 > CERO,
            validacion_1044_ok=v1044 >= res["validacion_1044"].valor,
            validacion_1045_ok=v1045 >= res["validacion_1045"].valor,
        )

        inspectores = None
        if mostrar_formulas:
            inspectores = {
                "1044": _a_inspector(res["1044"]),
                "1045": _a_inspector(res["1045"]),
                "ret30": _a_inspector(res["ret30"]),
                "ret15": _a_inspector(res["ret15"]),
                "validacion_1044": _a_inspector(res["validacion_1044"]),
                "validacion_1045": _a_inspector(res["validacion_1045"]),
            }
            for rut, r_14 in res_ret14.items():
                inspectores[f"ret14.{rut}"] = _a_inspector(r_14)
            for i, (res_f1, res_f2) in tops.items():
                inspectores[f"fila{i}_validacion_f1"] = _a_inspector(res_f1)
                inspectores[f"fila{i}_validacion_f2"] = _a_inspector(res_f2)

        return RetirosResponse(
            filas=filas,
            calculo=CalculoRetiros(v1044=v1044, v1045=v1045),
            derivadas=derivadas,
            totales=TotalizadoresRetiros(
                ret30=res["ret30"].valor,
                ret15=res["ret15"].valor,
                ret14={rut: r_14.valor for rut, r_14 in res_ret14.items()},
            ),
            avisos=avisos,
            inspectores=inspectores,
        )

    @staticmethod
    def _suma(nodos: list[Nodo]) -> Nodo:
        """Suma n sub-arboles con el motor de formulas (sin operadores nativos)."""
        if not nodos:
            return Constante(CERO)
        total = nodos[0]
        for nodo in nodos[1:]:
            total = total + nodo
        return total

    def _arbol_1044(self) -> Nodo:
        """POS(Vx014301 + Vx013509 + Vx013567 + Vx013591 + H2 + H3 + H6 + H7)."""
        return Pos(
            Var("Vx014301", "vector")
            + Var("Vx013509", "vector")
            + Var("Vx013567", "vector")
            + Var("Vx013591", "vector")
            + Var("RRE.H2", "digitado")
            + Var("RRE.H3", "digitado")
            + Var("RRE.H6", "digitado")
            + Var("RRE.H7", "digitado")
        )

    def _arbol_1045(self) -> Nodo:
        """POS(Vx014661 - Vx014662 - Vx014663) + Vx013510 + Vx013568 + Vx012951 + I17 + I4."""
        return (
            Pos(
                Var("Vx014661", "vector")
                - Var("Vx014662", "vector")
                - Var("Vx014663", "vector")
            )
            + Var("Vx013510", "vector")
            + Var("Vx013568", "vector")
            + Var("Vx012951", "vector")
            + Var("RRE.I17", "digitado")
            + Var("RRE.I4", "digitado")
        )
