"""Carga de parametros macroeconomicos (Pxxx) por anio tributario.

Los parametros (Pxxx) son constantes de la ley dictadas para cada AT (ej. UTM,
IPC, topes, reajustes). No los envia el Frontend: el backend los tiene
precargados en archivos JSON. Este modulo es la capa de repositorio simple que
los lee y los inyecta en el contexto del motor en tiempo de ejecucion.
"""

import json
from decimal import Decimal
from pathlib import Path

from app.core.config import MOCKS_DIR


def cargar_parametros(at: str) -> dict[str, Decimal]:
    """Lee los parametros del AT indicado y los devuelve como dict[str, Decimal].

    Busca el archivo app/db/mocks/parametros_<at>.json. Si no existe, retorna
    un dict vacio (los parametros faltantes se tratan como ausentes).
    """
    ruta: Path = MOCKS_DIR / f"parametros_{at}.json"
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8") as fh:
        crudo = json.load(fh)
    return {clave: Decimal(str(valor)) for clave, valor in crudo.items()}
