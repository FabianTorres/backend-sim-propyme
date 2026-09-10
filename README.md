# Backend Simulador Asistente Propyme (SII)

API REST (FastAPI) que calcula la logica tributaria del Asistente Propyme del
SII. Actua como ORACULO: recibe vectores + externos + digitados y devuelve
todos los resultados calculados en un solo JSON.

> **Para agentes de IA:** empieza por `docs/README.md` (contexto, convenciones
> y mapa de documentacion) y `docs/ESTADO_PROYECTO.md` (bitacora y estado).

## Stack
- Python 3.11+, FastAPI, Uvicorn, Pydantic v2, pytest.

## Arquitectura
- Clean Architecture: `api` -> `services` -> `schemas`.
- Orquestador Global: endpoint unico `POST /api/v1/simulador/calcular`.
- Stateless: el frontend envia TODO en cada request.

## Documentacion
- `docs/README.md` — contexto y convenciones para agentes (LEER PRIMERO).
- `docs/ESTADO_PROYECTO.md` — bitacora y estado.
- `docs/MOTOR_FORMULAS.md` — motor de arbol de expresiones.
- `docs/Pagina_1_14D1.md` / `docs/Pagina_2_Egresos.md` — reglas de negocio.
- `docs/GUIA_FRONTEND.md` — contrato con el frontend.

## Estado (8 paginas)
- [x] 1. Ingresos
- [x] 2. Egresos
- [ ] 3. Retiros
- [ ] 4. Determinacion RLI
- [ ] 5. Base Imponible
- [ ] 6. Capital Propio Tributario
- [ ] 7. Registro Renta Empresarial (RRE)
- [ ] 8. Confirmacion de resultados

## Correr tests
`python -m pytest`