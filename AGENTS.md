# AGENTS.md — Instrucciones completas para agentes de IA

> Lee este archivo COMPLETO antes de tocar el codigo. Contiene el proposito, el
> por que, el como, las reglas estrictas y donde encontrar cada informacion.

## 1. Proposito (que es y por que existe)

Este repo (`backend_sim_propyme`) es el **Backend / Motor de Reglas** del
ecosistema de Certificacion de Calidad del Asistente Propyme del SII (Servicio
de Impuestos Internos de Chile).

**Por que existe:** el SII tiene un asistente web (Propyme) que calcula
impuestos. El equipo de QA necesita certificar que la web calcula bien. Para
eso hay 3 proyectos:
1. Generador de casos de prueba (proyecto 1).
2. **Este backend (proyecto 2): el oraculo que calcula la respuesta correcta.**
3. Automatizador Playwright (proyecto 3), que compara la web contra el backend.

**Rol de este proyecto:** dado un caso (`vectores` + `externos` + `digitados`),
aplicar la logica tributaria oficial y devolver los resultados esperados
(campos calculados). No tiene interfaz grafica; es una API REST pura,
determinista y trazable.

## 2. Arquitectura (como funciona)

- **Clean Architecture** en FastAPI + Pydantic v2.
- **Orquestador Global:** un unico endpoint `POST /api/v1/simulador/calcular`.
  Recibe un payload global y devuelve un JSON global con sub-nodos por modulo.
- Cada **pagina** (Ingresos, Egresos, ...) es un **Service** puro
  (`IngresosService`, `EgresosService`, ...) llamado secuencialmente por
  `OrquestadorService`, que administra un `ContextoSimulacion` con totales
  cruzados entre paginas.
- **STATELESS (critico):** el backend es un oraculo sin memoria. No hay BD ni
  estado. El frontend envia TODO (historia completa) en cada request.

## 3. Estructura de carpetas

```
app/
  api/        # router + endpoints (simulador.py, health.py)
  core/       # config.py, motor_formulas.py, parametros.py
  db/mocks/   # mock_simulador_global.json, parametros_<at>.json
  schemas/    # globales.py, comunes.py, <pagina>.py, orquestador.py, _helpers.py
  services/   # orquestador.py, <pagina>.py, contexto.py, _helpers.py
  utils/      # matematicas.py (CERO, POS, max_d, redondear_monto)
tests/        # conftest.py + test_*.py (pytest)
docs/         # documentacion de negocio y tecnica
```

## 4. Donde encontrar la informacion (mapa de docs)

| Documento | Cuando leerlo |
|---|---|
| `AGENTS.md` (este) | Punto de entrada: proposito, reglas y mapa |
| `.clinerules` | Reglas operativas (Cline) |
| `docs/ESTADO_PROYECTO.md` | Bitacora/estado: que esta hecho, edge cases, decisiones |
| `docs/MOTOR_FORMULAS.md` | Detalle del motor de arbol de expresiones (Modo Auditoria) |
| `docs/Pagina_1_14D1.md` | Reglas de negocio de Ingresos |
| `docs/Pagina_2_Egresos.md` | Reglas de negocio de Egresos |
| `docs/GUIA_FRONTEND.md` | Contrato request/response para el frontend |
| `app/db/mocks/README.md` | Estructura de los mocks JSON |
| `README.md` (raiz) | Vision general breve para humanos |

## 5. Reglas ESTRICTAS (no negociables)

1. **Decimal, nunca float**: montos y calculos en `Decimal` (o `int`).
2. **Arbol de expresiones para TODO calculo**: construye formulas con nodos
   (`Var`, `MaxD`, `Pos`, `Si`, etc.) de `app/core/motor_formulas.py`.
   PROHIBIDO usar operadores Python nativos para el resultado final.
3. **Override primero**: el valor digitado SIEMPRE prioriza sobre la
   formula/vector (`_con_override` / patron `ReemplazoManual`).
4. **Stateless**: nunca guardes estado; todo entra por el request.
5. **TDD**: escribe el test primero, luego la logica.
6. **Sin endpoints por pagina**: todo modulo se llama desde `OrquestadorService`.
7. **Schemas nuevos al request global**: todo schema nuevo se integra al
   `SimuladorGlobalRequest`/`SimuladorGlobalResponse` en `app/schemas/orquestador.py`.
8. **Redondeo de resultados**: los RESULTADOS se redondean a cero decimales con
   `redondear_monto` (>=0.5 sube). Los insumos NO se redondean.
9. **Estilo**: comentarios en espanol, sin tildes, impersonales ("Se implemento...").
10. **No rompas lo que funciona**: si hay una contradiccion en la doc de negocio,
    AVISALO; no la resuelvas en silencio.

## 6. Convenciones clave

- **clave_celda**: las celdas del contexto se nombran `<Modulo> <fila><col>`
  (ej. `Ingresos 7.1B`). Usa `clave_celda` de `app/services/_helpers.py`.
- **Parametros (Pxxx)**: `cargar_parametros(at)` desde `app/core/parametros.py`
  + `app/db/mocks/parametros_<at>.json`.
