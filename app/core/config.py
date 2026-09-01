"""Configuracion central de la aplicacion.

Centraliza valores de entorno, constantes y settings que aplican a todo el
simulador. Por ahora es minimalista; crecera cuando se integren secretos de
Azure SQL, entornos (dev/staging/prod) y parametros globales.
"""

from pathlib import Path

# Raiz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Directorio de mocks (datos de prueba locales)
MOCKS_DIR = PROJECT_ROOT / "app" / "db" / "mocks"

# Puerto por defecto del servidor
DEFAULT_PORT = 8001

# Ambiente actual (se lee de variable de entorno, fallback a 'development')
# En produccion se setea APP_ENV=production
APP_ENV = "development"