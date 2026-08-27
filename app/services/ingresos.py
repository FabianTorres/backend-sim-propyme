"""Servicio de calculo del modulo 'Ingresos' - Pagina 1 del 14D1.

Logica pura de calculo (Clean Architecture): no depende de base de datos ni de
red. Recibe un IngresosRequest y devuelve un IngresosResponse con los campos
calculados (Columnas B y F, totalizadores y avisos).
"""
from decimal import Decimal

from app.schemas.ingresos import (
    AvisosIngresos,
    CamposDigitados,
    ExternosIngresos,
    FilaIngreso,
    IngresosResponse,
    TotalizadoresIngresos,
    VectoresIngresos,
)

CERO = Decimal("0")


def POS(valor: Decimal) -> Decimal:
    """Parte Positiva: devuelve max(valor, 0).

    Equivale a MAX(0, valor). Se aplica sobre valores monetarios (Decimal).
    """
    return valor if valor > CERO else CERO


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

    def calcular(
        self,
        vectores: VectoresIngresos,
        externos: ExternosIngresos,
        digitados: CamposDigitados,
    ) -> IngresosResponse:
        """Calcula todos los campos de salida del modulo Ingresos."""
        v = vectores
        d = digitados
        calc4064 = externos.Calc4064
        calc4075 = externos.Calc4075

        # --- Col. H (montos adeudados AT anterior) por fila ---
        # Prioriza el override manual (digitados) sobre el vector original.
        h = {
            "7.1": d.ingresos_adeudados_at_anterior.get("7.1", v.Vx014255),
            "7.2": d.ingresos_adeudados_at_anterior.get("7.2", v.Vx014256),
            "7.3": d.ingresos_adeudados_at_anterior.get("7.3", v.Vx014257),
            "7.4": d.ingresos_adeudados_at_anterior.get("7.4", v.Vx014258),
            "7.5": d.ingresos_adeudados_at_anterior.get("7.5", v.Vx014259),
            "7.6": d.ingresos_adeudados_at_anterior.get("7.6", v.Vx014260),
            "7.7": d.ingresos_adeudados_at_anterior.get("7.7", v.Vx014261),
            "7.9": d.ingresos_adeudados_at_anterior.get("7.9", v.Vx014263),
            "7.14": d.ingresos_adeudados_at_anterior.get("7.14", v.Vx014264),
            "7.15": d.ingresos_adeudados_at_anterior.get("7.15", v.Vx014265),
            "7.17": d.ingresos_adeudados_at_anterior.get("7.17", v.Vx014266),
            "7.18": d.ingresos_adeudados_at_anterior.get("7.18", v.Vx014267),
            "7.20": d.ingresos_adeudados_at_anterior.get("7.20", v.Vx014262),
        }

        # --- Col. B: Ingresos del anio (Neto) por fila ---
        b = {
            "7.1": IngresosService._b_71(v),
            "7.2": IngresosService._b_72(v),
            "7.3": IngresosService._b_73(v),
            "7.4": v.Vx012191,
            "7.5": IngresosService._max_d(v.Vx012192, v.Vx013379 + v.Vx013380),
            "7.6": IngresosService._max_d(v.Vx012193, v.Vx013378),
            "7.7": IngresosService._max_d(
                v.Vx012195,
                v.Vx013373 + v.Vx013374 + v.Vx013375 + v.Vx013376,
            ),
            "7.8": v.Vx012197,
            "7.9": IngresosService._max_d(v.Vx013257, v.Vx013377),
            "7.10": (
                v.Vx014255 + v.Vx014256 + v.Vx014257 + v.Vx014258
                + v.Vx014259 + v.Vx014260 + v.Vx014261 + v.Vx014263
            ),
            "7.11": d.ingresos_ano.get("7.11", CERO),
            "7.13": d.ingresos_ano.get("7.13", CERO),
            "7.14": d.ingresos_ano.get(
                "7.14",
                v.Vx010118 + v.Vx012830 + v.Vx010240 + v.Vx013639,
            ),
            "7.15": IngresosService._b_715(calc4064, calc4075, v),
            "7.16": d.ingresos_ano.get("7.16", CERO),
            "7.17": IngresosService._b_717(v),
            "7.18": IngresosService._b_718(v),
            "7.19": d.ingresos_ano.get(
                "7.19",
                v.Vx013633 + v.Vx013634 + v.Vx013635 + v.Vx013636
                + v.Vx013637 + v.Vx013638,
            ),
            "7.20": d.ingresos_ano.get(
                "7.20",
                v.Vx013640 + v.Vx013641 + v.Vx013642 + v.Vx013643
                + v.Vx013644 + v.Vx013645,
            ),
            "7.25": CERO,
            "7.26": CERO,
            "7.27": d.ingresos_ano.get("7.27", CERO),
        }

        # --- Col. F: Monto Ingreso Percibido por fila ---
        f = self._calcular_f(b, h, d)

        # --- Totalizadores ---
        # Segun el SII, el total debe representar la Columna F (Monto Ingreso Percibido)
        # Se usa .get() porque filas como 7.25 y 7.26 no tienen calculo de F definido
        fila_7_12 = POS(
            f.get("7.1", CERO) + f.get("7.2", CERO) + f.get("7.3", CERO)
            + f.get("7.4", CERO) + f.get("7.5", CERO) + f.get("7.6", CERO)
            + f.get("7.7", CERO) - f.get("7.8", CERO) + f.get("7.9", CERO)
            + f.get("7.11", CERO)
        )
        total_ingresos = (
            fila_7_12
            + f.get("7.13", CERO) + f.get("7.14", CERO) + f.get("7.15", CERO)
            + f.get("7.16", CERO) + f.get("7.17", CERO) + f.get("7.18", CERO)
            + f.get("7.19", CERO) + f.get("7.20", CERO) + f.get("7.25", CERO)
            + f.get("7.26", CERO) + f.get("7.27", CERO) + f.get("7.10", CERO)
        )

        filas = self._armar_filas(b, f, h)
        avisos = self._calcular_avisos(calc4064, externos.CRRP, v)

        return IngresosResponse(
            filas=filas,
            totales=TotalizadoresIngresos(
                fila_7_12=fila_7_12,
                fila_7_total=total_ingresos,
            ),
            avisos=avisos,
        )
