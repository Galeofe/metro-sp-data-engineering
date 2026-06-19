"""
Ingestion — Qualidade do Ar (CETESB)
Simula arquivos CSV com separador ponto-e-vírgula, formato de data brasileiro,
campos ausentes como strings vazias e estação CAC001 com CO em ppm (não µg/m³).
"""
from datetime import datetime, timedelta
from io import StringIO
import numpy as np
import pandas as pd

from config.settings import ESTACOES_AR, N_AIR_HOURS, RANDOM_SEED
from utils.logger import get_logger

log = get_logger("ingestion.air_quality")
rng = np.random.default_rng(RANDOM_SEED + 1)

_HEADER = (
    "ESTACAO_ID;DT_MEDICAO;HORA;"
    "MP10_ug_m3;MP2.5_ug_m3;O3_ug_m3;NO2_ug_m3;CO_mg_m3;SO2_ug_m3;"
    "TEMP_C;UMIDADE_PCT;PRESSAO_hPa;VENTO_DIR_GRAUS;VENTO_VEL_ms"
)


def _fmt(value, empty_prob: float = 0.0) -> str:
    if rng.random() < empty_prob:
        return ""
    if value is None:
        return ""
    return str(value)


def generate() -> pd.DataFrame:
    base = datetime(2026, 6, 17, 0, 0, 0)
    linhas = [_HEADER]

    for h in range(N_AIR_HOURS):
        dt   = base + timedelta(hours=h)
        hora = dt.hour
        fator = 1.0 + 0.8 * (
            np.exp(-((hora - 8) ** 2) / 6.0) +
            np.exp(-((hora - 19) ** 2) / 6.0)
        )

        for est in ESTACOES_AR:
            mp10  = round(float(rng.normal(38.0 * fator, 8.0)), 1)
            mp25  = round(float(rng.normal(17.0 * fator, 5.0)), 1)
            o3    = round(float(rng.normal(80.0, 20.0)), 1)
            no2   = round(float(rng.normal(50.0 * fator, 12.0)), 1)
            co    = round(float(rng.normal(0.85 * fator, 0.2)), 2)
            so2   = round(float(rng.normal(4.5, 1.5)), 1)
            temp  = round(19.0 + 5.0 * np.sin(hora * np.pi / 12.0) + float(rng.normal(0, 1.5)), 1)
            umid  = round(float(np.clip(rng.normal(72.0, 8.0), 20, 100)), 1)
            press = round(float(rng.normal(1013.0, 3.0)), 1)
            vdir  = int(rng.integers(0, 360))
            vvel  = round(float(rng.exponential(3.5)), 1)

            # Bug 1: estação CAC001 reporta CO em ppm (fator ÷ 1.165 para simular)
            if est["id"] == "CAC001":
                co = round(co / 1.165, 3)

            # Bug 2: valores negativos esporádicos de sensor com defeito (~1%)
            if rng.random() < 0.01:
                mp25 = -round(float(rng.uniform(0.1, 1.5)), 1)

            linhas.append(";".join([
                est["id"],
                dt.strftime("%d/%m/%Y"),  # formato BR — problema proposital
                dt.strftime("%H:00"),
                _fmt(mp10, empty_prob=0.07),
                _fmt(mp25),
                _fmt(o3),
                _fmt(no2),
                _fmt(co, empty_prob=0.04),
                _fmt(so2, empty_prob=0.06),
                _fmt(temp, empty_prob=0.03),
                _fmt(umid),
                _fmt(press),
                str(vdir),
                str(vvel),
            ]))

    df = pd.read_csv(StringIO("\n".join(linhas)), sep=";", dtype=str)
    log.info("Gerados %d registros de qualidade do ar (Bronze)", len(df))
    log.info("  Campos MP10 vazios:  %d", (df["MP10_ug_m3"] == "").sum())
    log.info("  Campos CO   vazios:  %d", (df["CO_mg_m3"] == "").sum())
    log.info("  Registros CAC001 (CO em ppm): %d", (df["ESTACAO_ID"] == "CAC001").sum())
    return df
