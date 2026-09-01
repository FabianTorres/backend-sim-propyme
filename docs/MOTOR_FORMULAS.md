# Motor de Fórmulas — Árbol de Expresiones (Composite Pattern)

> **Archivo:** `app/core/motor_formulas.py`  
> **Última actualización:** 2025-08-28 (refactor `pasos` + `inspectores` por columna)

---

## 1. Propósito y Filosofía

### 1.1 El Problema: Cálculo Directo sin Trazabilidad

Antes de este refactor, las fórmulas tributarias se evaluaban con operadores
nativos de Python:

```python
# Forma ANTIGUA (PROHIBIDA desde el refactor)
resultado = max_d(v.Vx012188, v.Vx013384 + v.Vx013394 + v.Vx013395 + v.Vx013396)
# resultado = 1000000
```

Esto es rápido, pero **destruye la trazabilidad**. Para QA (Playwright) y
auditores, un `1000000` no dice nada. Necesitan: ¿de dónde salió?, ¿qué
variables se usaron y con qué valores?, ¿cuál fue la fórmula literal del SII?,
¿cuál fue el paso a paso de la resolución?

### 1.2 La Solución: Árbol de Expresiones

Cada fórmula se construye como un **árbol de objetos `Nodo`** que, al
resolverse contra un `contexto` (diccionario de valores), produce en **una
sola pasada bottom-up**:

| Campo | Significado | Ejemplo |
|---|---|---|
| `valor` | Resultado numérico (`Decimal`) | `1000000` |
| `literal` | Fórmula con nombres de variables | `MAX(Vx012188, (Vx013384 + ...))` |
| `evaluado` | Fórmula con valores reales | `MAX(1000000, (100000 + 0 + ...))` |
| `variables_usadas` | Lista `{nombre, valor, origen}` | `[{nombre:"Vx012188", ...}]` |
| `pasos` | Paso a paso `"expresion = resultado"` | `["(100000+0)=100000", "MAX(1M,100k)=1M"]` |

### 1.3 Contrato con el Frontend

El Modo Auditoría se activa con `mostrar_formulas: true` en el
`SimuladorGlobalRequest`. Cuando está activo, **cada fila incluye un
diccionario `inspectores`** con una entrada por columna calculada:

| Llave del dict | Columna | Siempre presente? |
|---|---|---|
| `"ingresos_ano"` | Col. B | Sí (toda fila tiene Col. B) |
| `"ingresos_adeudados_at_anterior"` | Col. H | Solo si la fila tiene override de H |
| `"monto_ingreso_percibido"` | Col. F | Solo si la fila tiene fórmula de F |

Si `mostrar_formulas` es `false`, `inspectores` es `null` y no se genera
sobrecarga de strings ni árboles para H/F.
### 1.4 Ejemplo de respuesta del inspector (fila 7.1)

```json
{
  "codigo": "7.1",
  "ingresos_ano": "2400000",
  "ingresos_adeudados_at_anterior": "14000",
  "monto_ingreso_percibido": "2400000",
  "inspectores": {
    "ingresos_ano": {
      "valor": "2400000",
      "literal": "MAX(Vx012188, (Vx013384 + Vx013394 + Vx013395 + Vx013396))",
      "evaluado": "MAX(2400000, (0 + 0 + 0 + 0))",
      "variables_usadas": [{"nombre":"Vx012188","valor":"2400000","origen":"vector"}, ...],
      "pasos": ["0 + 0 = 0", "MAX(2400000, 0) = 2400000"]
    },
    "ingresos_adeudados_at_anterior": {
      "valor": "14000",
      "literal": "Vx014255",
      "evaluado": "14000",
      "variables_usadas": [{"nombre":"Vx014255","valor":"14000","origen":"vector"}],
      "pasos": ["Valor propuesto por el SII (sin edicion manual) = 14000"]
    },
    "monto_ingreso_percibido": {
      "valor": "2400000",
      "literal": "POS((((Ingresos 7.1B - Ingresos 7.1C) - Ingresos 7.1D) - Ingresos 7.1E))",
      "evaluado": "POS((((2400000 - 0) - 0) - 0))",
      "variables_usadas": [{"nombre":"Ingresos 7.1B","valor":"2400000","origen":"calculado"}, ...],
      "pasos": ["2400000 - 0 = 2400000", "POS(2400000) = 2400000"]
    }
  }
}
```

