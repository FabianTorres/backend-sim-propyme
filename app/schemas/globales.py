"""Datos globales de entrada del Simulador Propyme.

Los vectores (Vx...) y las variables externas (Calc..., atributos) son
compartidos por todas las paginas. Ningun vector pertenece a una pagina en
particular: cada modulo usa el subconjunto que necesite de este namespace
plano.

Estrategia de mapeo:
    - Se declaran estrictamente los codigos que el Motor de Reglas hoy consume.
    - Se usa extra='ignore' para tolerar vectores/externos que el Frontend envie
      y que el backend aun no haya declarado (forward-compat). Con pocos
      vectores nuevos por anio, el modelo crece de forma incremental.
"""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Vectores(BaseModel):
    """Namespace global y plano de vectores Vx... del contribuyente."""

    model_config = ConfigDict(extra="ignore")

    # Control: empresario individual (1 = SI)
    Vx010042: int = Field(default=0)

    # --- Col. H: montos adeudados de AT anterior ---
    Vx014255: Decimal = Field(default=Decimal("0"))
    Vx014256: Decimal = Field(default=Decimal("0"))
    Vx014257: Decimal = Field(default=Decimal("0"))
    Vx014258: Decimal = Field(default=Decimal("0"))
    Vx014259: Decimal = Field(default=Decimal("0"))
    Vx014260: Decimal = Field(default=Decimal("0"))
    Vx014261: Decimal = Field(default=Decimal("0"))
    Vx014262: Decimal = Field(default=Decimal("0"))
    Vx014263: Decimal = Field(default=Decimal("0"))
    Vx014264: Decimal = Field(default=Decimal("0"))
    Vx014265: Decimal = Field(default=Decimal("0"))
    Vx014266: Decimal = Field(default=Decimal("0"))
    Vx014267: Decimal = Field(default=Decimal("0"))

    # --- 7.1 Exportaciones ---
    Vx012188: Decimal = Field(default=Decimal("0"))
    Vx013384: Decimal = Field(default=Decimal("0"))
    Vx013394: Decimal = Field(default=Decimal("0"))
    Vx013395: Decimal = Field(default=Decimal("0"))
    Vx013396: Decimal = Field(default=Decimal("0"))

    # --- 7.2 Facturas por ventas y servicios gravados ---
    Vx012194: Decimal = Field(default=Decimal("0"))
    Vx013257: Decimal = Field(default=Decimal("0"))
    Vx013372: Decimal = Field(default=Decimal("0"))
    Vx013381: Decimal = Field(default=Decimal("0"))
    Vx013387: Decimal = Field(default=Decimal("0"))
    Vx013382: Decimal = Field(default=Decimal("0"))
    Vx013383: Decimal = Field(default=Decimal("0"))

    # --- 7.3 Ventas Exentas / No Gravadas ---
    Vx012189: Decimal = Field(default=Decimal("0"))
    Vx013365: Decimal = Field(default=Decimal("0"))
    Vx013366: Decimal = Field(default=Decimal("0"))
    Vx013367: Decimal = Field(default=Decimal("0"))
    Vx013368: Decimal = Field(default=Decimal("0"))
    Vx013369: Decimal = Field(default=Decimal("0"))
    Vx013370: Decimal = Field(default=Decimal("0"))
    Vx013371: Decimal = Field(default=Decimal("0"))
    Vx013385: Decimal = Field(default=Decimal("0"))

    # --- 7.4 Ventas con retencion sobre margen de comercializacion ---
    Vx012191: Decimal = Field(default=Decimal("0"))

    # --- 7.5 Fact. compra Retencion total ---
    Vx012192: Decimal = Field(default=Decimal("0"))
    Vx013379: Decimal = Field(default=Decimal("0"))
    Vx013380: Decimal = Field(default=Decimal("0"))

    # --- 7.6 Fact. compra Retencion parcial ---
    Vx012193: Decimal = Field(default=Decimal("0"))
    Vx013378: Decimal = Field(default=Decimal("0"))

    # --- 7.7 Boletas / Transbank ---
    Vx012195: Decimal = Field(default=Decimal("0"))
    Vx013373: Decimal = Field(default=Decimal("0"))
    Vx013374: Decimal = Field(default=Decimal("0"))
    Vx013375: Decimal = Field(default=Decimal("0"))
    Vx013376: Decimal = Field(default=Decimal("0"))

    # --- 7.8 Notas de credito emitidas ---
    Vx012197: Decimal = Field(default=Decimal("0"))

    # --- 7.9 Notas de debito emitidas ---
    Vx013377: Decimal = Field(default=Decimal("0"))

    # --- 7.14 Mayor valor inversiones / bienes no depreciables ---
    Vx010118: Decimal = Field(default=Decimal("0"))
    Vx012830: Decimal = Field(default=Decimal("0"))
    Vx010240: Decimal = Field(default=Decimal("0"))
    Vx013639: Decimal = Field(default=Decimal("0"))

    # --- 7.15 Arriendos de bienes raices ---
    Vx012209: Decimal = Field(default=Decimal("0"))

    # --- 7.17 Intereses Directos ---
    Vx010145: Decimal = Field(default=Decimal("0"))
    Vx012210: Decimal = Field(default=Decimal("0"))
    Vx010357: Decimal = Field(default=Decimal("0"))
    Vx010974: Decimal = Field(default=Decimal("0"))
    Vx010358: Decimal = Field(default=Decimal("0"))
    Vx010059: Decimal = Field(default=Decimal("0"))
    Vx010088: Decimal = Field(default=Decimal("0"))
    Vx010985: Decimal = Field(default=Decimal("0"))

    # --- 7.18 Intereses Indirectos ---
    Vx010238: Decimal = Field(default=Decimal("0"))
    Vx010239: Decimal = Field(default=Decimal("0"))
    Vx010236: Decimal = Field(default=Decimal("0"))
    Vx010237: Decimal = Field(default=Decimal("0"))
    Vx010934: Decimal = Field(default=Decimal("0"))
    Vx011015: Decimal = Field(default=Decimal("0"))

    # --- 7.19 Renta de fuente extranjera ---
    Vx013633: Decimal = Field(default=Decimal("0"))
    Vx013634: Decimal = Field(default=Decimal("0"))
    Vx013635: Decimal = Field(default=Decimal("0"))
    Vx013636: Decimal = Field(default=Decimal("0"))
    Vx013637: Decimal = Field(default=Decimal("0"))
    Vx013638: Decimal = Field(default=Decimal("0"))

    # --- 7.20 Otros ingresos ---
    Vx013640: Decimal = Field(default=Decimal("0"))
    Vx013641: Decimal = Field(default=Decimal("0"))
    Vx013642: Decimal = Field(default=Decimal("0"))
    Vx013643: Decimal = Field(default=Decimal("0"))
    Vx013644: Decimal = Field(default=Decimal("0"))
    Vx013645: Decimal = Field(default=Decimal("0"))

    # --- Mensaje validacion / patrimonio personal (VALOR1_PCalc) ---
    Vx013601: Decimal = Field(default=Decimal("0"))
    Vx013602: Decimal = Field(default=Decimal("0"))
    Vx013603: Decimal = Field(default=Decimal("0"))
    Vx013604: Decimal = Field(default=Decimal("0"))
    Vx013506: Decimal = Field(default=Decimal("0"))
    Vx013507: Decimal = Field(default=Decimal("0"))
    Vx013508: Decimal = Field(default=Decimal("0"))
    Vx013509: Decimal = Field(default=Decimal("0"))
    Vx013510: Decimal = Field(default=Decimal("0"))
    Vx013511: Decimal = Field(default=Decimal("0"))
    Vx013512: Decimal = Field(default=Decimal("0"))
    Vx013513: Decimal = Field(default=Decimal("0"))
    Vx013560: Decimal = Field(default=Decimal("0"))
    Vx013561: Decimal = Field(default=Decimal("0"))
    Vx013562: Decimal = Field(default=Decimal("0"))
    Vx013563: Decimal = Field(default=Decimal("0"))
    Vx013564: Decimal = Field(default=Decimal("0"))
    Vx013565: Decimal = Field(default=Decimal("0"))
    Vx013566: Decimal = Field(default=Decimal("0"))
    Vx013567: Decimal = Field(default=Decimal("0"))
    Vx013568: Decimal = Field(default=Decimal("0"))
    Vx013569: Decimal = Field(default=Decimal("0"))
    Vx013570: Decimal = Field(default=Decimal("0"))
    Vx013571: Decimal = Field(default=Decimal("0"))
    Vx013605: Decimal = Field(default=Decimal("0"))
    Vx013606: Decimal = Field(default=Decimal("0"))
    Vx013607: Decimal = Field(default=Decimal("0"))
    Vx013608: Decimal = Field(default=Decimal("0"))
    Vx013588: Decimal = Field(default=Decimal("0"))
    Vx013589: Decimal = Field(default=Decimal("0"))
    Vx013590: Decimal = Field(default=Decimal("0"))
    Vx013591: Decimal = Field(default=Decimal("0"))
    Vx013592: Decimal = Field(default=Decimal("0"))
    Vx013609: Decimal = Field(default=Decimal("0"))
    Vx013610: Decimal = Field(default=Decimal("0"))
    Vx013611: Decimal = Field(default=Decimal("0"))
    Vx013612: Decimal = Field(default=Decimal("0"))
    Vx013613: Decimal = Field(default=Decimal("0"))
    Vx013614: Decimal = Field(default=Decimal("0"))
    Vx013615: Decimal = Field(default=Decimal("0"))
    Vx013616: Decimal = Field(default=Decimal("0"))
    Vx012420: Decimal = Field(default=Decimal("0"))
    Vx012424: Decimal = Field(default=Decimal("0"))
    Vx013750: Decimal = Field(default=Decimal("0"))

    # --- Mensaje validacion / patrimonio personal (VALOR2_PCalc) ---
    Vx013514: Decimal = Field(default=Decimal("0"))
    Vx013515: Decimal = Field(default=Decimal("0"))
    Vx013516: Decimal = Field(default=Decimal("0"))
    Vx013517: Decimal = Field(default=Decimal("0"))
    Vx013518: Decimal = Field(default=Decimal("0"))
    Vx013519: Decimal = Field(default=Decimal("0"))
    Vx013520: Decimal = Field(default=Decimal("0"))
    Vx013521: Decimal = Field(default=Decimal("0"))
    Vx013523: Decimal = Field(default=Decimal("0"))
    Vx013524: Decimal = Field(default=Decimal("0"))
    Vx013525: Decimal = Field(default=Decimal("0"))
    Vx013526: Decimal = Field(default=Decimal("0"))
    Vx013528: Decimal = Field(default=Decimal("0"))
    Vx013572: Decimal = Field(default=Decimal("0"))
    Vx013573: Decimal = Field(default=Decimal("0"))
    Vx013574: Decimal = Field(default=Decimal("0"))
    Vx013575: Decimal = Field(default=Decimal("0"))
    Vx013576: Decimal = Field(default=Decimal("0"))
    Vx013577: Decimal = Field(default=Decimal("0"))
    Vx013578: Decimal = Field(default=Decimal("0"))
    Vx013579: Decimal = Field(default=Decimal("0"))
    Vx013581: Decimal = Field(default=Decimal("0"))
    Vx013582: Decimal = Field(default=Decimal("0"))
    Vx013583: Decimal = Field(default=Decimal("0"))
    Vx013584: Decimal = Field(default=Decimal("0"))
    Vx013586: Decimal = Field(default=Decimal("0"))
    Vx013617: Decimal = Field(default=Decimal("0"))
    Vx013618: Decimal = Field(default=Decimal("0"))
    Vx013593: Decimal = Field(default=Decimal("0"))
    Vx013594: Decimal = Field(default=Decimal("0"))
    Vx013619: Decimal = Field(default=Decimal("0"))
    Vx013620: Decimal = Field(default=Decimal("0"))
    Vx013595: Decimal = Field(default=Decimal("0"))
    Vx013596: Decimal = Field(default=Decimal("0"))
    Vx013621: Decimal = Field(default=Decimal("0"))
    Vx013622: Decimal = Field(default=Decimal("0"))
    Vx013623: Decimal = Field(default=Decimal("0"))
    Vx013597: Decimal = Field(default=Decimal("0"))
    Vx013598: Decimal = Field(default=Decimal("0"))
    Vx013625: Decimal = Field(default=Decimal("0"))
    Vx012421: Decimal = Field(default=Decimal("0"))
    Vx012425: Decimal = Field(default=Decimal("0"))
    Vx012426: Decimal = Field(default=Decimal("0"))

    @field_validator("*", mode="before")
    @classmethod
    def _normalizar(cls, value):
        """Normaliza valores nulos / cadenas vacias a Decimal de cero."""
        if value is None:
            return Decimal("0")
        if isinstance(value, str) and value.strip() == "":
            return Decimal("0")
        return value


class Externos(BaseModel):
    """Variables externas globales provenientes de otros asistentes (ej. BR).

    Calc4064: monto proveniente del asistente de Bienes Raices. Puede ser un
              monto (>0) o el literal 'N'. Se modela como Decimal | Literal['N'].
    Calc4075: flag 0/1 del asistente de Bienes Raices.
    """

    model_config = ConfigDict(extra="ignore")

    Calc4064: Decimal | Literal["N"] = Field(default=Decimal("0"))
    Calc4075: int = Field(default=0)
    CRRP: bool = Field(default=False, description="Atributo de Renta Presunta")

    @field_validator("Calc4064", mode="before")
    @classmethod
    def _norm_calc4064(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if value.upper() == "N":
                return "N"
            if value == "":
                return Decimal("0")
            return Decimal(value)
        return value