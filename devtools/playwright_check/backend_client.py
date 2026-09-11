"""Cliente HTTP del backend (oraculo) para obtener los valores esperados."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import config


def calcular(payload: dict) -> dict:
    """POST /simulador/calcular y devuelve el JSON de respuesta completo."""
    url = config.BACKEND_BASE.rstrip("/") + "/simulador/calcular"
    cuerpo = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=cuerpo,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cargar_caso(ruta: Path | None = None) -> dict:
    """Carga el payload del caso (por defecto el RUT 69500400-1)."""
    if ruta is None:
        ruta = config.CASOS_DIR / "rut_69500400-1.json"
    return json.loads(Path(ruta).read_text(encoding="utf-8"))
