# Algoritmos de cálculo 14D1

## Introducción

El asistente cuenta con 5 pantallas, una para Ingresos, Egresos, Retiros, Determinación de la RLI y Recuadro 17 del F22.

## Ingresos 14D1

El asistente cuenta con 5 pantallas, una para Ingresos (Esta es la Pagina 1), Egresos, Retiros, Determinación de la RLI y  Recuadro 17 del F22.

Al ingresar a la página “Ingresos” si Vx010042=1, el contribuyente ve el siguiente mensaje:

"Dividendos, retiros y creditos recibidos

Dado que es Empresario Invididual, estos dividendos, retiros y creditos reibidos podrian pertenecer a la contabilidad de su empresa o a su patrimonio personal:

-DIVIDENDOS Y RETIROS = VALOR1_PCalc
-CREDITOS = VALOR2_PCalc

¿Corresponde a tu patrimonio personal (o sea, estan fuera de la contabilidad de la empresa?)
Respuesta SI o NO
"

Con:

VALOR1_PCalc = Vx013601+ Vx013602+ Vx013603+ Vx013604+ Vx013506+ Vx013507+ Vx013508+ Vx013509+ Vx013510+ Vx013511+ Vx013512+ Vx013513+ Vx013560+ Vx013561+ Vx013562+ Vx013563+ Vx013564+ Vx013565+ Vx013566+ Vx013567+ Vx013568+ Vx013569+ Vx013570+ Vx013571+ Vx013605+ Vx013606+ Vx013607+. Vx013608+ Vx013588+ Vx013589+ Vx013590+ Vx013591+ Vx013592+ Vx013609+ Vx013610+ Vx013611+ Vx013612+ Vx013613+ Vx013614+ Vx013615+ Vx013616+ Vx012420+ Vx012424+Vx013750

VALOR2_PCalc = Vx013514+ Vx013515+ Vx013516+ Vx013517+ Vx013518+ Vx013519+ Vx013520+ Vx013521+ Vx013523+ Vx013524+ Vx013525+ Vx013526+ Vx013528+ Vx013572+ Vx013573+ Vx013574+ Vx013575+ Vx013576+ Vx013577+ Vx013578+ Vx013579+ Vx013581+ Vx013582+ Vx013583+ Vx013584+ Vx013586+ Vx013617+ Vx013618+ Vx013593+ Vx013594+ Vx013619+ Vx013620+ Vx013595+ Vx013596+ Vx013621+ Vx013622+ Vx013623+ Vx013597+ Vx013598+ Vx013625+ Vx012421 + Vx012425+ Vx012426

Se genera la variable CDEICalc=1 si el contribuyente elige la opción “SI” de dicho mensaje y 0 si escoge la opción “NO”. Si el contribuyente vuelve a la página anterior y continua nuevamente a la página de ingresos se vuelve a desplegar el mensaje.

El símbolo "?" abre en una pestaña la url: https://www4.sii.cl/djconsultarentaui/internet/#/agenteretenedor/

REGLAS PARA LA TABLA

Las columnas “No considerar es de Patrimonio Personal” se despliega solo cuando el contribuyente tiene el vector Vx010042=1, mientras que la columna “Facturas de Actividad de Renta Presunta” se despliega cuando el contribuyente tiene el Atributo CRRP.

Si la celda de la columna B tiene valor 0 o vacío (y el contribuyente no puede complementar dicho valor) en las celdas de la columna C, D y E correspondientes a esa fila no se pueden ingresar datos.

Si no existen valores propuestos se debe desplegar la totalidad de las filas. En caso de existir valores propuestos se debe desplegar una pantalla customizada con las filas con valores distintos a cero (además de las filas de totalizadores 7.12 y 7). En la pantalla customizada siempre debe aparecer la opción desplegar la totalidad de las filas

