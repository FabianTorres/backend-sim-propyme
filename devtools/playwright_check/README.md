# Playwright Check — Verificacion de desarrollo Web QA vs Backend

Herramienta **ad-hoc de desarrollo** que navega el Asistente Propyme del SII
(ambiente QA) con Playwright, lee los valores renderizados y los compara contra
el **backend/oraculo** (`backend_sim_propyme`).

> No forma parte de la suite de tests del backend ni del proyecto Playwright
> robusto. Es solo para ir validando valores durante el desarrollo.

## Que hace

1. Se autentica con **Clave Tributaria** (RUT/clave de QA, datos ficticios).
2. Selecciona el anio tributario **2026**.
3. Elige **Recuperar datos** o **Nueva informacion** (ver `modo`).
4. En el Home presiona **Ir al Asistente**.
5. Recorre **Ingresos -> Egresos -> Retiros -> RLI (Pagina 4)** con Continuar.
6. Compara cada valor contra el backend y genera un reporte.

## Requisitos

- Python 3.11+ (venv del proyecto: `venv\Scripts\python.exe`).
- `playwright` instalado en ese venv. No se descarga Chromium: se usa Edge del
  sistema (`BROWSER_CHANNEL=msedge`).
- Backend corriendo en `http://localhost:8002`.

## Scripts

| Archivo | Rol |
|---|---|
| `runner.py` | Compara Ingresos y Egresos (Nueva informacion) vs backend |
| `runner_rli.py` | Llega a RLI, responde el modal 14E y compara 9.x vs backend |
| `probe_rli.py` | Sonda: descubre la pantalla RLI (guarda `12_rli.*`) |
| `construir_caso.py` | Arma un caso (JSON) desde un Excel de propuesta del SII |
| `web_scraper.py` | Navegacion del asistente y lectura de tablas |
| `auth.py` / `config.py` / `backend_client.py` / `comparador.py` / `normalizar.py` / `reporte.py` / `mapeo_campos.py` | Soporte (login, config, HTTP backend, comparacion, reporte, mapeo) |
| `casos/rut_69500400-1.json` | Caso vigente (reconstruido desde el Excel Original) |

Los `probe_*.py`, `inspect_*.py`, `check_*.py`, `diag_*.py`, `dump_*.py` son
scripts exploratorios.

## Como correrlo

```powershell
cd devtools\playwright_check
..\..\venv\Scripts\python.exe runner.py
..\..\venv\Scripts\python.exe runner_rli.py si recuperar sinretiros
```

`runner_rli.py <si|no> <nueva|recuperar> [caso.json] [sinretiros]`:
- `si|no` = respuesta al modal 14E.
- `nueva|recuperar` = inicio del flujo (default `recuperar`).
- `[caso.json]` = caso a usar (default `casos/rut_69500400-1.json`).
- `sinretiros` = ignora los retiros del caso (util porque en QA los socios
  aparecen con montos en 0 -> RET30=0).

Reconstruir un caso desde un Excel:

```powershell
..\..\venv\Scripts\python.exe construir_caso.py <ruta.xlsx> [salida.json] [sinretiros]
```

## Salida

Reportes Markdown en `artefactos/` (`reporte_ingresos.md`, `reporte_egresos.md`,
`reporte_rli_<modo>_<si|no>.md`) + screenshots (`12_rli.png`, `13_rli_*.png`).
La diferencia +/-2 en RLI se marca `OK(+/-2)` (redondeo conocido del SII).

## Caso vigente y resultados (RUT 69500400-1, AT2026)

El caso se reconstruyo desde `propuesta-2026-69500400-1_Original.xlsx`
(Excel vigente del RIAC). Los casos/Excel anteriores fueron **borrados** porque
no coincidian con el ambiente QA.

- **Ingresos: 69/69 celdas coinciden.**
- **Egresos: 52/57.** Las 5 diferencias son el **bug del SII** (trunca en vez de
  redondear los reajustes): filas `8.4`/`8.11` (col. B y F) y el total `8`.
- **RLI (Pagina 4): 8/8** con tolerancia +/-2, en ambos modos (nueva y recuperar):
  - 9.1 = 65.639.532, 9.3 = 64.909.632, 9.5 = 1.075.360, 9.6 = 64.564.172
    (backend difiere +2 por redondeo). 9 = 8.26 = 729.900. Sin socios -> 9.21 = 0.
  - En QA los socios de Retiros aparecen con montos en 0 -> RET30 = 0; por eso la
    comparacion de RLI usa `sinretiros`.

## Notas

- Payload y backend usan `at: 2026` (unico ano tributario). Parametros en
  `app/db/mocks/parametros_2026.json` (P77=0.19, P179=1).
- `HEADLESS=false` por defecto; usar `HEADLESS=true` para correr sin ventana.
- Para dejarlo en un unico caso, `casos/rut_69500400-1.json` es el vigente.