---

## 2. Catálogo de Nodos

### 2.1 Nodo Base

Clase abstracta con sobrecarga de operadores mágicos (`+`, `-`, `*`, `-unario`).
Método obligatorio: `resolver(contexto: dict) -> ResultadoNodo`.

```python
arbol = Var("A") + Var("B")       # => Suma
arbol = Var("A") - Var("B")       # => Resta
arbol = Var("Ingreso") * 0.19     # => Multiplicacion(el 0.19 se vuelve Constante)
arbol = Var("A") + 100            # => Suma(Var, Constante(100))
```

### 2.2 `Var(nombre, origen, default=CERO)`

Hoja del árbol. Busca su valor en el `contexto`.

| Parámetro | Obligatorio | Descripción |
|---|---|---|
| `nombre` | Sí | Clave exacta en el diccionario `contexto` |
| `origen` | Sí | `"vector"`, `"externo"`, `"digitado"` o `"calculado"` |
| `default` | No | Valor si la clave no existe (default: `CERO`) |

```python
Var("Vx012188", origen="vector")
Var("Calc4064", origen="externo")
Var("dig_B_7.14", origen="digitado")
Var("B_7.1", origen="calculado")       # resultado intermedio de otra fila
```

### 2.3 `Constante(valor)`

Hoja del árbol. Valor fijo.

```python
Constante(Decimal("0"))
Constante(CERO)
```

### 2.4 `Suma(izq, der)` y `Resta(izq, der)`

Generados por `+` y `-`. Cada uno concatena los `pasos` de sus sub-nodos y
agrega su propio paso con formato `"expresion = resultado"`.

```python
Var("A") + Var("B")    # idiomático (preferido)
Var("A") - Var("B")
# paso generado: "(1000000 + 100000) = 1100000"
```

### 2.5 `MaxD(izq, der)`

`MAX(a, b)` del SII. Agrega paso `MAX(a, b) = ganador`.

```python
MaxD(Var("Vx012188","vector"), Var("Vx013384","vector") + Var("Vx013394","vector"))
# literal: "MAX(Vx012188, (Vx013384 + Vx013394))"
# paso:    "MAX(1000000, 100000) = 1000000"
```

### 2.6 `Pos(operando)`

`POS(x) = MAX(0, x)`. Agrega paso `POS(x) = resultado`.

```python
Pos(Var("Vx010145","vector") - Var("Vx012210","vector"))
# literal: "POS((Vx010145 - Vx012210))"
# paso:    "POS(50000) = 50000"
```

### 2.7 `Si(cond_fn, verdadero, falso, descripcion)`

Condicional. Agrega paso `SI(cond) => valor` o `SI(NO cond) => valor`.

```python
Si(
    cond_fn=lambda ctx: ctx.get("Calc4064", CERO) > CERO,
    verdadero=Var("Calc4064", origen="externo"),
    falso=Var("Vx012209", origen="vector"),
    descripcion="Calc4064 > 0",
)
# Si True:  paso="SI(Calc4064 > 0) => 50000"
# Si False: paso="SI(NO Calc4064 > 0) => 0"
```

### 2.8 Formato de los Pasos

Cada nodo operador agrega **un solo paso** al array `pasos`, con el formato
`<expresion_evaluada> = <resultado>`. Como los pasos se heredan bottom-up,
el array final contiene **toda la traza de resolución** desde las hojas.

Ejemplos reales del inspector:
```
"(100000 + 0) = 100000"
"MAX(1000000, 100000) = 1000000"
"POS(50000) = 50000"
"SI(Calc4064 > 0) => 50000"
"SI(NO override digitado presente) => 90000"
```

---

## 3. El Contexto Dinámico

### 3.1 ¿Qué es?

