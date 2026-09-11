# <u>Retiros Régimen 14D1 (Propyme)</u>

## Formato recuadro retiros

Los retiros se ingresan en una pantalla previa a la determinación del resultado del ejercicio, teniendo el siguiente formato:

> *(Nota de desarrollador de simulador: Agreguemos también una columna nombrando a la fila, para seguir la misma lógica de las demás páginas. Por ejemplo 1A, 3D, etc)*

### Tabla 1 — Recuadro Retiros

| A | B | C | D | E | F | G | H | I | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Rut socio** | **Usufructuario**[^1] | **Cantidad de Acciones** | **Retiros efectivos del ejercicio** | **Retiros efectivos del ejercicio** | **Retiros efectivos del ejercicio** | **Retiros efectivos del ejercicio** | **Saldo monto de retiro en exceso AT-1** | **Devolución de capital** | **Devolución de capital** | **Devolución de capital** | **Devolución de capital** |
| | | | **Fecha Retiro** | **Monto retiro** | **Monto ISFUT_H** | **Monto ISFUT_A** | | **Fecha** | **Monto** | **Monto ISFUT_H** | **Monto ISFUT_A** |
| Rut_Socio<sub>RIAC</sub> o Rut digitado (**agrega registro**) | Si **agrega registro**: digita 1 o 2 / Si **duplica registro**: vacío | Digita información | Digita información | Digita información | Digita información | Digita información | Digita información | Digita información | Digita información | Digita información | Digita información |
| RET1 | RET2 | RET3 | RET4 | RET5 | RET6 | RET7 | RET8 | RET9 | RET10 | RET11 | RET12 |
| *Variables que se generan a partir de las columnas* | | | | 1040 y RET30 | 1041 | 1042 | 1043 | | 1049 | 1051 | 1052 |

[^1]: Debe tener un tooltip indicando: Ingrese 1 si el Rut corresponde a usufructuario y 2 si corresponde a Nudo propietario.

En esta pantalla existen 2 botones: opción de **duplicar el registro** (duplicar el rut seleccionado manteniendo los valores de RET1) y **agregar registro** (agrega una línea de registro, siendo obligatorio digitar RET1, con RET2= 1 o 2). Hay que considerar que el registro agregado deberá poder duplicarse al igual que los registros provenientes del RIAC.

### Se considera

```
[1044]: POS(Vx014301 + Vx013509 + Vx013567 + Vx013591 + H2 + H3 + H6 + H7)

[1045]: POS(<mark>Vx014661 - Vx014662 - Vx014663</mark>) + Vx013510 + Vx013568 + Vx012951 + I17 + I4
```

**<u>NOTA:</u>** Los variables H2, H3, H6, H7, I4 e I17 vienen del Registro de Rentas Empresariales (variables temporales) por lo tanto no se utilizarán para calcular [1044] y [1045] a menos que el usuario haya llegado hasta el Registro de Rentas Empresariales y se haya devuelto hasta el recuadro de Retiros Propyme (que deberá tener un valor actualizado de [1044] y [1045]). Asimismo, las variables que vienen de dicho Registro que son negativas (-), vienen con valor negativo como por ejemplo H7 y I4.

## Validaciones

- Los campos [RET6] y [RET11] estarán habilitados solo en los casos en que la sociedad declarante cumple con [1044]>0.
- Los campos [RET7] y [RET12] estarán habilitados solo en los casos en que la sociedad declarante cumple con [1045]>0.
- El campo [RET8] solo podrá ingresar montos en aquellos [RET1] vigentes al 31.12.AT-1.
- En el campo [RET2] el contribuyente puede digitar "1" o "2" (únicos valores posibles) **solo en el caso en que agregue registro.**
- Validación para realizar socio por socio y por cada fecha indicada:
  - Para cada [RET4] > 0; [RET5]<sub>fecha_n_socio_n</sub> ≥ [RET6]<sub>fecha_n_socio_n</sub> + [RET7]<sub>fecha_n_socio_n</sub>
  - Para cada [RET9] > 0; [RET10]<sub>fecha_n_socio_n</sub> ≥ [RET11]<sub>fecha_n_socio_n</sub> + [RET12]<sub>fecha_n_socio_n</sub>
- Validación para realizar a los montos totales:
  - [1044] <mark>≥</mark> ∑ ([RET6] + [RET11])
  - [1045] <mark>≥</mark> ∑ ([RET7] + [RET12])

