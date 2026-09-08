# Guia de Integracion — Frontend <-> Backend Simulador Propyme

> Destinatario: el agente que mantiene el frontend (proyecto de UI).
> Endpoint unico: `POST /api/v1/simulador/calcular`
> Health check: `GET /health`

## 1. Reglas de oro (leer primero)

1. **El backend es un oraculo sin memoria (stateless).** En cada request el
   frontend envia SIEMPRE la historia completa: el bloque `vectores` y
   `externos` completos, mas los `digitados` del usuario. Si omites un vector,
   el backend lo inicializa en `0` y la matematica dara ceros.
2. **`vectores` y `externos` son globales y planos.** Un solo diccionario con
   todos los `Vx...` y `Calc...` del caso. No se repiten por pagina; el backend
   los comparte entre todas las paginas.
3. **`digitados` se agrupa por pagina.** Cada sub-nodo (`ingresos`, luego
   `egresos`, `retiros`, ...) contiene solo lo que esa pagina digita.
4. **Los montos viajan como STRING.** El backend serializa `Decimal` como
   string JSON (ej. `"4080000"`), no como numero. Usa aritmetica decimal (no
   `float`) para no perder precision en valores monetarios.
5. **El frontend NO calcula nada.** Solo envia entradas y recibe resultados.
   Todo calculo (y su trazabilidad) lo hace el backend.

## 2. Request (`SimuladorGlobalRequest`)

```json
{
  "at": "2025",
  "mostrar_formulas": false,
  "patrimonio_personal": false,
  "vectores": {
    "Vx010042": 1,
    "Vx012188": 1000000,
    "Vx013384": 100000
  },
  "externos": {
    "Calc4064": 0,
    "Calc4075": 0,
    "CRRP": false
  },
  "digitados": {
    "ingresos": {
      "monto_no_percibido": { "7.1": 0, "7.2": 100000 },
      "no_considerar_patrimonio": { "7.14": 0 },
      "factura_renta_presunta": { "7.1": 0 },
      "ingresos_ano": { "7.11": 150000 },
      "ingresos_adeudados_at_anterior": { "7.1": 50000 }
    }
  }
}
```

| Campo | Tipo | Notas |
|---|---|---|
| `at` | string | Anio tributario (default `"2025"`). |
| `mostrar_formulas` | bool | `true` = Modo Auditoria (desglose de formulas). |
| `patrimonio_personal` | bool \| null | Flag global CDEI. Se detona en Ingresos, impacta en RLI/Retiros. |
| `vectores` | objeto plano | `Vx...` -> numero. Solo envia los que apliquen al caso. |
| `externos` | objeto plano | `Calc...` y atributos (hoy `Calc4064`, `Calc4075`, `CRRP`). |
| `digitados.<pagina>` | objeto | Campos editados por el usuario, agrupados por pagina. |

- En `vectores`/`externos` puedes enviar codigos adicionales: el backend los
  ignora (`extra="ignore"`) hasta que los necesite. Es forward-compatible.
- Hoy solo existe `digitados.ingresos`. Las proximas paginas agregaran
  `digitados.egresos`, `digitados.retiros`, etc.

## 3. Response (`SimuladorGlobalResponse`)

```json
{
  "ingresos": {
    "filas": [
      {
        "codigo": "7.1",
        "concepto": "Exportaciones (Cod. 20 F29)",
        "codigo_f22": 1400,
        "ingresos_ano": "1000000",
        "ingresos_adeudados_at_anterior": "50000",
        "monto_no_percibido": "0",
        "no_considerar_patrimonio": "0",
        "factura_renta_presunta": "0",
        "monto_ingreso_percibido": "1000000",
        "inspectores": null
      }
    ],
    "totales": {
      "fila_7_12": "4080000",
      "fila_7_total": "4920000"
    },
    "avisos": {
      "aviso_montos_propuestos_7_10": false,
      "aviso_arriendos_bienes_raices": false,
      "mostrar_columna_patrimonio": true,
      "mostrar_columna_renta_presunta": false,
      "valor1_pcalc": "0",
      "valor2_pcalc": "0"
    }
  }
}
```

- La respuesta es un solo JSON con un sub-nodo por modulo. Hoy solo `ingresos`
  esta poblado; las demas paginas llegaran como `null` hasta implementarse.
- Cada fila de `filas` trae las columnas calculadas:
  - `ingresos_ano` (Col. B), `ingresos_adeudados_at_anterior` (Col. H),
    `monto_no_percibido` (Col. C), `no_considerar_patrimonio` (Col. D),
    `factura_renta_presunta` (Col. E), `monto_ingreso_percibido` (Col. F).
  - Los campos que no aplican a una fila vienen en `null`.
- `avisos` trae flags de visibilidad y mensajes para renderizar la UI
  (ej. `mostrar_columna_patrimonio`, `valor1_pcalc`, `valor2_pcalc`).

## 4. Modo Auditoria (`mostrar_formulas: true`)

Cuando actives el flag, cada fila incluye `inspectores`: un objeto con una
entrada por columna calculada y el paso a paso de la formula:

```json
"inspectores": {
  "ingresos_ano": {
    "valor": "1000000",
    "literal": "MAX(Vx012188, (Vx013384 + Vx013394 + Vx013395 + Vx013396))",
    "evaluado": "MAX(1000000, (100000 + 0 + 0 + 0))",
    "variables_usadas": [
      { "nombre": "Vx012188", "valor": "1000000", "origen": "vector" }
    ],
    "pasos": ["100000 + 0 = 100000", "MAX(1000000, 100000) = 1000000"]
  }
}
```

- Los nombres de variables calculadas usan la convencion
  `<Modulo> <fila><columna>` (ej. `Ingresos 7.1B`).
- Si `mostrar_formulas` es `false`, `inspectores` es `null` (menor payload).

## 5. Codigos de respuesta

- `200` -> calculo exitoso.
- `422` -> payload invalido (Pydantic rechazo el request). Revisa tipos
  (ej. `vectores` debe ser objeto plano, no array).