Un **diccionario plano** `dict[str, Any]` que se construye al inicio de
`calcular()` y se **enriquece fila a fila**. Permite **referencias cruzadas**:
una fila puede usar el resultado de una fila anterior.

### 3.2 Construcción inicial

```python
contexto: dict = {}
# Vectores
for field_name, value in v.model_dump().items():
    contexto[field_name] = value       # "Vx012188" → 1000000
# Externos
contexto["Calc4064"] = calc4064
# Digitados (Nomenclatura: Modulo FilaColumna)
contexto["Ingresos 7.11B"] = d.ingresos_ano.get("7.11", CERO)
contexto["Ingresos 7.1C"]  = d.monto_no_percibido.get("7.1", CERO)
contexto["Ingresos 7.1H (Modificado)"] = d.ingresos_adeudados_at_anterior.get("7.1", CERO)
```

### 3.3 Enriquecimiento progresivo

```python
for codigo, arbol in arboles_b.items():
    resultado = arbol.resolver(contexto)
    contexto[f"Ingresos {codigo}B"] = resultado.valor   # inyectado al contexto

for codigo in filas_con_f:
    arbol_f = self._arbol_f(codigo)
    # arbol_f usa Var("Ingresos 7.1B", origen="calculado")
    # ...y el contexto YA tiene Ingresos 7.1B con el valor resuelto
    resultado = arbol_f.resolver(contexto)
    contexto[f"Ingresos {codigo}F"] = resultado.valor
```

### 3.4 Convención de nombres (Estándar Global)

Para mantener la Caja de Cristal legible para QA y contadores, se abandonó el uso de variables de código (ej. `dig_C_7.1`) y se adoptó el estándar `[Módulo] [Fila][Columna]`.

| **Tipo**  | **Significado**            | **Ejemplo**                  |
| --------- | -------------------------- | ---------------------------- |
| Vector    | Vector histórico SII       | `Vx012188`                   |
| Externo   | Variable de otro asistente | `Calc4064`                   |
| Digitado  | Ingreso manual de columna  | `Ingresos 7.14C`             |
| Calculado | Resultado intermedio       | `Ingresos 7.1B`              |
| Override  | Celda en competencia       | `Ingresos 7.1H (Modificado)` |

---

## 4. Orígenes de Variables (`Var.origen`)

Cada `Var` debe declarar su origen. Esto alimenta el inspector y permite a
QA saber exactamente de dónde proviene cada número.

| Origen | Significado | Ejemplo |
|---|---|---|
| `"vector"` | Datos históricos del contribuyente (`Vx...`) | `Var("Vx012188", "vector")` |
| `"externo"` | Variable externa de otro asistente | `Var("Calc4064", "externo")` |
| `"digitado"` | Ingresado manualmente por el usuario | `Var("dig_B_7.14", "digitado")` |
| `"calculado"` | Resultado intermedio de una fila anterior | `Var("B_7.1", "calculado")` |

**Regla:** Nunca uses `Var` sin el parámetro `origen`. El default es
`"vector"`, pero ser explícito evita bugs en el inspector.

---

## 5. Guía para Nuevas Páginas

### 5.1 Checklist

1. **Definir fórmulas como árboles**, no como cálculos directos.
2. **Poblar el contexto** con vectores, externos y digitados usando las
   mismas convenciones de prefijos.
3. **Resolver en orden de dependencia**: primero filas independientes,
   luego las que dependen de resultados anteriores.
4. **Inyectar resultados intermedios** al contexto (`contexto[f"B_{fila}"]`).
5. **Respetar `mostrar_formulas`**: si es `False`, no construir inspectores.

### 5.2 Ejemplo: Fórmula 7.2 (Ingresos)

```python
# SII: MAX(Vx012194 - Vx013257;
#          POS(Vx013372 - Vx013381) + Vx013387 + Vx013382 + Vx013383)

"7.2": MaxD(
    Var("Vx012194", "vector") - Var("Vx013257", "vector"),
    (
        Pos(Var("Vx013372", "vector") - Var("Vx013381", "vector"))
        + Var("Vx013387", "vector") + Var("Vx013382", "vector")
        + Var("Vx013383", "vector")
    ),
)
```

