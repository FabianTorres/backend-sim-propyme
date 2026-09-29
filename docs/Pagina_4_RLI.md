# Determinación del resultado de la RLI 14D1

Antes de llegar a esta pantalla, si **9.1 > 0**, se le recuerda al contribuyente que puede acogerse a la deducción del **Art. 14 E (incentivo al ahorro)**.

Se debe desplegar el mensaje si **9.1 > 0** y se cumple la siguiente condición:

### Condición = 1 cuando:

```text
POS {
Vx010357 + Vx010145 + Vx010059 - Vx010146 - Vx010358 - Vx010088
+ Vx011930 - Vx011931
+ Vx012832 - Vx012833
+ Vx012946 + Vx012947 + Vx012948 + Vx012949
+ Vx012836 - Vx012837
+ Vx013663 + Vx013664 + Vx013665 + Vx013666
+ Vx013719 + Vx013720 + Vx013721 + Vx013722
+ Vx010118 - Vx010089
+ Vx012830 - Vx012831
}
≤ MAX(Vx010213; C1400 + C1401 + C1587 + C1588 + C1817) * P22
```

En caso contrario, la condición será **0**.

Si **9.1 > 0** y la condición es **0**, no se calculan **9.3** ni **9.4** y se debe dirigir al **Cuadro N°3**.

Si **9.1 > 0** y el contribuyente se acoge a la deducción del **Art. 14 E**, se despliega el **Cuadro N°1 y 1.1 (Detalle)**.

En caso contrario, no se despliega dicho cuadro y no se calculan los códigos **9.3** ni **9.4**.

La columna **Código** es sólo para uso interno.

## Mensaje emergente

> Puede optar por hacer uso del beneficio de incentivo al ahorro (deducción Art. 14 E), el cual consiste en una rebaja a la RLI, equivalente al 50% de la Renta Líquida Imponible (RLI) invertida en la empresa, con tope de UF 5.000. ¿Desea acogerse al incentivo al ahorro (deducción Art. 14 E)?

**Respuestas posibles:**

- SI
- NO

Si **9.1 = 0** o **9.2 > 0**, no se muestra el mensaje y no se calculan **9.3** ni **9.4**.

Si **9.2 > 0**, desplegar únicamente el **Cuadro N°2_RLI_neg**.

Si **9.1 ≥ 0** y el contribuyente no se acoge al incentivo Art. 14E, desplegar únicamente el **Cuadro N°3_RLI_pos** (sin 14E).

Las líneas **9.1** y **9.2** se despliegan solamente cuando su valor sea mayor que cero. Debe mostrarse una u otra, pero nunca ambas.

La línea **9.5** sólo se despliega si el valor propuesto es mayor que cero.

## Cuadro N°1 y 1.1_14E

| Código | Concepto | Código F22 | +/- | Monto |
|----------|----------|----------|----------|----------|
| 9.1 | Renta Líquida Imponible del ejercicio (antes de la rebaja del incentivo al ahorro) |  | (+) | Si (7-8+8.26) ≥ 0 entonces (7-8+8.26), sino 0 |
| 9.4 | Deducción 14 E Incentivo al Ahorro del ejercicio (50% de la RLI invertida en la empresa con tope). Click para ver detalle. | 1432 | | Min(P02 * POS(9.1 - RET30 - 8.26); P103) |
| 9.5 | Base del IDPC voluntario según art. 14 letra A N°6 LIR | 1433 | (-) | Min(Vx013013;(9.1-9.4)) |
| 9.6 | BASE IMPONIBLE DEL IMPUESTO DE PRIMERA CATEGORÍA (O PÉRDIDA TRIBUTARIA) DEL EJERCICIO | 1440 | = | Si (9.1-9.4-9.5) > 0: (9.1-9.4-9.5), sino -9.2 |

## Detalle Cuadro 1.1 (Cálculo Código 1432)

| Código | Concepto | Código F22 | +/- | Monto |
|----------|----------|----------|----------|----------|
| 9.1 | Renta Líquida Imponible del ejercicio (antes de la rebaja del incentivo al ahorro) | | (+) | Si (7-8+8.26) ≥ 0 entonces (7-8+8.26), sino 0 |
| 9 | Partidas del art. 21 inc. 1° no afectadas con IU 40% y del inc. 2° LIR pagadas | 1431 | (-) | Código 8.26 |
| 9.21 | Retiros | | (-) | RET30 |
| 9.3 | Renta Líquida Imponible del ejercicio invertida en la empresa | | (=) | (9.1 - RET30 - 8.26), si es positivo |

| Concepto | Monto |
|----------|----------|
| Monto disponible para deducción Art. 14E (50% de la RLI invertida con tope de 5.000 UF) | Min(P02 * (9.3); P103) |

## Cuadro N°2_RLI_neg

| Código | Concepto | Código F22 | +/- | Monto |
|----------|----------|----------|----------|----------|
| 9.2 | Pérdida Tributaria del Ejercicio | | (-) | Si (7-8+9) < 0: ABS(7-8+9), sino 0 |
| 9.7 | BASE IMPONIBLE DEL IMPUESTO DE PRIMERA CATEGORÍA (O PÉRDIDA TRIBUTARIA) DEL EJERCICIO | 1440 | = | Si (9.1-9.4-9.5) > 0: (9.1-9.4-9.5), sino -9.2 |