# --------------------------------------------------------------- #
    # Funciones puras de formula (columna B)
    # --------------------------------------------------------------- #
    @staticmethod
    def _max_d(a: Decimal, s: Decimal) -> Decimal:
        """MAX(a; s) con Decimal."""
        return a if a > s else s

    @staticmethod
    def _b_71(v) -> Decimal:
        # MAX(Vx012188; Vx013384 + Vx013394 + Vx013395 + Vx013396)
        return IngresosService._max_d(
            v.Vx012188,
            (v.Vx013384 + v.Vx013394 + v.Vx013395 + v.Vx013396),
        )

    @staticmethod
    def _b_72(v) -> Decimal:
        # MAX(Vx012194 - Vx013257;
        #     POS(Vx013372 - Vx013381) + Vx013387 + Vx013382 + Vx013383)
        return IngresosService._max_d(
            v.Vx012194 - v.Vx013257,
            (POS(v.Vx013372 - v.Vx013381)
             + v.Vx013387 + v.Vx013382 + v.Vx013383),
        )

    @staticmethod
    def _b_73(v) -> Decimal:
        # MAX(Vx012189; Vx013365+...+Vx013371 + Vx013385)
        return IngresosService._max_d(
            v.Vx012189,
            (v.Vx013365 + v.Vx013366 + v.Vx013367 + v.Vx013368
             + v.Vx013369 + v.Vx013370 + v.Vx013371 + v.Vx013385),
        )

    @staticmethod
    def _b_715(calc4064, calc4075, v) -> Decimal:
        """Caso fila 7.15:
        Si Calc4064 > 0                               => Calc4064
        Si Calc4075==1 y (Calc4064==0 o Calc4064=='N') => 0
        Sino                                           => Vx012209
        """
        if isinstance(calc4064, Decimal) and calc4064 > CERO:
            return calc4064
        if calc4075 == 1 and (
            not isinstance(calc4064, Decimal) or calc4064 == CERO
        ):
            return CERO
        return v.Vx012209

    @staticmethod
    def _b_717(v) -> Decimal:
        # POS(Vx010145 - Vx012210)
        # + POS(Vx010357 + Vx010974 - Vx010358)
        # + POS(Vx010059 - (Vx010088 + Vx010985))
        return (
            POS(v.Vx010145 - v.Vx012210)
            + POS(v.Vx010357 + v.Vx010974 - v.Vx010358)
            + POS(v.Vx010059 - (v.Vx010088 + v.Vx010985))
        )
