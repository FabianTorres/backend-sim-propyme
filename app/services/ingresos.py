"""Servicio de calculo del modulo 'Ingresos' - Pagina 1 del 14D1.

Logica pura de calculo con arboles de expresiones para Modo Auditoria.
"""

from decimal import Decimal

from app.core.motor_formulas import (
    Constante,
    MaxD,
    Nodo,
    Pos,
    ReemplazoManual,
    ResultadoNodo,
    Si,
    Var,
)
from app.schemas.ingresos import (
    AvisosIngresos,
    CamposDigitados,
    ExternosIngresos,
    FilaIngreso,
    IngresosResponse,
    InspectorFormula,
    TotalizadoresIngresos,
    VariableInfo,
    VectoresIngresos,
)
from app.utils.matematicas import CERO


class IngresosService:
    """Motor de reglas de la tabla de Ingresos (14D1, Pagina 1)."""

    CONCEPTOS = {
        "7.1": ("Exportaciones (Cod. 20 F29)", 1400),
        "7.2": ("Facturas por ventas y servicios gravados", 1400),
        "7.3": ("Ventas exentas o no gravadas", 1400),
        "7.4": ("Ventas con retencion sobre margen", 1400),
        "7.5": ("Facturas compra retencion total", 1400),
        "7.6": ("Facturas compra retencion parcial", 1400),
        "7.7": ("Boletas / Transbank", 1400),
        "7.8": ("Notas de credito emitidas", 1400),
        "7.9": ("Notas de debito emitidas", 1400),
        "7.10": ("Ingresos devengados AT anteriores percibidos", 1817),
        "7.11": ("Ingresos por contratos no facturados", 1400),
        "7.12": ("Total Ingresos por ventas y servicios", 1400),
        "7.13": ("Contratos con Empresas Relacionadas", 1587),
        "7.14": ("Mayor valor enajenacion de inversiones", 1403),
        "7.15": ("Arriendos de bienes raices", 1588),
        "7.16": ("Operaciones con empresas relacionadas", 1587),
        "7.17": ("Intereses Directos", 1402),
        "7.18": ("Intereses Indirectos", 1402),
        "7.19": ("Renta de fuente extranjera", 1401),
        "7.20": ("Otros ingresos percibidos o devengados", 1588),
        "7.25": ("Ingreso diferido pendiente art.14 D N8", None),
        "7.26": ("Incremento ingreso diferido", None),
        "7.27": ("Credito sobre Activos Fijos", 1405),
    }

    # ------------------------------------------------------------------
    # Metodo principal
    # ------------------------------------------------------------------

    def calcular(
        self,
        vectores: VectoresIngresos,
        externos: ExternosIngresos,
        digitados: CamposDigitados,
        mostrar_formulas: bool = False,
    ) -> IngresosResponse:
        """Calcula todos los campos de salida del modulo Ingresos."""
        v = vectores
        d = digitados
        calc4064 = externos.Calc4064
        calc4075 = externos.Calc4075

        # --- Construir contexto plano ---
        contexto: dict = {}
        for field_name, value in v.model_dump().items():
            contexto[field_name] = value
        contexto["Calc4064"] = calc4064
        contexto["Calc4075"] = calc4075

        # Digitados como variables: Ingresos <fila><col>
        for fila, monto in d.ingresos_ano.items():
            contexto[f"Ingresos {fila}B"] = monto
        for fila, monto in d.monto_no_percibido.items():
            contexto[f"Ingresos {fila}C"] = monto
        for fila, monto in d.no_considerar_patrimonio.items():
            contexto[f"Ingresos {fila}D"] = monto
        for fila, monto in d.factura_renta_presunta.items():
            contexto[f"Ingresos {fila}E"] = monto
        for fila, monto in d.ingresos_adeudados_at_anterior.items():
            contexto[f"Ingresos {fila}H (Modificado)"] = monto

        # --- Col. H: override digitado > vector como arboles ---
        reglas_h = {
            "7.1": "Vx014255",
            "7.2": "Vx014256",
            "7.3": "Vx014257",
            "7.4": "Vx014258",
            "7.5": "Vx014259",
            "7.6": "Vx014260",
            "7.7": "Vx014261",
            "7.9": "Vx014263",
            "7.14": "Vx014264",
            "7.15": "Vx014265",
            "7.17": "Vx014266",
            "7.18": "Vx014267",
            "7.20": "Vx014262",
        }
        h_valores: dict[str, Decimal] = {}
        h_inspectores: dict[str, InspectorFormula] = {}
        for fila, vec_key in reglas_h.items():
            arbol_h = _con_override(
                Var(f"Ingresos {fila}H (Modificado)", origen="digitado"),
                Var(vec_key, origen="vector"),
            )
            resultado_h = arbol_h.resolver(contexto)
            h_valores[fila] = resultado_h.valor
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
            contexto[f"Ingresos {codigo}B"] = resultado.valor
            if mostrar_formulas:
                b_inspectores[codigo] = _a_inspector(resultado)

        # --- Col. F ---
        f_valores: dict[str, Decimal] = {}
        f_inspectores: dict[str, InspectorFormula] = {}
        for codigo in self._filas_con_f():
            arbol_f = self._arbol_f(codigo, h_valores)
            resultado = arbol_f.resolver(contexto)
            f_valores[codigo] = resultado.valor
            contexto[f"Ingresos {codigo}F"] = resultado.valor
            if mostrar_formulas:
                f_inspectores[codigo] = _a_inspector(resultado)

        # --- Totalizadores ---
        total = self._resolver_totalizadores(f_valores)

        # --- Armar respuesta ---
        filas = self._armar_filas(
            b_valores,
            f_valores,
            h_valores,
            b_inspectores if mostrar_formulas else None,
            h_inspectores if mostrar_formulas else None,
            f_inspectores if mostrar_formulas else None,
        )
        avisos = self._calcular_avisos(calc4064, externos.CRRP, v)

        return IngresosResponse(
            filas=filas,
            totales=TotalizadoresIngresos(
                fila_7_12=total["fila_7_12"],
                fila_7_total=total["fila_7_total"],
            ),
            avisos=avisos,
        )

    # ------------------------------------------------------------------
    # Construccion de arboles de Col. B
    # ------------------------------------------------------------------

    def _construir_arboles_b(self) -> dict[str, Nodo]:
        """Devuelve {codigo_fila: Nodo} con las formulas de Col. B."""

        def dig_b(fila: str) -> Nodo:
            return Var(f"Ingresos {fila}B", origen="digitado")

        return {
            "7.1": MaxD(
                Var("Vx012188", "vector"),
                (
                    Var("Vx013384", "vector")
                    + Var("Vx013394", "vector")
                    + Var("Vx013395", "vector")
                    + Var("Vx013396", "vector")
                ),
            ),
            "7.2": MaxD(
                Var("Vx012194", "vector") - Var("Vx013257", "vector"),
                (
                    Pos(Var("Vx013372", "vector") - Var("Vx013381", "vector"))
                    + Var("Vx013387", "vector")
                    + Var("Vx013382", "vector")
                    + Var("Vx013383", "vector")
                ),
            ),
            "7.3": MaxD(
                Var("Vx012189", "vector"),
                (
                    Var("Vx013365", "vector")
                    + Var("Vx013366", "vector")
                    + Var("Vx013367", "vector")
                    + Var("Vx013368", "vector")
                    + Var("Vx013369", "vector")
                    + Var("Vx013370", "vector")
                    + Var("Vx013371", "vector")
                    + Var("Vx013385", "vector")
                ),
            ),
            "7.4": Var("Vx012191", "vector"),
            "7.5": MaxD(
                Var("Vx012192", "vector"),
                Var("Vx013379", "vector") + Var("Vx013380", "vector"),
            ),
            "7.6": MaxD(
                Var("Vx012193", "vector"),
                Var("Vx013378", "vector"),
            ),
            "7.7": MaxD(
                Var("Vx012195", "vector"),
                (
                    Var("Vx013373", "vector")
                    + Var("Vx013374", "vector")
                    + Var("Vx013375", "vector")
                    + Var("Vx013376", "vector")
                ),
            ),
            "7.8": Var("Vx012197", "vector"),
            "7.9": MaxD(
                Var("Vx013257", "vector"),
                Var("Vx013377", "vector"),
            ),
            "7.10": (
                Var("Vx014255", "vector")
                + Var("Vx014256", "vector")
                + Var("Vx014257", "vector")
                + Var("Vx014258", "vector")
                + Var("Vx014259", "vector")
                + Var("Vx014260", "vector")
                + Var("Vx014261", "vector")
                + Var("Vx014263", "vector")
            ),
            "7.11": dig_b("7.11"),
            "7.13": dig_b("7.13"),
            "7.14": _con_override(
                dig_b("7.14"),
                (
                    Var("Vx010118", "vector")
                    + Var("Vx012830", "vector")
                    + Var("Vx010240", "vector")
                    + Var("Vx013639", "vector")
                ),
            ),
            "7.15": self._arbol_715(),
            "7.16": dig_b("7.16"),
            "7.17": (
                Pos(Var("Vx010145", "vector") - Var("Vx012210", "vector"))
                + Pos(
                    Var("Vx010357", "vector")
                    + Var("Vx010974", "vector")
                    - Var("Vx010358", "vector")
                )
                + Pos(
                    Var("Vx010059", "vector")
                    - (Var("Vx010088", "vector") + Var("Vx010985", "vector"))
                )
            ),
            "7.18": (
                Pos(Var("Vx010238", "vector") - Var("Vx010239", "vector"))
                + Pos(Var("Vx010236", "vector") - Var("Vx010237", "vector"))
                + Pos(Var("Vx010934", "vector") - Var("Vx011015", "vector"))
            ),
            "7.19": _con_override(
                dig_b("7.19"),
                (
                    Var("Vx013633", "vector")
                    + Var("Vx013634", "vector")
                    + Var("Vx013635", "vector")
                    + Var("Vx013636", "vector")
                    + Var("Vx013637", "vector")
                    + Var("Vx013638", "vector")
                ),
            ),
            "7.20": _con_override(
                dig_b("7.20"),
                (
                    Var("Vx013640", "vector")
                    + Var("Vx013641", "vector")
                    + Var("Vx013642", "vector")
                    + Var("Vx013643", "vector")
                    + Var("Vx013644", "vector")
                    + Var("Vx013645", "vector")
                ),
            ),
            "7.25": Constante(CERO),
            "7.26": Constante(CERO),
            "7.27": dig_b("7.27"),
        }

    # ------------------------------------------------------------------
    # Arbol condicional 7.15
    # ------------------------------------------------------------------

    def _arbol_715(self) -> Nodo:
        """SI(Calc4064 > 0 => Calc4064;
        SI(Calc4075==1 and Calc4064==0 => 0; Vx012209))"""
        return Si(
            cond_fn=lambda ctx: isinstance(ctx.get("Calc4064"), Decimal) and ctx["Calc4064"] > CERO,
            verdadero=Var("Calc4064", origen="externo"),
            falso=Si(
                cond_fn=lambda ctx: (
                    ctx.get("Calc4075") == 1
                    and (not isinstance(ctx.get("Calc4064"), Decimal) or ctx["Calc4064"] == CERO)
                ),
                verdadero=Constante(CERO),
                falso=Var("Vx012209", origen="vector"),
                descripcion="Calc4075==1 y Calc4064==0",
            ),
            descripcion="Calc4064 > 0",
        )

    # ------------------------------------------------------------------
    # Columna F
    # ------------------------------------------------------------------

    def _filas_con_f(self) -> set[str]:
        return {
            "7.1",
            "7.2",
            "7.3",
            "7.4",
            "7.5",
            "7.6",
            "7.7",
            "7.8",
            "7.9",
            "7.10",
            "7.11",
            "7.13",
            "7.14",
            "7.15",
            "7.16",
            "7.17",
            "7.18",
            "7.19",
            "7.20",
            "7.27",
        }

    def _arbol_f(self, codigo: str, h_valores: dict) -> Nodo:
        """Construye el arbol de Col. F: POS(B +/- H - C - D - E)."""
        avanzadas = {"7.14", "7.15", "7.17", "7.18", "7.20"}
        b = Var(f"Ingresos {codigo}B", origen="calculado")
        c = Var(f"Ingresos {codigo}C", origen="digitado")
        d_col = Var(f"Ingresos {codigo}D", origen="digitado")
        e = Var(f"Ingresos {codigo}E", origen="digitado")

        if codigo in avanzadas:
            h_val = h_valores.get(codigo, CERO)
            return Pos(b + Constante(h_val) - c - d_col - e)
        return Pos(b - c - d_col - e)

    # ------------------------------------------------------------------
    # Totalizadores
    # ------------------------------------------------------------------

    def _resolver_totalizadores(self, f_vals: dict) -> dict:
        """Calcula fila_7_12 y fila_7_total desde los valores de F."""
        f12 = (
            f_vals.get("7.1", CERO)
            + f_vals.get("7.2", CERO)
            + f_vals.get("7.3", CERO)
            + f_vals.get("7.4", CERO)
            + f_vals.get("7.5", CERO)
            + f_vals.get("7.6", CERO)
            + f_vals.get("7.7", CERO)
            - f_vals.get("7.8", CERO)
            + f_vals.get("7.9", CERO)
            + f_vals.get("7.11", CERO)
        )
        fila_7_12 = f12 if f12 > CERO else CERO

        total = (
            fila_7_12
            + f_vals.get("7.13", CERO)
            + f_vals.get("7.14", CERO)
            + f_vals.get("7.15", CERO)
            + f_vals.get("7.16", CERO)
            + f_vals.get("7.17", CERO)
            + f_vals.get("7.18", CERO)
            + f_vals.get("7.19", CERO)
            + f_vals.get("7.20", CERO)
            + f_vals.get("7.25", CERO)
            + f_vals.get("7.26", CERO)
            + f_vals.get("7.27", CERO)
            + f_vals.get("7.10", CERO)
        )
        return {"fila_7_12": fila_7_12, "fila_7_total": total}

    # ------------------------------------------------------------------
    # Armado de respuesta
    # ------------------------------------------------------------------

    def _armar_filas(
        self,
        b: dict,
        f: dict,
        h: dict,
        ins_b: dict[str, InspectorFormula] | None,
        ins_h: dict[str, InspectorFormula] | None,
        ins_f: dict[str, InspectorFormula] | None,
    ) -> list:
        codigos = [
            "7.1",
            "7.2",
            "7.3",
            "7.4",
            "7.5",
            "7.6",
            "7.7",
            "7.8",
            "7.9",
            "7.10",
            "7.11",
            "7.13",
            "7.14",
            "7.15",
            "7.16",
            "7.17",
            "7.18",
            "7.19",
            "7.20",
            "7.25",
            "7.26",
            "7.27",
        ]
        filas = []
        for codigo in codigos:
            concepto, f22 = self.CONCEPTOS[codigo]
            # Construir diccionario de inspectores para esta fila
            inspectores_fila: dict[str, InspectorFormula] | None = None
            if ins_b is not None:
                inspectores_fila = {}
                if codigo in ins_b:
                    inspectores_fila["ingresos_ano"] = ins_b[codigo]
                if ins_h and codigo in ins_h:
                    inspectores_fila["ingresos_adeudados_at_anterior"] = ins_h[codigo]
                if ins_f and codigo in ins_f:
                    inspectores_fila["monto_ingreso_percibido"] = ins_f[codigo]
            filas.append(
                FilaIngreso(
                    codigo=codigo,
                    concepto=concepto,
                    codigo_f22=f22,
                    ingresos_ano=b.get(codigo),
                    ingresos_adeudados_at_anterior=h.get(codigo),
                    monto_ingreso_percibido=f.get(codigo),
                    inspectores=inspectores_fila,
                )
            )
        return filas

    def _calcular_avisos(self, calc4064, crrp, v) -> AvisosIngresos:
        monto_7_10 = (
            v.Vx014255
            + v.Vx014256
            + v.Vx014257
            + v.Vx014258
            + v.Vx014259
            + v.Vx014260
            + v.Vx014261
            + v.Vx014263
        )
        aviso_7_10 = monto_7_10 > CERO

        calc4064_no_existe = not (isinstance(calc4064, Decimal) and calc4064 > CERO)
        aviso_arriendos = calc4064_no_existe and (v.Vx012209 > CERO)

        mostrar_columna_patrimonio = v.Vx010042 == 1
        mostrar_columna_renta_presunta = crrp

        return AvisosIngresos(
            aviso_montos_propuestos_7_10=bool(aviso_7_10),
            aviso_arriendos_bienes_raices=aviso_arriendos,
            mostrar_columna_patrimonio=mostrar_columna_patrimonio,
            mostrar_columna_renta_presunta=mostrar_columna_renta_presunta,
        )


# ------------------------------------------------------------------
# Helpers a nivel modulo
# ------------------------------------------------------------------


def _con_override(digitado: Nodo, formula: Nodo) -> Nodo:
    """Override: si el contribuyente ingreso un valor (>0), se usa; sino la formula."""
    return ReemplazoManual(digitado, formula)


def _a_inspector(r: ResultadoNodo) -> InspectorFormula:
    """Convierte un ResultadoNodo en InspectorFormula (schema Pydantic)."""
    return InspectorFormula(
        valor=r.valor,
        literal=r.literal,
        evaluado=r.evaluado,
        variables_usadas=[
            VariableInfo(
                nombre=v["nombre"],
                valor=v["valor"],
                origen=v["origen"],
            )
            for v in r.variables_usadas
        ],
        pasos=list(r.pasos),
    )
