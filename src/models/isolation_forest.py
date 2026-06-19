"""
Modelo — Isolation Forest para Detecção de Anomalias de Qualidade do Ar
Treina um modelo por estação de monitoramento e retorna o DataFrame
anotado com scores e predições de anomalia.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, roc_auc_score
from utils.logger import get_logger
from config.settings import ISOLATION_FOREST_PARAMS

log = get_logger("model.isolation_forest")

_FEATURE_COLS = ["mp10", "mp25", "o3", "no2", "co", "so2",
                 "temp_c", "umidade_pct", "vento_vel_ms", "hora_do_dia"]


def train_and_predict(df_gold: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Treina um Isolation Forest para cada estação e retorna:
    - df anotado com `anomaly_score` e `anomalia_pred`
    - dicionário com métricas por estação
    """
    df = df_gold.copy()
    df["anomaly_score"] = np.nan
    df["anomalia_pred"] = 0
    metricas = {}

    feature_cols = [c for c in _FEATURE_COLS if c in df.columns]
    estacoes = df["estacao_id"].unique() if "estacao_id" in df.columns else ["global"]

    for est in estacoes:
        if "estacao_id" in df.columns:
            mask = df["estacao_id"] == est
        else:
            mask = pd.Series([True] * len(df), index=df.index)

        X = df.loc[mask, feature_cols].fillna(0).values

        if len(X) < 20:
            log.warning("Estação %s com poucos dados (%d). Pulando.", est, len(X))
            continue

        clf = IsolationForest(**ISOLATION_FOREST_PARAMS)
        clf.fit(X)

        scores = clf.score_samples(X)          # mais negativo = mais anômalo
        preds  = (clf.predict(X) == -1).astype(int)   # -1 → anomalia → 1

        df.loc[mask, "anomaly_score"] = scores
        df.loc[mask, "anomalia_pred"] = preds

        # Métricas vs label
        if "label_anomalia" in df.columns:
            y_true = df.loc[mask, "label_anomalia"].values
            try:
                auc = roc_auc_score(y_true, -scores)
            except Exception:
                auc = float("nan")
            metricas[est] = {
                "n_amostras":      int(mask.sum()),
                "anomalias_pred":  int(preds.sum()),
                "anomalias_label": int(y_true.sum()),
                "roc_auc":         round(auc, 4),
            }
            log.info("  Estação %-10s  n=%4d  anomalias_pred=%3d  ROC-AUC=%.3f",
                     est, mask.sum(), preds.sum(), auc)

    total_anomalias = df["anomalia_pred"].sum()
    log.info("Isolation Forest concluído: %d anomalias detectadas (%.1f%%)",
             total_anomalias, total_anomalias / len(df) * 100)
    return df, metricas
