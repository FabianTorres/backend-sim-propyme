"""Smoke: corre el caso QA por el Orquestador y muestra el nodo Retiros."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.schemas.orquestador import SimuladorGlobalRequest  # noqa: E402
from app.services.orquestador import OrquestadorService  # noqa: E402


def main() -> None:
    caso = Path(__file__).resolve().parent / "casos" / "rut_69500400-1.json"
    payload = json.loads(caso.read_text(encoding="utf-8"))
    req = SimuladorGlobalRequest.model_validate(payload)
    resp = OrquestadorService().calcular_simulacion(req)
    r = resp.retiros
    print("[1044] =", r.calculo.v1044)
    print("[1045] =", r.calculo.v1045)
    print("RET30 =", r.totales.ret30, "| RET15 =", r.totales.ret15, "| RET14 =", r.totales.ret14)
    print("avisos =", r.avisos.model_dump())
    print("filas =", len(r.filas))
    print("inspectores =", None if r.inspectores is None else sorted(r.inspectores.keys()))


if __name__ == "__main__":
    main()
