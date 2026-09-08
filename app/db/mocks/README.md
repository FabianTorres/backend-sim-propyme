# Mocks del Simulador Propyme

## Estructura del JSON Global

Cada mock sigue el contrato `SimuladorGlobalRequest` definido en
`app/schemas/orquestador.py`. La estructura esperada es:

```json
{
  "at": "2025",
  "patrimonio_personal": false,
  "vectores": { "Vx...": 0 },
  "externos": { "Calc...": 0 },
  "digitados": {
    "ingresos": { "...": 0 },
    "egresos": { "...": 0 }
  }
}
```

## Reglas del payload (importante para el Frontend)

- `vectores` y `externos` son GLOBALES y PLANOS: un solo diccionario con todos
  los vectores (Vx...) y variables externas (Calc..., atributos) del caso. El
  Frontend nunca repite vectores ni calcs entre paginas.
- El backend mapea estrictamente solo los codigos que usa (`extra="ignore"`),
  por lo que el Frontend puede enviar vectores/calcs adicionales sin romper la
  validacion.
- `digitados` va agrupado por pagina: cada sub-nodo (`ingresos`, `egresos`, ...)
  contiene solo los campos que esa pagina digita.

## Como agregar una nueva pagina (ej. Egresos)

1. Crear `app/schemas/egresos.py` con `CamposDigitadosEgresos` y `EgresosResponse`.
2. Agregar los vectores que Egresos consume a `app/schemas/globales.py` (Vectores).
3. Agregar `egresos: CamposDigitadosEgresos | None` en `DigitadosGlobal`.
4. Agregar `egresos: EgresosResponse | None` en `SimuladorGlobalResponse`.
5. Crear `app/services/egresos.py` con `EgresosService` y llamarlo desde el Orquestador.

Los tests en `tests/conftest.py` cargan automaticamente este mock via el
fixture `mock_payload` (session scope).