> *Nota: lo que tiene que pasar (lo correcto) es que las variables 1044 y/o 1045 sean mayor o igual a lo que ingresa el contribuyente en ([RET6] + [RET11]) o ([RET7] + [RET12]), respectivamente.*

## Detalle de los campos

- **RET1 = RUT SOCIO:**
  - Campo propuesto (RIAC) o ingresado por el contribuyente (**agregar registro**).
  - Al ingresar al aplicativo, deberá desplegarse los RUT de los socios que permanecieron en la empresa o sociedad entre el 01.01.AT-1 y el 31.12.AT-1, provenientes de RIAC.
  - Los RUT incluidos con la opción **agregar registro** por el declarante deberán validar que el campo Usufructuario (RET2="X") contenga alguno de los valores indicados para éste.
  - **En caso de que el servicio RIAC no entregue socios (la respuesta distinta a error), se despliega el rut del contribuyente (declarante) como uno de los rut de los socios, accionistas o propietarios (siendo el único Rut desplegado).**
  - Un RUT puede estar n veces (**duplicar el registro**).

- **RET2 = USUFRUCTUARIO:**
  - Este campo corresponde a una marca, que indica que el RUT informado es un usufructuario o nudo propietario de los dividendos.
  - Por lo cual, los valores posibles son: 1 .o. 2.
  - Campo habilitado tanto para los RUT agregados como para los provenientes del RIAC.

- **RET3 = CANTIDAD ACCIONES:**
  - Valor ingresado por el contribuyente.
  - Campo obligatorio para RUT con Vx010599 = 213, 214, 216, 222, 223 o 227.
  - Para otros valores de Vx010599, el campo debe estar bloqueado.
  - En el caso de los RUT obtenidos desde el RIAC, el campo sólo deberá estar disponible para ingreso de valor para aquellos RUT que se encuentran vigentes al 31.12.AT-1. Para los otros RUT la celda deberá estar bloqueada.

- **RET4 = FECHA RETIRO:**
  - Valor ingresado por el contribuyente.
  - Formato de la celda deberá ser dd/mm/AT-1.
  - Debe corresponder a fechas entre el 01.01.AT-1 y 31.12.AT-1.
  - Si ingresa RET5=[MONTO RETIRO] deberá informar la fecha en que se realizó.
  - Para un mismo RUT no podrá ingresar dos veces la misma fecha.
  - Si declarante duplica registro, este campo debe estar habilitado para ingresar una nueva fecha.

- **RET5 = MONTO RETIRO:**
  - Valor ingresado por el contribuyente.
  - Si el declarante **duplica registro** o **agrega registro**, este campo debe estar habilitado para ingresar monto.

- **RET6 = MONTO ISFUT_H:**
  - Valor ingresado por el contribuyente.
  - Si el declarante **duplica registro** o **agrega registro**, este campo debe estar habilitado para ingresar monto.

- **RET7 = MONTO ISFUT_A:**
  - Valor ingresado por el contribuyente.
  - Si el declarante **duplica registro** o **agrega registro**, este campo debe estar habilitado para ingresar monto.

- **RET8 = SALDO RETIRO EXCESO:**
  - Valor ingresado por el contribuyente.
  - Para los RUT obtenidos desde el RIAC, sólo deberán estar disponible para ingreso de valor aquellos RUT que se encuentran vigentes al 31.12.AT-1. Para los otros RUT la celda deberá estar bloqueada.
  - Al **agregar registro**, esta columna **no** debe estar habilitada para ingresar datos.
  - Si declarante **duplica registro**, este campo **no** debe estar habilitado para ingresar datos.

- **RET9 = FECHA RETIRO:**
  - Valor ingresado por el contribuyente.
  - Formato de la celda deberá ser dd/mm/AT-1.
  - Debe corresponder a fechas entre el 01.01.AT-1 y 31.12.AT-1.
  - Si ingresa RET10=[MONTO RETIRO] deberá informar la fecha en que se realizó.
  - Para un mismo RUT no podrá ingresar dos veces la misma fecha.
  - Si declarante duplica registro, este campo debe estar habilitado para ingresar una nueva fecha.

- **RET10 = MONTO RETIRO:**
  - Valor ingresado por el contribuyente.
  - Si el declarante **duplica registro** o **agrega registro**, este campo debe estar habilitado para ingresar monto.

