# Bitacora y Estado del Proyecto: Backend Simulador Propyme (14D1)

## Arquitectura Base
* Framework: FastAPI + Pydantic v2.
* Logica: Clean Architecture (Endpoints -> Services). No hay DB real, solo Mocks JSON.
* Regla Critica: El Backend es un Oraculo. El Frontend no calcula NADA, solo envia `vectores`, `externos` e inputs `digitados`, y el Backend devuelve todo calculado.
* Patron Override: Si un campo calculado es editable por el usuario, el Backend prioriza el valor enviado en `request.digitados` por sobre la formula original.
* Orquestador Global: Endpoint unico `POST /api/v1/simulador/calcular`. Recibe y responde JSON global con sub-nodos por modulo. Facilita dependencias cruzadas como RLI.

## Contrato de datos globales
* `vectores` y `externos` son GLOBALES y PLANOS: viven en `app/schemas/globales.py`
  (`Vectores`, `Externos`). Ningun vector pertenece a una pagina; cada modulo
  consume el subconjunto que usa. Se declaran solo los codigos usados
  (`extra="ignore"` para forward-compat).
* `digitados` se agrupa por pagina dentro de `DigitadosGlobal`.
* `patrimonio_personal` (flag CDEICalc) es global: se detona en Ingresos pero
  su impacto matematico ocurre en RLI/Retiros. El Orquestador lo inyecta al
  `ContextoSimulacion`.
* Artefactos de auditoria compartidos: `app/schemas/comunes.py`
  (`InspectorFormula`, `VariableInfo`).
* Helpers compartidos: `app/services/_helpers.py` (`_a_inspector`,
  `_con_override`, `clave_celda`).
* Contexto entre paginas: `app/services/contexto.py` (`ContextoSimulacion`).
* Parametros (Pxxx): `app/core/parametros.py` carga `parametros_<at>.json` desde
  `app/db/mocks/` (repositorio simple). Ej. P77/P179 usados por Egresos.

## Progreso de Modulos (Paginas) - 8 en total
- [x] **Pagina 1: Ingresos**
  - Schemas, logica con arboles de expresiones, override, endpoint global.
  - Modo Auditoria (`mostrar_formulas`) con inspectores por columna.
- [x] **Refactor de estructura (previo a Pagina 2)**
  - Vectores/externos extraidos a `app/schemas/globales.py` (globales y planos).
  - `InspectorFormula`/`VariableInfo` extraidos a `app/schemas/comunes.py`.
  - `_a_inspector`/`_con_override`/`clave_celda` extraidos a `app/services/_helpers.py`.
  - Creado `app/services/contexto.py` con `ContextoSimulacion` (totales cruzados).
  - Orquestador inyecta `patrimonio_personal` y guarda totales de Ingresos.
- [x] **Pagina 2: Egresos**
  - Schemas (`egresos.py`) y servicio `EgresosService` con arboles de expresiones.
  - Condicional Vx014022 (reajuste P77+P179), override en filas editables, fila 8.31 (suma de H).
  - Aviso `aviso_arriendos_pagados`, totalizador `fila_8_total` (incluye 8.12).
  - Nueva capa de parametros (`app/core/parametros.py` + `parametros_2025.json`).
  - Externo nuevo `Calc4066` agregado a `Externos`.
  - Redondeo de resultados a cero decimales (`redondear_monto`, redondeo normal >=0.5).
- [x] **Pagina 3: Retiros**
  - Schemas `app/schemas/retiros.py` y `app/schemas/rre.py`; servicio `RetirosService`.
  - Pagina casi de solo ingreso: calcula `[1044]`/`[1045]` (usando las variables
    `H2..I17` del RRE), las derivadas `1040..1052`, los totales `RET30/RET14/RET15`
    y las habilitaciones/validaciones.
  - Vectores nuevos en `globales.py`: `Vx014301`, `Vx012951`, `Vx014661/4662/4663`,
    `Vx010599`. Los centinelas `900000000000000` no se normalizan (se usan tal cual).
  - Flujo no lineal: `H2..I17` viajan en `digitados.rre` (no en `digitados.retiros`).
  - Modo Auditoria: `inspectores` con claves `1044`, `1045`, `ret30`, `ret15`,
    `ret14.<rut>`, `validacion_1044/1045` y `fila<i>_validacion_f1/f2`.
  - Validacion por fila (backend): `RET5>=RET6+RET7` y `RET10>=RET11+RET12`
    (flags `validacion_f1`/`validacion_f2` por fila).
  - Todos los calculos usan el motor de formulas (arboles); sin operadores nativos.
  - Nota: la web NO muestra valores calculados en Retiros (se usan para RRE).
