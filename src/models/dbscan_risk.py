"""
Modelo — DBSCAN para Mapeamento de Áreas de Risco Urbano
Agrupa ocorrências de ouvidoria por proximidade geográfica e caracteriza
cada cluster pela categoria dominante e prioridade média.
"""
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from utils.logger import get_logger
from config.settings import DBSCAN_PARAMS

log = get_logger("model.dbscan_risk")


def cluster(df_gold: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retorna:
    - df_gold anotado com `cluster_id`
    - df_clusters: resumo de cada cluster (centroide, categoria, prioridade, tamanho)
    """
    df = df_gold.copy()
    coords = df[["lat", "lon"]].dropna()

    model = DBSCAN(**DBSCAN_PARAMS)
    labels = model.fit_predict(coords.values)

    df.loc[coords.index, "cluster_id"] = labels
    df["cluster_id"] = df["cluster_id"].fillna(-1).astype(int)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_ruido    = (labels == -1).sum()
    log.info("DBSCAN: %d clusters encontrados, %d pontos de ruído", n_clusters, n_ruido)

    # Resumo por cluster
    summaries = []
    for cid in sorted(df["cluster_id"].unique()):
        if cid == -1:
            continue
        grupo = df[df["cluster_id"] == cid]
        cat_dominante = grupo["categoria_l1"].value_counts().idxmax()
        summaries.append({
            "cluster_id":      cid,
            "lat_centro":      round(grupo["lat"].mean(), 5),
            "lon_centro":      round(grupo["lon"].mean(), 5),
            "n_ocorrencias":   len(grupo),
            "categoria_dom":   cat_dominante,
            "prioridade_media":round(grupo["prioridade"].mean(), 2),
            "bairros":         ", ".join(grupo["bairro"].value_counts().head(2).index),
        })

    df_clusters = pd.DataFrame(summaries)
    if not df_clusters.empty:
        log.info("  Clusters por categoria:\n%s",
                 df[df.cluster_id >= 0].groupby("categoria_l1")["cluster_id"]
                 .nunique().to_string())

    return df, df_clusters
