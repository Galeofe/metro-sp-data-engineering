"""
Silver — Limpeza dos Sensores de Tráfego
- Detecta e corrige timestamps BRT vs UTC
- Remove campos operacionais (firmware, bateria)
- Classifica qualidade de cada registro
- Imputa velocidade=0 quando contagem=0
"""
import pandas as pd
import numpy as np
from utils.logger import get_logger

log = get_logger("silver.traffic")


def _parse_timestamp(raw) -> pd.Timestamp:
    """Retorna sempre um Timestamp UTC-aware para evitar mistura de tipos."""
    if pd.isna(raw):
        return pd.NaT
    s = str(raw)
    if s.endswith("Z"):
        return pd.to_datetime(s.rstrip("Z")).tz_localize("UTC")
    # Sem 'Z' → assumir BRT (UTC-3) e converter para UTC
    dt = pd.to_datetime(s)
    return (dt + pd.Timedelta(hours=3)).tz_localize("UTC")


def transform(df_bronze: pd.DataFrame) -> pd.DataFrame:
    df = df_bronze.copy()

    # 1. Parse de timestamp — produz lista de UTC-aware Timestamps
    parsed = [_parse_timestamp(ts) for ts in df["timestamp_raw"]]
    df["timestamp_utc"] = pd.DatetimeIndex(parsed)

    # 2. Classifica qualidade
    df["qualidade"] = "OK"
    df.loc[df["contagem_veiculos"] == -1, "qualidade"] = "SENSOR_MANUTENCAO"
    mask_zero = (df["contagem_veiculos"] == 0) & df["velocidade_media_kmh"].isna()
    df.loc[mask_zero, "qualidade"] = "VELOCIDADE_INFERIDA"

    # 3. Trata manutenção — anula contagem e ocupação
    manut = df["qualidade"] == "SENSOR_MANUTENCAO"
    df.loc[manut, "contagem_veiculos"] = pd.NA
    df.loc[manut, "ocupacao_pct"]      = pd.NA
    df.loc[manut, "n_carros"]          = pd.NA
    df.loc[manut, "n_motos"]           = pd.NA
    df.loc[manut, "n_onibus"]          = pd.NA

    # 4. Velocidade=0 para registros sem veículos
    df.loc[mask_zero, "velocidade_media_kmh"] = 0.0

    # 5. Renomeia e remove campos não analíticos
    df = df.rename(columns={"velocidade_media_kmh": "velocidade_kmh"})
    df = df.drop(columns=["timestamp_raw", "firmware_version", "bateria_pct",
                           "_ingested_at", "_source_system"], errors="ignore")

    # 6. Particiona por data
    df["dt_particao"] = df["timestamp_utc"].dt.date

    log.info("Silver tráfego: %d registros", len(df))
    log.info("  Qualidade OK:              %d", (df.qualidade == "OK").sum())
    log.info("  SENSOR_MANUTENCAO:         %d", (df.qualidade == "SENSOR_MANUTENCAO").sum())
    log.info("  VELOCIDADE_INFERIDA:       %d", (df.qualidade == "VELOCIDADE_INFERIDA").sum())
    return df
