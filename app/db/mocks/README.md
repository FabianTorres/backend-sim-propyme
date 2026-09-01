# Mocks del Simulador Propyme

## Estructura del JSON Global

Cada mock sigue el contrato `SimuladorGlobalRequest` definido en
`app/schemas/orquestador.py`. La estructura esperada es:

```json
{
  "at": "2025",
  "patrimonio_personal": false,
  "vectores": { ... },
  "externos": { ... },
  "digitados": {
    "ingresos": { ... },
    "egresos": { ... }
  }
}
```

## Como agregar una nueva pagina (ej. Egresos)

1. Crear `mock_egresos.json` o simplemente agregar `"egresos": {...}` dentro
   de `digitados` en `mock_simulador_global.json`.
2. Agregar los vectores necesarios en `VectoresEgresos` e incluirlos en el
   `VectoresGlobales` del `SimuladorGlobalRequest`.
3. Agregar `egresos: CamposDigitadosEgresos | None` en `DigitadosGlobal`.
4. Agregar `egresos: EgresosResponse | None` en `SimuladorGlobalResponse`.

Los tests en `tests/conftest.py` cargan automaticamente este mock via el
fixture `mock_payload` (session scope).