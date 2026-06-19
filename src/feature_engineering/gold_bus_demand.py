"""
Gold — Dataset para XGBoost (Previsão de Demanda de Transporte)
- Agrega GPS por linha/hora → estimativa de lotação média
- Join com meteorologia
- Features de calendário e lags temporais
- Target: lotação na próxima hora
"""
import pandas as pd
import numpy as np
from utils.logger import get_logger

log = get_logger("gold.bus_demand")

_LOTACAO_NUM = {"VAZIA": 0.1, "MEIA": 0.4, "CHEIA": 0.75, "LOTADA": 1.0, "DESCONHECIDA": 0.5}
_FERIADOS = {"2026-06-11", "2026-06-15", "2026-06-18"}


def build(df_gps: pd.DataFrame, df_weather: pd.DataFrame) -> pd.DataFrame:
    df = df_gps[df_gps["ativo"]].copy()

    # 1. Converte lotação enum → numérico (0–1)
    df["lotacao_num"] = df["lotacao"].map(_LOTACAO_NUM).fillna(0.5)

    # 2. Agrega por linha × hora
    df["hora_ref"] = df["timestamp_utc"].dt.floor("h")
    agg = (
        df.groupby(["linha", "hora_ref"])
        .agg(
            lotacao_media=("lotacao_num", "mean"),
            n_veiculos=("prefixo", "nunique"),
            velocidade_media=("velocidade", "mean"),
        )
        .reset_index()
    )

    # 3. Join meteorologia
    df_w = df_weather[["timestamp_utc", "temperatura_c", "precipitacao_mm", "umidade_pct"]].copy()
    df_w["hora_ref"] = df_w["timestamp_utc"].dt.floor("h")
    agg = agg.merge(
        df_w[["hora_ref", "temperatura_c", "precipitacao_mm"]].drop_duplicates("hora_ref"),
        on="hora_ref", how="left"
    )

    # 4. Features de calendário
    agg["hora_do_dia"] = agg["hora_ref"].dt.hour
    agg["dia_semana"]  = agg["hora_ref"].dt.dayofweek  # 0=segunda
    agg["e_feriado"]   = agg["hora_ref"].dt.strftime("%Y-%m-%d").isin(_FERIADOS).astype(int)
    agg["e_fim_semana"]= (agg["dia_semana"] >= 5).astype(int)

    # 5. Lags temporais por linha
    agg = agg.sort_values(["linha", "hora_ref"])
    agg["lag_1h"]   = agg.groupby("linha")["lotacao_media"].shift(1)
    agg["lag_24h"]  = agg.groupby("linha")["lotacao_media"].shift(24)

    # 6. Target: lotação na próxima hora
    agg["target"] = agg.groupby("linha")["lotacao_media"].shift(-1)

    # 7. Codifica linha como dummy (one-hot)
    agg = pd.get_dummies(agg, columns=["linha"], prefix="linha")

    # Preenche lag_24h com lag_1h quando série ainda é curta
    agg["lag_24h"] = agg["lag_24h"].fillna(agg["lag_1h"])

    # 8. Remove linhas sem target ou lag_1h
    agg = agg.dropna(subset=["target", "lag_1h"])

    # Preenche nulos restantes
    agg = agg.fillna(0.0)

    log.info("Gold demanda transporte: %d registros", len(agg))
    log.info("  Features: %d", len(agg.columns))
    return agg