La primera fila (código columna) no se despliega para el contribuyente (sirve para referirse a las celdas, por ejemplo: 7.1A corresponde a “Exportaciones (Cód. 20 F29)” y 7.1B “MAX(Vx012188; Vx013384+ Vx013394+ Vx013395+ Vx013396)”.

Si el contribuyente tiene monto propuesto, en columna B, Fila 7.10, es decir si ( Vx014255 + Vx014256  Vx014257 + Vx014258 + Vx014259 + Vx014260 +  Vx014261 + Vx014263) >0  indicar  mensaje en tooltip de la celda:  “El valor propuesto corresponde a la sumatoria de los ingresos del giro  registrados el año anterior como no percibidos (partidas detalladas anteriormente columna Ingresos percibidos de montos adeudados AT anterior)”.

Si calc4064 (proveniente del asistente de BR) es > 0 .o. no existe Calc4064 .y. (Vx012209) > 0, entonces desplegar la siguiente mensaje : “Si el ingreso proveniente del arrendamiento de bienes raíces se encuentra facturado e incluido en ítems anteriores de ingresos, correspondería rebajarlas en “Ingresos percibidos provenientes de arriendos de bienes raíces” para no duplicar dicho ingreso”.

## Tabla Pagina 1 (Ingresos)

| Código Columna |  | A | H | B | C | D | E | F | G |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Código de Partidas |  | Ventas y Servicios Afectos a IVA | Ingresos percibidos de montos adeudados de AT anterior | Ingresos del año (Neto) | Monto No Percibido del año (Neto) | No considerar es de Patrimonio Personal | Facturas de Actividad de Renta Presunta | Monto Ingreso Percibido | Código F22 |
| 7.1 | (+) | Exportaciones (Cód. 20 F29) (…) | Vx014255 (editable, mostrar sólo en casos de que tengan montos AT-1) | MAX(Vx012188; Vx013384+ Vx013394+ Vx013395+ Vx013396) | El contribuyente ingresa información |  | El contribuyente ingresa información | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.2 | (+) | Facturas por ventas y servicios gravados (Cód. 502, 717 y 501 F29) (…) | Vx014256 (editable, mostrar sólo en casos de que tengan montos AT-1) | MAX(Vx012194-Vx013257; Pos(Vx013372- Vx Vx013381) + Vx013387+ Vx013382+ Vx013383) | El contribuyente ingresa información |  | El contribuyente ingresa información | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.3 | (+) | Ventas y/o Servicios prestados Exentos, o No Gravados (Cód. 142 y 715 F29) (…) | Vx014257 (editable, mostrar sólo en casos de que tengan montos AT-1) | MAX(Vx012189; Vx013365+ Vx013366+ Vx013367+ Vx013368 + Vx013369+ Vx013370+ Vx013371+ Vx013385) | El contribuyente ingresa información |  | El contribuyente ingresa información | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.4 | (+) | Ventas con retención sobre el margen de comercialización (Contrib. Retenidos) (Cód. 732 F29) (…) | Vx014258 (editable, mostrar sólo en casos de que tengan montos AT-1) | Vx012191 | El contribuyente ingresa información |  | El contribuyente ingresa información | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.5 | (+) | Fact. Compra recibidas Retención total (Cont. retenidos) y fact. de inicio emitida (Cód. 587 F29) (…) | Vx014259 (editable, mostrar sólo en casos de que tengan montos AT-1) | MAX(Vx012192; Vx013379+ Vx013380) | El contribuyente ingresa información |  | El contribuyente ingresa información | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.6 | (+) | Fact. de Compra recibidas con retención parcial (Cód. 720 F29) (…) | Vx014260 (editable, mostrar sólo en casos de que tengan montos AT-1) | MAX(Vx012193; Vx013378) | El contribuyente ingresa información |  | El contribuyente ingresa información | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.7 | (+) | Boletas y Comprobante o recibo de pago de transacciones transbank (Cód. 111 y 759 F29) (…) | Vx014261 (editable, mostrar sólo en casos de que tengan montos AT-1) | MAX(Vx012195; Vx013373+ Vx013374+ Vx013375+ Vx013376) | El contribuyente ingresa información |  | El contribuyente ingresa información | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.8 | (-) | Notas de Crédito emitidas por ventas y servicios (Cód. 510, 709 y 734 F29) (…) | (Bloquear este campo) | Vx012197 | (Bloquear este campo) |  | El contribuyente ingresa información | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.9 | (+) | Notas de débito emitidas (Cód. 513 F29) (…) | Vx014263 (editable, mostrar sólo en casos de que tengan montos AT-1) | MAX(Vx013257;Vx013377) | El contribuyente ingresa información |  | El contribuyente ingresa información | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.10 | (+) | Ingresos devengados del giro ejercicios anteriores y percibidos en el ejercicio | (Bloquear este campo) | 7.1H + 7.2H + 7.3H + 7.4H + 7.5H +7.6H + 7.7H +7.9 H (no editable) |  |  |  | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1817 |
| 7.11 | (+) | Ingresos pagados según contratos no facturados | (Bloquear este campo) | Contribuyente ingresa la información |  |  |  | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1400 |
| 7.12 | = | Total Ingresos por ventas y servicios |  | = POS(7.1+7.2+7.3+7.4+7.5+7.6+7.7-7.8+7.9+7.11) | = POS(7.1+7.2+7.3+7.4+7.5+7.6+7.7-7.8+7.9+7.11) | = POS(7.1+7.2+7.3+7.4+7.5+7.6+7.7-7.8+7.9+7.11) | = POS(7.1+7.2+7.3+7.4+7.5+7.6+7.7-7.8+7.9+7.11) | = POS(7.1+7.2+7.3+7.4+7.5+7.6+7.7-7.8+7.9+7.11) | 1400 |
| 7.13 | (+) | Ingresos pagados según contratos con Empresas Relacionadas | (Bloquear este campo) | El contribuyente debe ingresar la información |  |  |  | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1587 |
| 7.14 | (+) | Mayor valor por rescate o enajenación de inversiones o bienes no depreciables (ver información para declarar) | Vx014264 (editable, mostrar sólo en casos de que tengan montos AT-1) | Vx010118+ Vx012830 + Vx010240+ Vx013639 (Campo editable) | El contribuyente ingresa información | El contribuyente ingresa información | El contribuyente ingresa información | POS(Ingresos + Ingresos percibidos de monto adeudado AT anterior – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1403 |
| 7.15 | (+) | Ingresos percibidos provenientes de arriendos de bienes raíces (ver información para declarar) | Vx014265 (editable, mostrar sólo en casos de que tengan montos AT-1) | Si Calc4064 > 0, entonces Calc4064 .o. Si Calc4075=1 .y. (Calc4064=0 .o. ECal4064 == ´N´), entonces cero, Sino (si no se cumplen las 2 condiciones anteriores) entonces Vx012209 | El contribuyente ingresa información | El contribuyente ingresa información | El contribuyente ingresa información | POS(Ingresos + Ingresos percibidos de monto adeudado AT anterior – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1588 |
| 7.16 | (+) | Ingresos percibidos o devengados por operaciones con empresas relacionadas del art. 14 letra A) LIR (depurados de notas de débito y crédito) | (Bloquear este campo) | El contribuyente ingresa información |  |  |  | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1587 |
| 7.17 | (+) | Intereses Directos (ver información para declarar) | Vx014266 (editable, mostrar sólo en casos de que tengan montos AT-1) | POS(Vx010145 - Vx012210) + POS(Vx010357+ Vx010974 - Vx010358) + POS(Vx010059 – (Vx010088 + Vx010985)) | El contribuyente ingresa información | El contribuyente ingresa información | El contribuyente ingresa información | POS(Ingresos + Ingresos percibidos de monto adeudado AT anterior – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1402 |
| 7.18 | (+) | Intereses Indirectos (ver información para declarar) | Vx014267 (editable, mostrar sólo en casos de que tengan montos AT-1) | POS(Vx010238- Vx010239) + POS(Vx010236 - Vx010237) + POS( Vx010934 – Vx011015) | El contribuyente ingresa información | El contribuyente ingresa información | El contribuyente ingresa información | POS(Ingresos + Ingresos percibidos de monto adeudado AT anterior – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1402 |
| 7.19 | (+) | Renta de fuente extranjera percibidas (ver información para declarar) | (Bloquear este campo) | Vx013633+ Vx013634+ Vx013635+ Vx013636+ Vx013637+ Vx013638 (Campo editable) |  |  |  | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1401 |
| 7.20 | (+) | Otros ingresos percibidos o devengados (ver información para declarar) | Vx014262 (editable, mostrar sólo en casos de que tengan montos AT-1) | Vx013640+ Vx013641+ Vx013642+ Vx013643+ Vx013644+ Vx013645 (Campo editable) | El contribuyente ingresa información |  |  | POS(Ingresos + Ingresos percibidos de monto adeudado AT anterior – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1588 |
| 7.25 | (+) | Ingreso diferido pendiente de tributación de acuerdo al art. 14 letra D) N°8, letra d) de la LIR |  |  |  |  |  |  |  |
| 7.26 | (+) | Incremento Ingreso diferido pendiente de tributación de acuerdo al art. 14 letra D) N°8, letra d) de la LIR |  |  |  |  |  |  |  |
| 7.27 | (+) | Crédito sobre Activos Fijos Adquiridos en el ejercicio | (Bloquear este campo) | Informa el contribuyente |  |  |  | POS(Ingresos – Monto no Percibido – No Considerar: es de Patrimonio Personal – Facturas de Actividad de Renta Presunta) | 1405 |
| 7 | TOTAL INGRESOS |  |  |  |  | =7.12 + 7.13 + 7.14 + 7.15 + 7.16 + 7.17 + 7.18 + 7.19 + 7.20 + 7.25 + 7.26 + 7.27+7.10 | 1410 |  |  |
