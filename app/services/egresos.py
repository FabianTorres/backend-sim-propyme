"""Servicio de calculo del modulo 'Egresos' - Pagina 2 del 14D1.

Logica pura de calculo con arboles de expresiones para Modo Auditoria.
Espejo del modulo Ingresos (Pagina 1).
"""

from decimal import Decimal

from app.core.motor_formulas import (
    Constante,
    MaxD,
    Nodo,
    Pos,
    Si,
    Var,
)
from app.schemas.comunes import InspectorFormula
from app.schemas.egresos import (
    AvisosEgresos,
    CamposDigitadosEgresos,
    EgresosResponse,
    FilaEgreso,
    TotalizadoresEgresos,
)
from app.schemas.globales import Externos, Vectores
from app.services._helpers import _a_inspector, _con_override
from app.utils.matematicas import CERO


class EgresosService:
    """Motor de reglas de la tabla de Egresos (14D1, Pagina 2)."""

    CONCEPTOS = {
        "8.1": ("Gasto por saldo inicial de existencias o insumos del negocio en cambio de regimen", 1406),
        "8.2": ("Gasto por saldo inicial de activo fijo en cambio de regimen", 1407),
        "8.3": ("Gasto por perdida tributaria en cambio de regimen", 1408),
        "8.4": ("Compras y/o Servicios Internas del Giro o Facturas de Compra Emitidas", 1409),
        "8.5": ("Compras Internas e Importaciones del Activo Fijo", 1413),
        "8.6": ("Importaciones del Giro", 1409),
        "8.7": ("Notas de Credito recibidas", 1409),
        "8.8": ("Notas de Debito recibidas", 1409),
        "8.9": ("Compras y/o Servicios Sin derecho a Credito Fiscal", 1409),
        "8.10": ("Facturas recibidas por adquisicion o construccion de bienes inmuebles", 1413),
        "8.11": ("Facturas recibidas de Proveedores: Supermercados y Comercios similares", 1409),
        "8.12": ("Perdidas tributarias de ejercicios anteriores", 1426),
        "8.13": ("Gastos de rentas de fuente extranjera", 1429),
        "8.14": ("Remuneraciones pagadas", 1411),
        "8.15": ("Honorarios pagados", 1412),
        "8.17": ("Arriendos pagados", 1415),
        "8.18": ("Gastos por responsabilidad social", 1416),
        "8.19": ("Gastos por inversion en investigacion y desarrollo no certificados por CORFO", 1417),
        "8.20": ("Gastos por inversion en investigacion y desarrollo certificados por CORFO", 1418),
        "8.21": ("Impuestos Pagados excepto Impuestos a la Renta", 1424),
        "8.22": ("Intereses y reajustes pagados por prestamos y otros", 1419),
        "8.23": ("Gastos o egresos pagados o adeudados por operaciones con empresas relacionadas", 1425),
        "8.24": ("Otros gastos deducibles de los ingresos", 1424),
        "8.25": ("Ajuste por partidas del inciso 1 y 3 del art. 21 de la LIR pagados", 1421),
        "8.26": ("Ajuste por partidas del art. 21 inc. 1 no afectados con IU 40% y del inc. 2 LIR pagados", 1422),
        "8.27": ("Perdida en rescate o enajenacion de inversiones o bienes no depreciables", 1423),
        "8.28": ("Creditos incobrables castigados en el ejercicio", 1427),
        "8.29": ("Gastos aceptados por donaciones", 1428),
        "8.31": ("Existencias, insumos y servicios del negocio adeudados en el ejercicio anterior y pagados", 1818),
        "8": ("TOTAL EGRESOS", 1430),
    }

    # ------------------------------------------------------------------
    # Metodo principal
    # ------------------------------------------------------------------

    def calcular(
        self,
        vectores: Vectores,
        externos: Externos,
        digitados: CamposDigitadosEgresos,
        parametros: dict[str, Decimal] | None = None,
        mostrar_formulas: bool = False,
    ) -> EgresosResponse:
        """Calcula todos los campos de salida del modulo Egresos."""
        v = vectores
        d = digitados

        # --- Construir contexto plano ---
        contexto: dict = {}
        for field_name, value in v.model_dump().items():
            contexto[field_name] = value
        contexto["Calc4066"] = externos.Calc4066
        for clave, valor in (parametros or {}).items():
            contexto[clave] = valor

        # Digitados como variables: Egresos <fila><col>
        for fila, monto in d.egresos_ano.items():
            contexto[f"Egresos {fila}B"] = monto
        for fila, monto in d.no_pagadas.items():
            contexto[f"Egresos {fila}C"] = monto
        for fila, monto in d.no_considerar_patrimonio.items():
            contexto[f"Egresos {fila}D"] = monto
        for fila, monto in d.factura_renta_presunta.items():
            contexto[f"Egresos {fila}E"] = monto
        for fila, monto in d.egresos_adeudados_at_anterior.items():
            contexto[f"Egresos {fila}H (Modificado)"] = monto

        # --- Col. H: override digitado > vector como arboles ---
        reglas_h = {
            "8.4": "Vx014350",
            "8.5": "Vx014355",
            "8.6": "Vx014351",
            "8.8": "Vx014352",
            "8.9": "Vx014353",
            "8.10": "Vx014356",
            "8.11": "Vx014354",
            "8.14": "Vx014357",
            "8.15": "Vx014358",
            "8.24": "Vx014359",
            "8.27": "Vx014360",
        }
        h_valores: dict[str, Decimal] = {}
        h_inspectores: dict[str, InspectorFormula] = {}
        for fila, vec_key in reglas_h.items():
            arbol_h = _con_override(
                Var(f"Egresos {fila}H (Modificado)", origen="digitado"),
                Var(vec_key, origen="vector"),
            )
            resultado_h = arbol_h.resolver(contexto)
            h_valores[fila] = resultado_h.valor
            contexto[f"Egresos {fila}H"] = resultado_h.valor
            if mostrar_formulas:
                h_inspectores[fila] = _a_inspector(resultado_h)

        # --- Arboles de Col. B ---
        arboles_b = self._construir_arboles_b()

        # --- Resolver Col. B ---
        b_valores: dict[str, Decimal] = {}
        b_inspectores: dict[str, InspectorFormula] = {}
        for codigo, arbol in arboles_b.items():
            resultado = arbol.resolver(contexto)
            b_valores[codigo] = resultado.valor
            contexto[f"Egresos {codigo}B"] = resultado.valor
            if mostrar_formulas:
                b_inspectores[codigo] = _a_inspector(resultado)

        # --- Col. F ---
        f_valores: dict[str, Decimal] = {}
        f_inspectores: dict[str, InspectorFormula] = {}
        for codigo in self._filas_con_f():
            arbol_f = self._arbol_f(codigo, h_valores)
            resultado = arbol_f.resolver(contexto)
            f_valores[codigo] = resultado.valor
            contexto[f"Egresos {codigo}F"] = resultado.valor
            if mostrar_formulas:
                f_inspectores[codigo] = _a_inspector(resultado)

        # --- Armar respuesta ---
        filas = self._armar_filas(
            b_valores,
            f_valores,
            h_valores,
            d,
            b_inspectores if mostrar_formulas else None,
            h_inspectores if mostrar_formulas else None,
            f_inspectores if mostrar_formulas else None,
        )
        avisos = self._calcular_avisos(v, externos)

        return EgresosResponse(
            filas=filas,
            totales=TotalizadoresEgresos(fila_8_total=f_valores.get("8", CERO)),
            avisos=avisos,
        )


    # ------------------------------------------------------------------
    # Construccion de arboles de Col. B
    # ------------------------------------------------------------------

    def _construir_arboles_b(self) -> dict[str, Nodo]:
        """Devuelve {codigo_fila: Nodo} con las formulas de Col. B (Egresos del anio)."""

        def dig_b(fila: str) -> Nodo:
            return Var(f"Egresos {fila}B", origen="digitado")

        def cond_1422(sin_cond: Nodo, con_cond: Nodo) -> Nodo:
            """Aplica el reajuste (P77+P179) solo si Vx014022==1."""
            return Si(
                cond_fn=lambda ctx: ctx.get("Vx014022") == 1,
                verdadero=con_cond,
                falso=sin_cond,
                descripcion="Vx014022==1",
            )

        return {
            "8.1": dig_b("8.1"),
            "8.2": dig_b("8.2"),
            "8.3": dig_b("8.3"),
            "8.4": cond_1422(
                MaxD(Var("Vx012214", "vector"), Var("Vx013350", "vector")),
                MaxD(Var("Vx012214", "vector"), Var("Vx013350", "vector"))
                * (Var("P77", "parametro") + Var("P179", "parametro")),
            ),
            "8.5": cond_1422(
                MaxD(
                    Var("Vx012215", "vector"),
                    Var("Vx013356", "vector") + Var("Vx013364", "vector"),
                ),
                MaxD(
                    Var("Vx012215", "vector"),
                    Var("Vx013356", "vector") + Var("Vx013364", "vector"),
                )
                * (Var("P77", "parametro") + Var("P179", "parametro")),
            ),
            "8.6": cond_1422(
                MaxD(Var("Vx012216", "vector"), Var("Vx013362", "vector")),
                MaxD(Var("Vx012216", "vector"), Var("Vx013362", "vector"))
                * (Var("P77", "parametro") + Var("P179", "parametro")),
            ),
            "8.7": cond_1422(
                MaxD(Var("Vx012217", "vector"), Var("Vx013358", "vector")),
                MaxD(Var("Vx012217", "vector"), Var("Vx013358", "vector"))
                * (Var("P77", "parametro") + Var("P179", "parametro")),
            ),
            "8.8": cond_1422(
                MaxD(Var("Vx012218", "vector"), Var("Vx013360", "vector")),
                MaxD(Var("Vx012218", "vector"), Var("Vx013360", "vector"))
                * (Var("P77", "parametro") + Var("P179", "parametro")),
            ),
            "8.9": _con_override(
                dig_b("8.9"),
                cond_1422(
                    MaxD(
                        Var("Vx012219", "vector"),
                        Var("Vx013344", "vector")
                        + Var("Vx013346", "vector")
                        + Var("Vx013348", "vector"),
                    ),
                    MaxD(
                        Var("Vx012219", "vector"),
                        Var("Vx013344", "vector")
                        + Var("Vx013346", "vector")
                        * (Var("P77", "parametro") + Var("P179", "parametro"))
                        + Var("Vx013348", "vector"),
                    ),
                ),
            ),
            "8.10": cond_1422(
                MaxD(Var("Vx012221", "vector"), Var("Vx013354", "vector")),
                MaxD(Var("Vx012221", "vector"), Var("Vx013354", "vector"))
                * (Var("P77", "parametro") + Var("P179", "parametro")),
            ),
            "8.11": cond_1422(
                MaxD(Var("Vx012220", "vector"), Var("Vx013352", "vector")),
                MaxD(Var("Vx012220", "vector"), Var("Vx013352", "vector"))
                * (Var("P77", "parametro") + Var("P179", "parametro")),
            ),

            "8.12": Si(
                cond_fn=lambda ctx: ctx.get("Vx014237") < CERO,
                verdadero=-Var("Vx014237", "vector"),
                falso=Constante(CERO),
                descripcion="Vx014237<0",
            ),
            "8.13": dig_b("8.13"),
            "8.14": (
                Var("Vx012222", "vector")
                + Var("Vx012252", "vector")
                + Var("Vx012253", "vector")
                + Var("Vx012254", "vector")
                + Var("Vx013646", "vector")
            ),
            "8.15": Var("Vx013647", "vector"),
            "8.17": _con_override(dig_b("8.17"), Var("Vx014021", "vector")),
            "8.18": dig_b("8.18"),
            "8.19": dig_b("8.19"),
            "8.20": dig_b("8.20"),
            "8.21": dig_b("8.21"),
            "8.22": dig_b("8.22"),
            "8.23": dig_b("8.23"),
            "8.24": _con_override(dig_b("8.24"), Var("Calc4066", "externo")),
            "8.25": _con_override(
                dig_b("8.25"),
                (
                    Var("Vx014094", "vector")
                    + Var("Vx014095", "vector")
                    + Var("Vx014096", "vector")
                    + Var("Vx014097", "vector")
                    + Var("Vx014098", "vector")
                    + Var("Vx014099", "vector")
                ),
            ),
            "8.26": _con_override(
                dig_b("8.26"),
                Var("Vx013649", "vector") + Var("Vx013650", "vector"),
            ),
            "8.27": _con_override(
                dig_b("8.27"),
                (
                    Var("Vx010089", "vector")
                    + Var("Vx010241", "vector")
                    + Var("Vx012831", "vector")
                ),
            ),
            "8.28": dig_b("8.28"),
            "8.29": dig_b("8.29"),
            "8.31": (
                Var("Egresos 8.4H", "calculado")
                + Var("Egresos 8.6H", "calculado")
                + Var("Egresos 8.8H", "calculado")
                + Var("Egresos 8.9H", "calculado")
                + Var("Egresos 8.11H", "calculado")
            ),
        }


    # ------------------------------------------------------------------
    # Columna F
    # ------------------------------------------------------------------

    def _filas_con_f(self) -> list[str]:
        """Orden de resolucion de Col. F. '8' (total) va al final."""
        return [
            "8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9",
            "8.10", "8.11", "8.12", "8.13", "8.14", "8.15", "8.17", "8.18",
            "8.19", "8.20", "8.21", "8.22", "8.23", "8.24", "8.25", "8.26",
            "8.27", "8.28", "8.29", "8.31", "8",
        ]

    def _arbol_f(self, codigo: str, h_valores: dict) -> Nodo:
        """Construye el arbol de Col. F: POS(B +/- H - C - D - E)."""
        if codigo == "8":
            return (
                Var("Egresos 8.1F", "calculado")
                + Var("Egresos 8.2F", "calculado")
                + Var("Egresos 8.3F", "calculado")
                + Var("Egresos 8.4F", "calculado")
                + Var("Egresos 8.5F", "calculado")
                + Var("Egresos 8.6F", "calculado")
                - Var("Egresos 8.7F", "calculado")
                + Var("Egresos 8.8F", "calculado")
                + Var("Egresos 8.9F", "calculado")
                + Var("Egresos 8.10F", "calculado")
                + Var("Egresos 8.11F", "calculado")
                + Var("Egresos 8.12F", "calculado")
                + Var("Egresos 8.13F", "calculado")
                + Var("Egresos 8.14F", "calculado")
                + Var("Egresos 8.15F", "calculado")
                + Var("Egresos 8.17F", "calculado")
                + Var("Egresos 8.18F", "calculado")
                + Var("Egresos 8.19F", "calculado")
                + Var("Egresos 8.20F", "calculado")
                + Var("Egresos 8.21F", "calculado")
                + Var("Egresos 8.22F", "calculado")
                + Var("Egresos 8.23F", "calculado")
                + Var("Egresos 8.24F", "calculado")
                + Var("Egresos 8.25F", "calculado")
                + Var("Egresos 8.26F", "calculado")
                + Var("Egresos 8.27F", "calculado")
                + Var("Egresos 8.28F", "calculado")
                + Var("Egresos 8.29F", "calculado")
                + Var("Egresos 8.31F", "calculado")
            )

        con_h = {"8.5", "8.10", "8.14", "8.15", "8.24", "8.27"}
        b = Var(f"Egresos {codigo}B", origen="calculado")
        c = Var(f"Egresos {codigo}C", origen="digitado")
        d_col = Var(f"Egresos {codigo}D", origen="digitado")
        e = Var(f"Egresos {codigo}E", origen="digitado")

        if codigo in con_h:
            h_val = h_valores.get(codigo, CERO)
            return Pos(b + Constante(h_val) - c - d_col - e)
        return Pos(b - c - d_col - e)

    # ------------------------------------------------------------------
    # Avisos
    # ------------------------------------------------------------------

    def _calcular_avisos(self, v: Vectores, externos: Externos) -> AvisosEgresos:
        """Calcula los flags y avisos de la tabla de Egresos."""
        aviso_arriendos_pagados = v.Vx014022 == 1 and v.Vx014021 > CERO
        mostrar_columna_patrimonio = v.Vx010042 == 1
        mostrar_columna_renta_presunta = externos.CRRP
        return AvisosEgresos(
            aviso_arriendos_pagados=aviso_arriendos_pagados,
            mostrar_columna_patrimonio=mostrar_columna_patrimonio,
            mostrar_columna_renta_presunta=mostrar_columna_renta_presunta,
        )

    # ------------------------------------------------------------------
    # Armado de respuesta
    # ------------------------------------------------------------------

    def _armar_filas(
        self,
        b: dict,
        f: dict,
        h: dict,
        d: CamposDigitadosEgresos,
        ins_b: dict[str, InspectorFormula] | None,
        ins_h: dict[str, InspectorFormula] | None,
        ins_f: dict[str, InspectorFormula] | None,
    ) -> list:
        codigos = [
            "8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9",
            "8.10", "8.11", "8.12", "8.13", "8.14", "8.15", "8.17", "8.18",
            "8.19", "8.20", "8.21", "8.22", "8.23", "8.24", "8.25", "8.26",
            "8.27", "8.28", "8.29", "8.31", "8",
        ]
        filas = []
        for codigo in codigos:
            concepto, f22 = self.CONCEPTOS[codigo]

            if codigo == "8":
                c_val = None
                d_val = None
                e_val = None
            else:
                c_val = d.no_pagadas.get(codigo, CERO)
                d_val = d.no_considerar_patrimonio.get(codigo, CERO)
                e_val = d.factura_renta_presunta.get(codigo, CERO)

            inspectores_fila: dict[str, InspectorFormula] | None = None
            if ins_b is not None:
                inspectores_fila = {}
                if codigo in ins_b:
                    inspectores_fila["egresos_ano"] = ins_b[codigo]
                if ins_h and codigo in ins_h:
                    inspectores_fila["egresos_adeudados_at_anterior"] = ins_h[codigo]
                if ins_f and codigo in ins_f:
                    inspectores_fila["monto_egresos_pagados"] = ins_f[codigo]

            filas.append(
                FilaEgreso(
                    codigo=codigo,
                    concepto=concepto,
                    codigo_f22=f22,
                    egresos_ano=b.get(codigo),
                    egresos_adeudados_at_anterior=h.get(codigo),
                    no_pagadas=c_val,
                    no_considerar_patrimonio=d_val,
                    factura_renta_presunta=e_val,
                    monto_egresos_pagados=f.get(codigo),
                    inspectores=inspectores_fila,
                )
            )
        return filas