- [ ] **Pagina 4: Determinacion RLI** (depende de Ingresos y Egresos)
- [ ] **Pagina 5: Base Imponible**
- [ ] **Pagina 6: Capital Propio Tributario**
- [ ] **Pagina 7: Registro Renta Empresarial (RRE)**
- [ ] **Pagina 8: Confirmacion de resultados**

## Notas Tecnicas para el Agente (IA)
* Tipos de dato: Usa siempre `Decimal` para valores monetarios.
* Los vectores/externos son globales: al necesitar un vector nuevo, agregarlo a
  `app/schemas/globales.py` (nunca a un schema de pagina).
* Al iniciar una nueva pagina, sigue la estructura de `ingresos` (schemas, services, tests).
* **PROHIBIDO usar matematica nativa en Servicios**: todos los calculos se
  construyen devolviendo objetos `Nodo` desde `app.core.motor_formulas`. Usa
  `Var`, `MaxD`, `Pos`, `Si`, etc. Revisa `docs/MOTOR_FORMULAS.md`.
* La convencion de claves de celda es `<Modulo> <fila><col>` (usa `clave_celda`
  desde `app/services/_helpers.py`).
* El flujo entre paginas se hace con `ContextoSimulacion` (claves `<Modulo>.<Concepto>`).
* Modo Auditoria: las 8 paginas exponen `inspectores` ("Caja de Cristal").

## Contexto de datos (RIAC) y flujos no lineales (ver AGENTS.md seccion 12)
* El asistente real del SII obtiene TODO del RIAC (vectores, calcs, atributos,
  socios). Nuestro backend NO accede al RIAC: el frontend envia el equivalente
  via un Excel convertido a `vectores`/`externos`/`digitados`.
* La lista de socios no llega del RIAC hacia nosotros: el analista QA la ingresa
  a mano en el formulario y usa "Recalcular".
* Retiros es una pagina de flujo no lineal: `H2, H3, H6, H7, I4, I17` vienen del
  RRE (Pagina 7) y se reciben como digitados dentro del request.
* **Reglas de UI vs simulador:** las habilitaciones/bloqueos de columnas del SII
  (ej. Retiros: filas RIAC vs nuevas) son del SII real y se certifican contra la
  web real. En el simulador/frontend **todas las celdas son editables** (es una
  maqueta de ingreso de datos; el analista digita lo que el caso necesite).

## Advertencias y Casos Extremos Conocidos (Edge Cases)
* **Amnesia de Vectores en UI:** la API es Stateless. Si el usuario edita un
  campo, el payload DEBE incluir igual el bloque `vectores` y `externos`
  completo. Si no se envian, Pydantic los inicializa en 0.
* **Totalizadores:** todo totalizador general de una tabla (ej. Fila 7 en
  Ingresos) suma la columna correcta segun reglas SII (Col. F), nunca la Col. B.
* **Redondeo de resultados (regla):** los RESULTADOS calculados se redondean a
  cero decimales con `redondear_monto` (redondeo normal >=0.5 sube). Los
  insumos no se redondean. Ver `app/utils/matematicas.py`.
* **Bug del SII (trunca en vez de redondear):** la web del SII trunca los
  valores reajustados (ej. Egresos 8.4 con reajuste P77+P179) en vez de
  redondear, generando diferencias de centavos/pesos. Los QA lo reportaron.
  Nuestro backend aplica redondeo normal (correcto).