- **Modo Auditoria**: `mostrar_formulas=true` agrega `inspectores` por columna
  (valor, literal, evaluado, variables_usadas, pasos).
- **ContextoSimulacion**: totales cruzados entre paginas, claves
  `<Modulo>.<Concepto>` (ej. `Ingresos.TotalIngresos`).

## 7. Contrato de datos

- `vectores` y `externos` son GLOBALES y PLANOS (un solo diccionario, compartido
  por todas las paginas). Se declaran solo los codigos usados (`extra="ignore"`).
- `digitados` se agrupa por pagina.
- `patrimonio_personal` (flag CDEICalc) es global.
- La respuesta trae un sub-nodo por pagina.

## 8. Estado del proyecto (8 paginas)

- [x] 1. Ingresos
- [x] 2. Egresos
- [x] 3. Retiros
- [ ] 4. Determinacion RLI (depende de Ingresos y Egresos)
- [ ] 5. Base Imponible
- [ ] 6. Capital Propio Tributario
- [ ] 7. Registro Renta Empresarial (RRE)
- [ ] 8. Confirmacion de resultados

## 9. Como agregar una pagina nueva

1. `app/schemas/<pagina>.py` (schemas de digitados y respuesta).
2. Agregar vectores/externos a `app/schemas/globales.py`.
3. Nodo en `DigitadosGlobal` y `SimuladorGlobalResponse` (`app/schemas/orquestador.py`).
4. `app/services/<pagina>.py` (`<Pagina>Service`, espejo de `IngresosService`).
5. Llamar el service en `OrquestadorService` y guardar totales en `ContextoSimulacion`.
6. `tests/test_<pagina>.py` (TDD: primero el test).

## 10. Decisiones de negocio y problemas conocidos

- **Bug del SII (trunca vs redondea)**: la web del SII truncaba los valores
  reajustados; los QA lo reportaron. Nosotros redondeamos (>=0.5 sube) a cero
  decimales sobre resultados.
- **8.12 (Egresos)**: se INCLUYE en el total (correccion del doc original).
- **Reajuste Egresos**: P77=0.19 y P179=1 (factor 1.19) cuando Vx014022=1.
- **Doc desactualizado**: `Pagina_1_14D1.md` dice "5 pantallas"; son 8.

## 11. Como correr los tests

```bash
cd backend_sim_propyme
python -m pytest
```

## 12. Contexto de datos (RIAC) y flujos no lineales

**De donde salen los datos.** El asistente real del SII (QA) solo recibe RUT +
clave; internamente rescata TODOS los datos del contribuyente (vectores `Vx`,
`Calc`, atributos, socios) desde el **RIAC**. Nuestro backend NO accede al RIAC,
asi que el frontend lo compensa enviando el equivalente del RIAC en el payload:
el analista sube un **Excel** que el frontend transforma a `vectores`, `externos`
y `digitados`. El backend recibe lo mismo que el asistente obtendria del RIAC.

**Unica excepcion: la lista de socios.** El asistente obtiene los socios del
RIAC; nosotros no. Solucion: el analista QA **ingresa manualmente** los socios (y
los demas datos de esa pantalla) en el formulario y luego presiona
**Recalcular**, que reenvia toda la informacion (incluida la digitada a mano) al
backend para obtener los resultados esperados.

**Dos paginas con flujo no lineal.** Hay dos pantallas donde el asistente NO
avanza solo hacia adelante. Una es **Retiros**: las variables `H2, H3, H6, H7,
I4, I17` provienen de la pagina **RRE** (Registro Renta Empresarial, Pagina 7).
En la realidad, el contribuyente llega a Retiros, digita, sigue hasta RRE, digita
`H2..I4`, y el sistema le avisa que debe **volver a Retiros** para recalcular.
Nosotros no replicamos ese "flujo", pero SI necesitamos recibir esos valores
digitados (`H2..I4`) dentro del request para poder calcular [1044]/[1045].

**Rol del simulador en la certificacion.** El backend sirve para: (1) generar
casos de prueba, (2) resolver dudas de la certificacion, y (3) entregar al
proyecto Playwright un archivo (formato aun en definicion) con los campos
**digitados** y los **resultados calculados** esperados. El certificador
Playwright recorre TODAS las paginas de la web y compara; si algo no coincide, se
escala al analista QA, quien define (apoyandose en el Simulador) si es un error
de nuestro calculo o un problema del SII.

**Reglas de UI (habilitacion/bloqueo) y el simulador.** Las reglas de
habilitacion/bloqueo de columnas del SII (ej. Retiros: filas provenientes del
RIAC vs filas nuevas) son comportamiento del **SII real** y se certifican
**contra la web real** (proyecto Playwright), NO en nuestra maqueta. Nuestro
frontend/simulador es una herramienta de **ingreso de datos**: todas las celdas
son editables y el analista digita lo que el caso necesite; no se replican los
bloqueos del SII. El flag `es_registro_nuevo` se sigue enviando (semantico), pero
el backend no lo usa para calcular.