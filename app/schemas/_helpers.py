"""Helpers reutilizables para schemas Pydantic.

Define validadores y funciones de conversion compartidas por todos los
modulos del simulador (Ingresos, Egresos, Retiros, etc.). Centralizarlas
evita duplicacion de logica de normalizacion en cada modulo.
"""

from decimal import Decimal


def coerce_to_decimal(value) -> Decimal:
    """Convierte None, cadenas vacias o strings numericos a Decimal.

    Usado como helper dentro de field_validators de Pydantic para garantizar
    que los campos monetarios siempre lleguen como Decimal.
    """
    if value is None:
        return Decimal("0")
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return Decimal("0")
        return Decimal(stripped)
    return Decimal(str(value))


def normalizar_dict_decimal(value) -> dict[str, Decimal]:
    """Normaliza un dict[str, X] a dict[str, Decimal] con claves limpias.

    Transforma valores None, strings vacios o numeros en Decimal. Si value no
    es un dict, retorna dict vacio. Usado en field_validators de
    CamposDigitados y similares.
    """
    if not isinstance(value, dict):
        return {}
    result: dict[str, Decimal] = {}
    for clave, monto in value.items():
        clave = str(clave).strip()
        if monto is None or (isinstance(monto, str) and monto.strip() == ""):
            result[clave] = Decimal("0")
        else:
            result[clave] = Decimal(str(monto))
    return result