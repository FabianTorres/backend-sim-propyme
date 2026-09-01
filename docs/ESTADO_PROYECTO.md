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
- [x] **Refactor: Arbol de Expresiones / Modo Auditoria**
  - Creado `app/core/motor_formulas.py`: `ResultadoNodo`, `Nodo`, `Suma`, `Resta`, `Multiplicacion`, `MaxD`, `Pos`, `Si`, `Var`, `Constante` con sobrecarga de operadores y unico recorrido `resolver(contexto)`.
  - Refactorizado `IngresosService`: todas las formulas son ahora arboles de `Nodo`. El `contexto` se puebla con vectores, externos y digitados, y los resultados intermedios (B, F) se almacenan para referencias cruzadas.
  - Agregado `mostrar_formulas: bool` en `SimuladorGlobalRequest`. Cuando es True, la respuesta incluye `InspectorFormula` con `literal`, `evaluado` y `variables_usadas` por fila.
  - Golden Master: 9/9 tests existentes pasan sin cambios en valores numericos.
  - Agregado `tests/test_auditor.py` (6 tests) validando los strings del inspector.
  - Extraidas utilidades matematicas compartidas: `app/utils/matematicas.py` (`POS`, `CERO`, `max_d`).
  - Extraidos validadores Pydantic reutilizables: `app/schemas/_helpers.py` (`coerce_to_decimal`, `normalizar_dict_decimal`).
  - Creado `pyproject.toml` con config de proyecto, pytest y ruff.
  - Creado `tests/conftest.py` con fixtures compartidos (`mock_payload`, `mock_global_request`, `datos_ingresos`).
  - Eliminado directorio muerto `app/models/`.
  - `app/core/` ahora tiene `config.py` con constantes reales (`PROJECT_ROOT`, `MOCKS_DIR`, etc.).
  - Health check movido a `app/api/endpoints/health.py`; `main.py` queda limpio (solo inicializacion).
  - Mock renombrado: `mock_ingresos.json` → `mock_simulador_global.json`. Agregado `README.md` en mocks.
  - Orquestador blindado con comentarios-guia `# TODO` en los 4 puntos de extension (schemas entrada/salida, service).
- [x] **Humanizacion del Inspector de Formulas (Modo Auditoria)**
  - Ajustados los pasos de los nodos operadores (`Suma`, `Resta`, `Multiplicacion`, `MaxD`, `Pos`, etc.) para usar `_fmt(ri.valor)` y `_fmt(rd.valor)`, eliminando la anidacion ilegible de historiales completos.
  - Creado nodo `ReemplazoManual` en `app/core/motor_formulas.py` con lenguaje tributario (`ELEGIR(Digitado: ... | Propuesto: ...)` y pasos claros para el contribuyente).
  - Refactorizado `_con_override` en `app/services/ingresos.py` para usar `ReemplazoManual` en lugar del nodo generico `Si`.
  - Actualizado `tests/test_auditor.py` con los nuevos strings esperados; 18/18 tests pasan.
  - Implementado un Estándar Global de Nomenclatura para el inspector: Se eliminaron variables internas como `dig_C_7.1` en favor del formato legible `[Módulo] [Fila][Columna]` (ej. `Ingresos 7.1B`), facilitando la lectura para QA y Contadores.
  - *Pendiente de inicio.*
- [ ] **Página 3: Retiros**
  - *Pendiente de inicio.*
- [ ] **Página 4: Determinación RLI**
  - *Pendiente de inicio.*
- [ ] **Página 5: Recuadro 17 (F22)**
  - *Pendiente de inicio.*

## Notas Técnicas para el Agente (IA)
* Tipos de dato: Usa siempre `Decimal` para valores monetarios.
* Al iniciar una nueva pagina, sigue exactamente la misma estructura de carpetas y patrones (schemas, services, tests) usada en `ingresos`.
* **PROHIBIDO usar matematica nativa en Servicios:** Todos los calculos en las paginas deben construirse devolviendo objetos `Nodo` (Arbol de Expresiones) importados desde `app.core.motor_formulas`. Nunca uses `+`, `-`, `max()` o `POS()` directamente sobre `Decimal` en un servicio; siempre construye el arbol con `Var`, `MaxD`, `Pos`, `Si`, etc. Revisa `docs/MOTOR_FORMULAS.md` antes de implementar la logica de cualquier pagina nueva.

## Advertencias y Casos Extremos Conocidos (Edge Cases)
* **Amnesia de Vectores en UI:** Recordar que la API es Stateless. Si se simula un request donde el usuario "editó" un campo, el payload de prueba DEBE incluir de todos modos el bloque `vectores` y `externos` completo. Si no se envían, Pydantic los inicializará en `0` y la matemática de la tabla resultante dará ceros.
* **Totalizadores:** Todo totalizador general de una tabla (ej. Fila 7 en Ingresos) debe sumar los valores de la Columna F (Monto Ingreso Percibido), NUNCA los de la Columna B (Ingreso del año).