## Cuadro N°3_RLI_pos (sin 14E)

| Código | Concepto | Código F22 | +/- | Monto |
|----------|----------|----------|----------|----------|
| 9.1 | Renta Líquida Imponible del ejercicio | | (+) | Si (7-8+8.26) ≥ 0 entonces (7-8+8.26), sino 0 |
| 9.5 | Base del IDPC voluntario según art. 14 letra A N°6 LIR | 1433 | (-) | Min(Vx013013;(9.1-9.4)) |
| 9.6 | BASE IMPONIBLE DEL IMPUESTO DE PRIMERA CATEGORÍA (O PÉRDIDA TRIBUTARIA) DEL EJERCICIO | 1440 | = | Si (9.1-9.4-9.5) > 0 entonces (9.1-9.4-9.5), sino -9.2 |

## Cálculos para códigos F22 14D1

| Código F22 | Algoritmo |
|------------|------------|
| 1400Calc | 7.12 |
| 1401Calc | 7.19 |
| 1402Calc | 7.17 + 7.18 |
| 1403Calc | 7.14 |
| 1587Calc | 7.13 + 7.16 |
| 1588Calc | 7.15 + 7.20 |
| 1404Calc | 7.25 + 7.26 |
| 1405Calc | 7.27 |
| 1410Calc | 7 |
| 1406Calc | 8.1 |
| 1407Calc | 8.2 |
| 1408Calc | 8.3 |
| 1409Calc | 8.4 + 8.6 - 8.7 + 8.8 + 8.9 + 8.11 |
| 1429Calc | 8.13 |
| 1411Calc | 8.14 |
| 1412Calc | 8.15 |
| 1413Calc | 8.5 + 8.10 |
| 1415Calc | 8.17 |
| 1416Calc | 8.18 |
| 1417Calc | 8.19 |
| 1418Calc | 8.20 |
| 1419Calc | 8.22 |
| 1421Calc | 8.25 |
| 1422Calc | 8.26 |
| 1423Calc | 8.27 |
| 1424Calc | 8.21 + 8.24 |
| 1425Calc | 8.23 |
| 1426Calc | 8.12 |
| 1427Calc | 8.28 |
| 1428Calc | 8.29 |
| 1430Calc | 8 |
| 1431Calc | 8.26 |
| 1432Calc | 9.4 |
| 1433Calc | 9.5 |
| 1440Calc | 9.6 |
| 1818Calc | 8.31 |
| 1817Calc | 7.10 |

## Precisiones verificadas en la aplicación original

> Lo siguiente complementa (no reemplaza) las tablas de arriba. Surge de la
> revision detallada de la aplicacion original. Ante cualquier diferencia entre
> el documento oficial, la aplicacion original y este backend, se analiza caso
> por caso (ver AGENTS.md 5b): el documento oficial es la base y la aplicacion
> original tambien puede estar mala.

1. **9.4 es editable con cota.** El valor de la formula
   `Min(P02 * POS(9.1 - RET30 - 8.26); P103)` es el *propuesto inicial*
   (maximo). El contribuyente puede modificarlo y la aplicacion lo recorta al
   intervalo `[0, maximo]`. Si responde NO al incentivo, 9.4 queda en 0.
2. **Gatillo del modal 14E.** La pregunta "¿Desea acogerse...?" se muestra
   solo si `9.1 > 0`, `9.2 == 0` y se cumple la Condicion (punto 7). Si la
   condicion falla, se va directo al Cuadro N°3 sin preguntar.
3. **Seleccion de cuadros.** `9.2 > 0` → Cuadro N°2. Cuadro N°1 solo si
   responde SI. Todo lo demas (incluido `9.1 == 0` y `9.2 == 0`) → Cuadro N°3.
4. **9.3 crudo vs "si es positivo" (discrepancia documentada).** El doc dice
   `(9.1 - RET30 - 8.26), si es positivo`; la aplicacion original exhibe el
   valor crudo (puede resultar negativo) y aplica el `POS` solo donde lo
   consume (calculo de 9.4). Se adopta lo original para el despliegue (no
   altera ningun calculo, ya que el consumo usa `POS(9.3)` en ambos casos) y
   se deja constancia aqui.
5. **Reglas de despliegue.** La fila 9.1 se muestra solo si `> 0`, la 9.2 solo
   si `> 0` (nunca ambas) y la 9.5 solo si `> 0`.
6. **Los 9.x se calculan en el backend.** La aplicacion original reparte este
   calculo entre cliente y servidor; en este simulador TODO el calculo vive en
   el backend (el frontend solo envia `acoge_14e` y el eventual `deduccion_14e`
   digitado, y recibe los resultados).
7. **C1404 (anos 2026+).** `1404Calc = 7.25 + 7.26`. Solo se soporta el ano
   tributario en curso y siguientes; no se replican ramificaciones de anos
   anteriores.
8. **Persistencia.** La aplicacion original guarda por contribuyente y periodo:
   partidas art.21 (= 8.26), totales 7 y 8, subtotal depurado, deduccion 14E
   (9.4), base IDPC (9.5) y base imponible (9.6/9.7). La Base Imponible
   (Pagina 5) consume 9.4/9.5/9.6 desde aqui.
9. **Codigo 9.** La variable `9` (Detalle 1.1, F22 1431) vale lo mismo que el
   codigo 8.26, pero se modela con nombre propio por trazabilidad.