# --------------------------------------------------------------- #
    # Columna F (Monto Ingreso Percibido)
    # --------------------------------------------------------------- #
    def _calcular_f(self, b: dict, h: dict, d) -> dict:
        """Calcula el Monto Ingreso Percibido (col. F) por fila."""

        def basica(row):
            return POS(
                b[row]
                - d.monto_no_percibido.get(row, CERO)
                - d.no_considerar_patrimonio.get(row, CERO)
                - d.factura_renta_presunta.get(row, CERO)
            )

        def avanzada(row):
            return POS(
                b[row]
                + h.get(row, CERO)
                - d.monto_no_percibido.get(row, CERO)
                - d.no_considerar_patrimonio.get(row, CERO)
                - d.factura_renta_presunta.get(row, CERO)
            )

        filas_basicas = {
            "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9",
            "7.10", "7.11", "7.13", "7.16", "7.19", "7.27",
        }
        filas_avanzadas = {"7.14", "7.15", "7.17", "7.18", "7.20"}

        result = {}
        for r in filas_basicas:
            result[r] = basica(r)
        for r in filas_avanzadas:
            result[r] = avanzada(r)
        return result

    def _armar_filas(self, b: dict, f: dict, h: dict) -> list:
        codigos = [
            "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8",
            "7.9", "7.10", "7.11", "7.13", "7.14", "7.15", "7.16", "7.17",
            "7.18", "7.19", "7.20", "7.25", "7.26", "7.27",
        ]
        filas = []
        for codigo in codigos:
            concepto, f22 = self.CONCEPTOS[codigo]
            filas.append(
                FilaIngreso(
                    codigo=codigo,
                    concepto=concepto,
                    codigo_f22=f22,
                    ingresos_ano=b.get(codigo),
                    ingresos_adeudados_at_anterior=h.get(codigo),
                    monto_ingreso_percibido=f.get(codigo),
                )
            )
        return filas

    def _calcular_avisos(self, calc4064, crrp, v) -> AvisosIngresos:
        # Aviso 7.10 (tooltip): sumatoria H en 7.10 > 0 => monto propuesto
        monto_7_10 = (
            v.Vx014255 + v.Vx014256 + v.Vx014257 + v.Vx014258
            + v.Vx014259 + v.Vx014260 + v.Vx014261 + v.Vx014263
        )
        aviso_7_10 = monto_7_10 > CERO

        # Aviso arriendos BR: si Calc4064 NO > 0 .y. Vx012209 > 0
        calc4064_no_existe = not (
            isinstance(calc4064, Decimal) and calc4064 > CERO
        )
        aviso_arriendos = calc4064_no_existe and (v.Vx012209 > CERO)

        # Visibilidad de columnas segun reglas de negocio
        #  - 'No considerar es de Patrimonio Personal' solo si Vx010042=1
        #  - 'Facturas de Renta Presunta' solo si el contribuyente es CRRP
        mostrar_columna_patrimonio = (v.Vx010042 == 1)
        mostrar_columna_renta_presunta = crrp

        return AvisosIngresos(
            aviso_montos_propuestos_7_10=bool(aviso_7_10),
            aviso_arriendos_bienes_raices=aviso_arriendos,
            mostrar_columna_patrimonio=mostrar_columna_patrimonio,
            mostrar_columna_renta_presunta=mostrar_columna_renta_presunta,
        )

    @staticmethod
    def _b_718(v) -> Decimal:
        # POS(Vx010238 - Vx010239) + POS(Vx010236 - Vx010237)
        # + POS(Vx010934 - Vx011015)
        return (
            POS(v.Vx010238 - v.Vx010239)
            + POS(v.Vx010236 - v.Vx010237)
            + POS(v.Vx010934 - v.Vx011015)
        )