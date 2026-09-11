# Playwright Check — Verificación de desarrollo Web QA vs Backend

Herramienta **ad-hoc de desarrollo** que navega el Asistente Propyme del SII
(ambiente QA) con Playwright, lee los valores renderizados en pantalla y los
compara contra el **backend/oráculo** (`backend_sim_propyme`).

> No forma parte de la suite de tests del backend ni del proyecto Playwright
> robusto. Es solo para ir validando valores durante el desarrollo.

## Qué hace

1. Se autentica con **Clave Tributaria** (RUT/clave de QA, datos ficticios).
2. Selecciona el año tributario **2026**.
3. Elige **Nueva información**.
4. En el Home presiona **Ir al Asistente**.
5. Lee la tabla de **Ingresos** y luego, con **Continuar**, la de **Egresos**.
6. Compara cada celda contra el backend y genera un reporte.

## Requisitos

- Python 3.11+ (se usa el venv del proyecto: `venv\Scripts\python.exe`).
- `playwright` instalado en ese venv (`pip install playwright`).
- No se necesita descargar Chromium: se usa **Edge/Chrome del sistema**.
- Backend corriendo en `http://localhost:8002` (ya levantado).

## Cómo correrlo

```powershell
cd devtools\playwright_check
..\..\venv\Scripts\python.exe runner.py
```

Opcional: crear `.env` (copia de `.env.example`) para cambiar URL/RUT/clave.

## Salida

- Consola: resumen `X de Y celdas coinciden` + lista de diferencias.
- Archivos Markdown: `artefactos/reporte_ingresos.md` y
  `artefactos/reporte_egresos.md`.

## Archivos

| Archivo | Rol |
|---|---|
| `runner.py` | Orquesta: backend + navegación + comparación + reporte |
| `auth.py` | Login por Clave Tributaria y reuso de sesión |
| `web_scraper.py` | Navegación del asistente y lectura de tablas |
| `mapeo_campos.py` | Mapeo fila/código y columna/campo entre web y backend |
| `backend_client.py` | Cliente HTTP del endpoint `/simulador/calcular` |
| `comparador.py` | Comparación y clasificación de diferencias |
| `normalizar.py` | Normaliza montos a `Decimal` |
| `reporte.py` | Reporte en consola y Markdown |
| `casos/rut_69500400-1.json` | Payload del caso (vectores + externos + digitados) |

Los archivos `probe_*.py`, `inspect_*.py` y `check_*.py` son scripts
exploratorios usados para descubrir los selectores de la web QA.

## Resultado actual (RUT 69500400-1)

- **Ingresos: 69/69 celdas coinciden.**
- **Egresos: 52/57 celdas coinciden.** Las 5 diferencias son esperadas y
  corresponden al **bug del SII** (trunca en vez de redondear los valores
  reajustados): filas `8.4` y `8.11` (col. B y F), y el total `8` que las
  propaga. El backend redondea (`>=0.5` sube), que es lo correcto.

## Notas

- El payload trae `at: 2025`, pero el año real es **2026** (error solo de dato).
  El backend se consulta con `at=2025` porque es el que carga los parámetros de
  reajuste `parametros_2025.json` (P77=0.19, P179=1). Si el reajuste de 2026
  difiere, hay que alinear los parámetros en el backend.
- `HEADLESS=false` por defecto para ver el navegador; cambiar a `true` en `.env`
  para correr sin ventana.
