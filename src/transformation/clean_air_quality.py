"""
Silver — Limpeza da Qualidade do Ar (CETESB)
- Converte strings vazias em NaN
- Padroniza data DD/MM/YYYY + hora → timestamp UTC
- Normaliza CO da estação CAC001 de ppm para µg/m³
- Remove valores fisicamente impossíveis (negativos)
- Calcula IQAr composto (metodologia CETESB)
"""
import pandas as pd
import numpy as np
from utils.logger import get_logger
from config.settings import IQAR_BREAKPOINTS

log = get_logger("silver.air_quality")

_NUMERIC = [
    "MP10_ug_m3", "MP2.5_ug_m3", "O3_ug_m3", "NO2_ug_m3",
    "CO_mg_m3", "SO2_ug_m3", "TEMP_C", "UMIDADE_PCT",
    "PRESSAO_hPa", "VENTO_DIR_GRAUS", "VENTO_VEL_ms",
]

_RENAME = {
    "ESTACAO_ID": "estacao_id", "MP10_ug_m3": "mp10", "MP2.5_ug_m3": "mp25",
    "O3_ug_m3": "o3", "NO2_ug_m3": "no2", "CO_mg_m3": "co", "SO2_ug_m3": "so2",
    "TEMP_C": "temp_c", "UMIDADE_PCT": "umidade_pct", "PRESSAO_hPa": "pressao_hpa",
    "VENTO_DIR_GRAUS": "vento_dir", "VENTO_VEL_ms": "vento_vel_ms",
}


def _iqar_poluente(valor: float, pontos: list) -> float:
    if pd.isna(valor) or valor < 0:
        return np.nan
    for cp_lo, cp_hi, iq_lo, iq_hi in pontos:
        if cp_lo <= valor <= cp_hi:
            return iq_lo + (iq_hi - iq_lo) * (valor - cp_lo) / (cp_hi - cp_lo)
    return 400.0


def _faixa(iqar: float) -> str:
    if pd.isna(iqar):   return "INDISPONIVEL"
    if iqar <= 40:      return "BOA"
    if iqar <= 80:      return "MODERADA"
    if iqar <= 120:     return "RUIM"
    if iqar <= 200:     return "MUITO_RUIM"
    return "PESSIMA"


def transform(df_bronze: pd.DataFrame) -> pd.DataFrame:
    df = df_bronze.copy()

    # 1. Strings vazias → NaN
    df = df.replace("", np.nan)

    # 2. Converte numéricos
    for col in _NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 3. Timestamp unificado (DD/MM/YYYY HH:MM → UTC)
    df["timestamp_utc"] = pd.to_datetime(
        df["DT_MEDICAO"].str.strip() + " " + df["HORA"].str.strip(),
        format="%d/%m/%Y %H:%M",
        utc=True,
    )
    df = df.drop(columns=["DT_MEDICAO", "HORA"])

    # 4. Corrige CO da estação CAC001 (ppm → µg/m³, fator CETESB = 1.165)
    cac = df["ESTACAO_ID"] == "CAC001"
    df.loc[cac, "CO_mg_m3"] = df.loc[cac, "CO_mg_m3"] * 1.165

    # 5. Remove valores físicamente impossíveis (concentrações negativas)
    for col in ["MP10_ug_m3", "MP2.5_ug_m3", "O3_ug_m3", "NO2_ug_m3", "CO_mg_m3", "SO2_ug_m3"]:
        df.loc[df[col] < 0, col] = np.nan

    # 6. Renomeia
    df = df.rename(columns=_RENAME)

    # 7. Calcula IQAr composto
    poluentes_iqar = {"mp10": "mp10", "mp25": "mp25", "o3": "o3",
                      "no2": "no2", "co": "co", "so2": "so2"}
    for chave, col in poluentes_iqar.items():
        if col in df.columns:
            pts = IQAR_BREAKPOINTS[chave]
            df[f"_iqar_{chave}"] = df[col].apply(lambda v: _iqar_poluente(v, pts))

    iqar_cols = [c for c in df.columns if c.startswith("_iqar_")]
    df["iqar"]       = df[iqar_cols].max(axis=1)
    df["faixa_iqar"] = df["iqar"].apply(_faixa)
    df = df.drop(columns=iqar_cols)

    df["dt_particao"] = df["timestamp_utc"].dt.date

    log.info("Silver qualidade do ar: %d registros", len(df))
    log.info("  Distribuição IQAr: %s", df.faixa_iqar.value_counts().to_dict())
    log.info("  Nulos MP2.5 após limpeza: %d", df.mp25.isna().sum())
    return df
