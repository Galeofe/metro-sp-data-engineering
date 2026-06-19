"""
Gold — Dataset para Isolation Forest (Anomalias de Qualidade do Ar)
- Join com dados meteorológicos Silver
- Z-score de cada poluente em relação ao histórico da estação
- Imputa NaN por mediana da estação
- StandardScaler — features prontas para sklearn
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from utils.logger import get_logger

log = get_logger("gold.air_quality")

_FEATURES = ["mp10", "mp25", "o3", "no2", "co", "so2",
             "temp_c", "umidade_pct", "vento_vel_ms"]


def build(df_ar: pd.DataFrame, df_weather: pd.DataFrame) -> pd.DataFrame:
    # 1. Join com meteorologia por hora mais próxima
    df_ar = df_ar.copy()
    df_w  = df_weather[["timestamp_utc", "temperatura_c", "precipitacao_mm",
                         "umidade_pct", "vento_ms"]].copy()
    df_w  = df_w.rename(columns={"temperatura_c": "temp_met",
                                  "precipitacao_mm": "chuva_mm",
                                  "umidade_pct": "umid_met",
                                  "vento_ms": "vento_met"})

    # Arredonda horas para fazer merge temporal
    df_ar["_hora_join"] = df_ar["timestamp_utc"].dt.floor("h")
    df_w["_hora_join"]  = df_w["timestamp_utc"].dt.floor("h")
    df = df_ar.merge(df_w.drop(columns="timestamp_utc"),
                     on="_hora_join", how="left").drop(columns="_hora_join")

    # 2. Preenche coluna temp_c: prefere sensor de AR, cai back para meteorologia
    df["temp_c"] = df["temp_c"].fillna(df["temp_met"])
    df = df.drop(columns=["temp_met", "umid_met", "vento_met"], errors="ignore")

    # 3. Imputa nulos por mediana da estação
    for col in _FEATURES:
        if col in df.columns:
            df[col] = df.groupby("estacao_id")[col].transform(
                lambda s: s.fillna(s.median())
            )

    # 4. Z-score por estação (desvio relativo ao histórico local)
    for col in ["mp10", "mp25", "o3", "no2"]:
        df[f"z_{col}"] = df.groupby("estacao_id")[col].transform(
            lambda s: (s - s.mean()) / (s.std() + 1e-8)
        )

    # 5. Feature temporal
    df["hora_do_dia"] = df["timestamp_utc"].dt.hour

    # 6. Label de anomalia: IQAr ≥ RUIM (>80)
    df["label_anomalia"] = (df["iqar"] > 80).astype(int)

    # 7. Normalização das features (StandardScaler)
    feature_cols = [c for c in _FEATURES if c in df.columns] + \
                   [f"z_{c}" for c in ["mp10","mp25","o3","no2"]] + \
                   ["hora_do_dia"]
    feature_cols = [c for c in feature_cols if c in df.columns]

    scaler = StandardScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols].fillna(0))

    df = df.dropna(subset=["estacao_id", "timestamp_utc"])

    log.info("Gold qualidade do ar: %d registros, %d features", len(df), len(feature_cols))
    log.info("  Anomalias (IQAr > 80): %d (%.1f%%)",
             df.label_anomalia.sum(), df.label_anomalia.mean() * 100)
    return df
