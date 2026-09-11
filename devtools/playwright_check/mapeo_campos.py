"""Mapeo de filas y columnas entre la tabla web y el response del backend."""

# Orden de filas de la tabla de Ingresos tal como las renderiza la web QA.
# La web omite 7.11, 7.13, 7.16 y 7.27 porque no tienen valores propuestos.
ORDEN_INGRESOS = [
    "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9",
    "7.10", "7.12", "7.14", "7.15", "7.17", "7.18", "7.19", "7.20",
    "7.25", "7.26", "7",
]

# Columna web -> indice de celda (td) dentro de cada fila de Ingresos.
COLUMNAS_INGRESOS = {
    "H": 1,  # ingresos percibidos de montos adeudados de AT anterior
    "B": 3,  # ingresos del anio (neto)
    "C": 5,  # monto no percibido del anio (neto)
    "F": 7,  # monto ingreso percibido
}

# Columna web -> campo del response del backend.
CAMPOS_INGRESOS = {
    "B": "ingresos_ano",
    "H": "ingresos_adeudados_at_anterior",
    "C": "monto_no_percibido",
    "F": "monto_ingreso_percibido",
}

CAMPOS_EGRESOS = {
    "B": "egresos_ano",
    "H": "egresos_adeudados_at_anterior",
    "C": "no_pagadas",
    "F": "monto_egresos_pagados",
}

# Orden de filas de la tabla de Egresos tal como las renderiza la web QA.
# (Pantalla customizada: solo filas con valores propuestos + totalizador.)
ORDEN_EGRESOS = [
    "8.4", "8.6", "8.7", "8.8", "8.9", "8.11", "8.31", "8.5", "8.10",
    "8.14", "8.15", "8.24", "8.25", "8.26", "8.27", "8",
]

# Columna web -> indice de celda (td) dentro de cada fila de Egresos.
COLUMNAS_EGRESOS = {
    "H": 1,  # monto adeudados AT anterior pagados
    "B": 3,  # egresos del anio
    "C": 5,  # no pagadas del anio
    "F": 7,  # monto egresos pagados (total)
}

# Filas con reajuste (Vx014022=1) donde la web trunca y el backend redondea.
FILAS_REAJUSTE_EGRESOS = {
    "8.4", "8.5", "8.6", "8.7", "8.8", "8.9", "8.10", "8.11",
}
