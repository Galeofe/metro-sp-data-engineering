"""
Gold — Dataset para DBSCAN (Mapa de Risco de Ocorrências)
- Consolida ocorrências de ouvidoria com contexto de IQAr e tráfego
- Codifica categoria hierárquica
- Agrega por área (geohash simplificado via arredondamento de 3 casas)
"""
import pandas as pd
import numpy as np
from utils.logger import get_logger
from config.settings import CATEGORIA_HIERARQUIA

log = get_logger("gold.occurrence_map")


def _geohash_simple(lat: float, lon: float, precision: int = 3) -> str:
    """Geohash aproximado: arredonda para N casas decimais (~100m para 3 casas)."""
    return f"{round(lat, precision)},{round(lon, precision)}"


def build(df_ouvidoria: pd.DataFrame, df_ar: pd.DataFrame) -> pd.DataFrame:
    df = df_ouvidoria.copy()

    # 1. Hierarquia de categorias
    df["categoria_l1"] = df["categoria"].map(
        lambda c: CATEGORIA_HIERARQUIA.get(c, ("OUTROS", "NAO_CLASSIFICADO"))[0]
    )
    df["categoria_l2"] = df["categoria"].map(
        lambda c: CATEGORIA_HIERARQUIA.get(c, ("OUTROS", "NAO_CLASSIFICADO"))[1]
    )

    # 2. Geohash simplificado por localização
    df["geohash"] = df.apply(lambda r: _geohash_simple(r["lat"], r["lon"]), axis=1)

    # 3. Feature temporal
    df["hora_abertura"] = pd.to_datetime(df["dt_abertura"]).dt.hour
    df["dia_semana"]    = pd.to_datetime(df["dt_abertura"]).dt.dayofweek

    # 4. Contexto IQAr: IQAr médio da estação mais próxima no mesmo período
    iqar_medio = df_ar.groupby("dt_particao")["iqar"].mean().reset_index()
    iqar_medio = iqar_medio.rename(columns={"iqar": "iqar_medio_dia"})
    df["dt_particao_str"] = pd.to_datetime(df["dt_particao"]).dt.date
    iqar_medio["dt_particao"] = pd.to_datetime(iqar_medio["dt_particao"]).dt.date
    df = df.merge(iqar_medio.rename(columns={"dt_particao": "dt_particao_str"}),
                  on="dt_particao_str", how="left")

    # 5. Codificação numérica das categorias
    cat_map_l1 = {c: i for i, c in enumerate(df["categoria_l1"].unique())}
    df["categoria_l1_num"] = df["categoria_l1"].map(cat_map_l1)

    # 6. Seleciona colunas para o modelo
    df_gold = df[[
        "id", "lat", "lon", "geohash",
        "categoria_l1", "categoria_l2", "categoria_l1_num",
        "prioridade", "hora_abertura", "dia_semana",
        "iqar_medio_dia", "bairro",
    ]].fillna({"iqar_medio_dia": 50.0})

    log.info("Gold mapa de ocorrências: %d registros", len(df_gold))
    log.info("  Categorias L1: %s", sorted(df_gold.categoria_l1.unique()))
    return df_gold