- **RET11 = MONTO ISFUT_H:**
  - Valor ingresado por el contribuyente.
  - Si el declarante **duplica registro** o **agrega registro**, este campo debe estar habilitado para ingresar monto.

- **RET12 = MONTO ISFUT_A:**
  - Valor ingresado por el contribuyente.
  - Si el declarante **duplica registro** o **agrega registro**, este campo debe estar habilitado para ingresar monto.

## Variables para usos posteriores

- RET30 = ∑RET5 (considera todos los RET1 (Rut))
- RET14 = ∑RET6 por cada RET1 (Rut)
- RET15 = ∑RET6 (considera todos los RET1 (Rut))
- 1040<sub>Socio</sub> = RET5 por Socio (RET1) y fecha. Dado que solo hay un registro por fecha, se generan tantos 1040<sub>Socio</sub> como fechas existan.
- 1041<sub>Socio</sub> = RET6 por Socio (RET1) y fecha. Dado que solo hay un registro por fecha, se generan tantos 1041<sub>Socio</sub> como fechas (y registros) existan.
- 1042<sub>Socio</sub> = RET7 por Socio (RET1) y fecha. Dado que solo hay un registro por fecha, se generan tantos 1042<sub>Socio</sub> como fechas (y registros) existan.
- 1043<sub>Socio</sub> = RET8 por Socio (RET1)
- 1049<sub>Socio</sub> = RET10 por Socio (RET1) y fecha. Dado que solo hay un registro por fecha, se generan tantos 1049<sub>Socio</sub> como fechas (y registros) existan.
- 1051<sub>Socio</sub> = RET11 por Socio (RET1) y fecha. Dado que solo hay un registro por fecha, se generan tantos 1051<sub>Socio</sub> como fechas (y registros) existan.
- 1052<sub>Socio</sub> = RET12 por Socio (RET1) y fecha. Dado que solo hay un registro por fecha, se generan tantos 1052<sub>Socio</sub> como fechas (y registros) existan.

### Por ejemplo

| **Rut socio** | **Usufructuario** | **Cantidad de Acciones** | **Retiros efectivos del ejercicio** | **Retiros efectivos del ejercicio** | **Retiros efectivos del ejercicio** | **Retiros efectivos del ejercicio** | **Saldo monto de retiro en exceso AT-1** | **Devolución de capital** | **Devolución de capital** | **Devolución de capital** | **Devolución de capital** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | **Fecha Retiro** | **Monto retiro** | **Monto ISFUT_H** | **Monto ISFUT_A** | | **Fecha** | **Monto** | **Monto ISFUT_H** | **Monto ISFUT_A** |
| 1-9 | | 50 | 02/01/2020 | 100 | | | 20 | | | | |
| 1-9 | | | 02/02/2020 | 50 | | | | | | | |
| 2-7 | | 50 | 02/03/2020 | 25 | | | | | | | |
| 3-5 | 1 | | 02/04/2020 | 25 | | | | | | | |

Se generan 4 valores 1040<sub>Socio</sub>:

- 1040<sub>1-9</sub> = 100 asociado al 02/01/2020
- 1040<sub>1-9</sub> = 50 asociado al 02/02/2020
- 1040<sub>2-7</sub> = 25 asociado al 02/03/2020
- 1040<sub>3-5</sub> = 25 asociado al 02/04/2020

Y el valor de RET30 es 200 (100+50+25+25).

Además, se genera 1043<sub>1-9</sub> = 20.

---

**Notas sobre la conversión desde Word a markdown:**
- La tabla principal tiene encabezados anidados en el original (grupos como "Retiros efectivos del ejercicio" y "Devolución de capital" que abarcan 4 columnas cada uno). Como Markdown estándar no soporta celdas combinadas (rowspan/colspan), se repitió el nombre del grupo en cada columna que abarca, y se agregó una fila adicional en negrita con el subtítulo específico de cada columna (Fecha, Monto, etc.), justo debajo de la fila de letras (A–L).
- El texto resaltado en amarillo en el original (`Vx04661 - Vx04662 - Vx04663` y los símbolos `≥`) se marcó con `<mark>` para conservar esa señal visual. (no es importante para la visualizacion en la web)
- El título principal y la palabra "NOTA" estaban subrayados en el original; se representaron con `<u>`.
- Los subíndices (ej. 1040_Socio, RET5_fecha_n_socio_n) se representaron con `<sub>`.
