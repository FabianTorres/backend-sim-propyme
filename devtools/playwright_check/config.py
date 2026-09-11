"""Configuracion del checker de desarrollo (Playwright vs Backend)."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _cargar_dotenv(ruta: Path) -> None:
    """Carga pares CLAVE=VALOR de un archivo .env simple (sin dependencias)."""
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip()
        valor = valor.strip().strip('"').strip("'")
        os.environ.setdefault(clave, valor)


_cargar_dotenv(BASE_DIR / ".env")

# Ambiente QA del SII (datos y claves ficticios, solo desarrollo)
QA_URL = os.environ.get("QA_URL", "https://www2qa.sii.cl/asistente-propyme")
RUT = os.environ.get("RUT", "69500400-1")
CLAVE = os.environ.get("CLAVE", "aa11")

# Backend local (ya levantado por el usuario)
BACKEND_BASE = os.environ.get("BACKEND_BASE", "http://localhost:8002/api/v1")

# Directorios y artefactos
CASOS_DIR = BASE_DIR / "casos"
ARTEFACTOS_DIR = BASE_DIR / "artefactos"
STORAGE_STATE = ARTEFACTOS_DIR / "storage_state.json"

# Navegador: por defecto visible para observar el proceso de desarrollo
HEADLESS = os.environ.get("HEADLESS", "false").lower() == "true"

# Canal del navegador Chromium del sistema (evita descargar Chromium de Playwright).
# "msedge" usa Microsoft Edge; "chrome" usa Google Chrome; None usa Chromium de Playwright.
BROWSER_CHANNEL = os.environ.get("BROWSER_CHANNEL", "msedge") or None
