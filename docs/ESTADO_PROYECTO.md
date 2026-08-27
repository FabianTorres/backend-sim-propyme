# Bitácora y Estado del Proyecto: Backend Simulador Propyme (14D1)

## Arquitectura Base
* Framework: FastAPI + Pydantic v2.
* Lógica: Clean Architecture (Endpoints -> Services). No hay DB real, solo Mocks JSON.
* Regla Crítica: El Backend es un Oráculo. El Frontend no calcula NADA, solo envía `vectores` e inputs `digitados`, y el Backend devuelve todo calculado.
* Patrón Override: Si un campo calculado es editable por el usuario, el Backend prioriza el valor enviado en `request.digitados` por sobre la fórmula original (ej. Columna H, y filas 7.14, 7.19, 7.20 de Columna B).

* **Orquestador Global**: Endpoint unico `POST /api/v1/simulador/calcular`. Recibe y responde JSON global con sub-nodos por modulo (ej. `ingresos`). Facilita dependencias cruzadas como RLI.

## Progreso de Modulos (Paginas)
- [x] **Página 1: Ingresos**
  - Schemas creados (166 vectores tipados con Decimal).
  - Lógica de cálculo implementada (`POS`, dependencias, avisos).
  - Patrón Override implementado para Col H y Col B (parcial).
  - Endpoint migrado al Orquestador Global.
- [x] **Correcciones de Pagina 1: Ingresos**
  - Bugfix: totalizadores (7.12 y 7) sumaban Columna B (Ingresos del ano). Corregido para sumar Columna F (Monto Ingreso Percibido) segun reglas SII.
  - Ajuste: `.get(key, CERO)` en lugar de acceso directo a `f[key]` para filas sin calculo de F (7.25, 7.26).
- [x] **Refactor Arquitectonico: Orquestador Global**
  - Creado `app/schemas/orquestador.py`: `SimuladorGlobalRequest` / `SimuladorGlobalResponse` con sub-nodos por modulo.
  - Creado `app/services/orquestador.py`: `OrquestadorService` que coordina `IngresosService` (futuros Egresos, RLI, etc.).
  - Creado `app/api/endpoints/simulador.py`: endpoint unico `POST /api/v1/simulador/calcular`.
  - Eliminado `app/api/endpoints/ingresos.py` (reemplazado por el endpoint global).
  - Refactorizado `IngresosService.calcular()`: recibe `(vectores, externos, digitados)` por separado en lugar de `IngresosRequest`.
  - Mock JSON reestructurado con `digitados.ingresos` anidado.
  - Tests actualizados a la nueva estructura y 100% en verde.
- [ ] **Página 2: Egresos**
  - *Pendiente de inicio.*
- [ ] **Página 3: Retiros**
  - *Pendiente de inicio.*
- [ ] **Página 4: Determinación RLI**
  - *Pendiente de inicio.*
- [ ] **Página 5: Recuadro 17 (F22)**
  - *Pendiente de inicio.*

## Notas Técnicas para el Agente (IA)
* Tipos de dato: Usa siempre `Decimal` para valores monetarios.
* Al iniciar una nueva página, sigue exactamente la misma estructura de carpetas y patrones (schemas, services, tests) usada en `ingresos`.