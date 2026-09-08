"""Contexto de simulacion compartido entre paginas (totales cruzados).

Objeto mutable que el Orquestador crea al inicio y pasa de pagina en pagina
para transportar los totales consolidados que una pagina calcula y otra
consume (ej. la RLI consume el Total de Ingresos y el Total de Egresos).

Se mantiene intencionalmente simple (YAGNI): una bolsa de totales mas el flag
global 'patrimonio_personal' (CDEICalc) disponible para cualquier pagina. No
se modelan todavia saltos retroactivos ni inyecciones temporales de paginas
avanzadas (ej. RRE); se agregaran solo si el negocio lo exige.
"""

from decimal import Decimal

CERO = Decimal("0")


class ContextoSimulacion:
    """Bolsa mutable de totales y flags globales compartidos entre paginas.

    Convencion de claves: '<Modulo>.<Concepto>' (ej. 'Ingresos.TotalIngresos').
    """

    def __init__(self, patrimonio_personal: bool | None = None) -> None:
        # Flag global CDEICalc. Se detona en Ingresos pero su impacto
        # matematico ocurre mas adelante (RLI, Retiros). Disponible aqui para
        # que cualquier pagina lo consuma.
        self.patrimonio_personal = patrimonio_personal
        self._totales: dict[str, Decimal] = {}

    def set_total(self, clave: str, valor: Decimal) -> None:
        """Guarda un total consolidado de una pagina."""
        self._totales[clave] = valor

    def get_total(self, clave: str) -> Decimal:
        """Lee un total consolidado; retorna 0 si aun no fue calculado."""
        return self._totales.get(clave, CERO)