### 5.3 Patrón Override (Reemplazo Manual)

```python
from app.services.ingresos import _con_override

"7.14": _con_override(
    digitado=Var("Ingresos 7.14B", origen="digitado"),
    formula=(Var("Vx010118", "vector") + Var("Vx012830", "vector")
             + Var("Vx010240", "vector") + Var("Vx013639", "vector")),
)
```

_con_override utiliza el nodo ReemplazoManual con evaluación perezosa (lazy evaluation):
- Si el usuario digitó algo (>0) → ignora la fórmula, usa el digitado y agrega el paso "Se utiliza el valor modificado...".
- Si no → ignora el digitado, usa 100% la fórmula y agrega el paso "Valor propuesto por el SII...".

### 5.4 Estructura canónica de `calcular()`

```python
def calcular(self, vectores, externos, digitados, mostrar_formulas=False):
    # 1. Contexto inicial
    contexto = _poblar_contexto(vectores, externos, digitados)

    # 2. Construir árboles (NO resolver aún)
    arboles = self._construir_arboles()

    # 3. Resolver en orden, inyectando al contexto
    for codigo, arbol in arboles.items():
        resultado = arbol.resolver(contexto)
        contexto[f"resultado_{codigo}"] = resultado.valor

    # 4. Armar respuesta
    return self._armar_respuesta(contexto, mostrar_formulas)
```

---

## 6. Anti-Patrones (PROHIBIDO)

### ❌ Usar operadores nativos para cálculos finales

```python
# PROHIBIDO
resultado = v.Vx012188 + v.Vx013384    # No genera trazabilidad
```

### ❌ Construir strings de inspector manualmente

Los strings SIEMPRE deben provenir de `arbol.resolver(contexto).literal`.

### ❌ Usar `float`

Siempre `Decimal`. El motor acepta `int` (lo convierte), pero nunca `float`.

### ❌ Modificar el contexto desde un nodo

El contexto es de solo lectura para los nodos. Solo `calcular()` inyecta
nuevos valores entre resoluciones.

---

## 7. Testing

- **Golden Master:** `tests/test_ingresos.py` — si falla, el árbol está mal.
- **Auditoría:** `tests/test_auditor.py` — valida `inspectores` por columna
  (B, H, F), pasos, variables_usadas, literales y evaluados.
- **Al agregar un nodo:** tests unitarios + `pytest tests/` completo.
- **Suite actual:** 18 tests (9 Golden Master + 9 Auditoría).

---


## 8. Inspectores por Columna

Cada fila de la respuesta, cuando mostrar_formulas=True, contiene un
diccionario inspectores con una entrada por columna calculada:

| Llave | Columna | Arbol usado | Siempre presente? |
|---|---|---|---|
| ingresos_ano | Col. B | _construir_arboles_b() | Si |
| ingresos_adeudados_at_anterior | Col. H | _con_override(dig_H, Vx) | Solo filas con regla H |
| monto_ingreso_percibido | Col. F | _arbol_f() -> Pos(B +/- H - C - D - E) | Solo _filas_con_f() |

Cada InspectorFormula dentro del dict contiene los 5 campos:
valor, literal, evaluado, variables_usadas, pasos.

---

## 9. Referencias

| Recurso | Ruta |
|---|---|
| Codigo del motor | app/core/motor_formulas.py |
| Servicio migrado | app/services/ingresos.py |
| Schemas de salida | app/schemas/ingresos.py -> InspectorFormula, VariableInfo, FilaIngreso.inspectores |
| Schema del request | app/schemas/orquestador.py -> SimuladorGlobalRequest.mostrar_formulas |
| Tests Golden Master | tests/test_ingresos.py |
| Tests de auditoria | tests/test_auditor.py |
| Documento de negocio | docs/Pagina_1_14D1.md |
| Bitacora del proyecto | docs/ESTADO_PROYECTO.md |
