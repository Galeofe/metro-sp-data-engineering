"""
Silver — Limpeza dos Dados Meteorológicos (INMET)
- Converte todos os campos de string para tipos nativos
- Substitui a string "null" por NaN real
- Unifica DT_MEDICAO + HR_MEDICAO em timestamp UTC
"""
import pandas as pd
import numpy as np
from utils.logger import get_logger

log = get_logger("silver.weather")

_NUMERIC = [
    "VL_TEMPERATURA", "VL_TEMPERATURA_MAX", "VL_TEMPERATURA_MIN",
    "VL_UMIDADE_REL_AR", "VL_PRESSAO_ATM_EST", "VL_VENTO_VELOCIDADE",
    "VL_VENTO_DIRECAO", "VL_PRECIPITACAO_TOTAL", "VL_RADIACAO_GLOBAL",
]

_RENAME = {
    "CD_ESTACAO":          "cd_estacao",
    "VL_TEMPERATURA":      "temperatura_c",
    "VL_TEMPERATURA_MAX":  "temp_max_c",
    "VL_TEMPERATURA_MIN":  "temp_min_c",
    "VL_UMIDADE_REL_AR":   "umidade_pct",
    "VL_PRESSAO_ATM_EST":  "pressao_hpa",
    "VL_VENTO_VELOCIDADE": "vento_ms",
    "VL_VENTO_DIRECAO":    "vento_dir",
    "VL_PRECIPITACAO_TOTAL":"precipitacao_mm",
    "VL_RADIACAO_GLOBAL":  "radiacao_wm2",
}


def transform(df_bronze: pd.DataFrame) -> pd.DataFrame:
    df = df_bronze.copy()

    # 1. "null" (string) → NaN real
    df = df.replace("null", np.nan)

    # 2. Converte numéricos
    for col in _NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 3. Unifica data + hora em timestamp UTC
    df["timestamp_utc"] = pd.to_datetime(
        df["DT_MEDICAO"] + " " + df["HR_MEDICAO"].str.zfill(4).str[:2] + ":00",
        format="%Y-%m-%d %H:%M",
        utc=True,
    )
    df = df.drop(columns=["DT_MEDICAO", "HR_MEDICAO", "CD_SITUACAO"])

    # 4. Renomeia
    df = df.rename(columns=_RENAME)
    df["dt_particao"] = df["timestamp_utc"].dt.date

    log.info("Silver meteorologia: %d registros", len(df))
    log.info("  Nulos precipitação: %d", df.precipitacao_mm.isna().sum())
    return df
