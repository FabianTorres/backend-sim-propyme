import json

from app.schemas.orquestador import SimuladorGlobalRequest
from app.services.orquestador import OrquestadorService

with open("tmp_payload.json", encoding="utf-8") as fh:
    payload = json.load(fh)

request = SimuladorGlobalRequest.model_validate(payload)
resp = OrquestadorService().calcular_simulacion(request)

print("=== INGRESOS ===")
print("fila_7_12 (Total ventas y servicios):", resp.ingresos.totales.fila_7_12)
print("fila_7_total (TOTAL INGRESOS):", resp.ingresos.totales.fila_7_total)

print()
print("=== EGRESOS ===")
print("fila_8_total (TOTAL EGRESOS):", resp.egresos.totales.fila_8_total)
print("aviso_arriendos_pagados:", resp.egresos.avisos.aviso_arriendos_pagados)
print("mostrar_columna_patrimonio:", resp.egresos.avisos.mostrar_columna_patrimonio)
print()
print("Fila | B (Egresos anio) | H (adeudados) | F (egresos pagados)")
for f in resp.egresos.filas:
    print(f"{f.codigo:>4} | {f.egresos_ano} | {f.egresos_adeudados_at_anterior} | {f.monto_egresos_pagados}")

print()
f84 = next(f for f in resp.egresos.filas if f.codigo == "8.4")
print("=== INSPECTOR 8.4 (reajuste P77+P179) ===")
insp = f84.inspectores["egresos_ano"]
print("valor:", insp.valor)
print("literal:", insp.literal)
print("evaluado:", insp.evaluado)
print("pasos:", insp.pasos)
