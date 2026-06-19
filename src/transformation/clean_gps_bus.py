"""
Silver — Limpeza do GPS de Ônibus (SPTrans)
- Converte UNIX epoch para timestamp UTC
- Normaliza enum de lotação (PT/EN → {VAZIA, MEIA, CHEIA, LOTADA})
- Filtra coordenadas 0,0 (veículos fora de serviço)
- Anonimiza motorista_id via SHA-256 + salt (LGPD Art. 5)
- Padroniza coordenadas para 5 casas decimais (~1.1m)
"""
import hashlib
import pandas as pd
from utils.logger import get_logger

log = get_logger("silver.gps_bus")

_SALT = "metropole-sp-salt-2026"

_LOTACAO_MAP = {
    "VAZIA":       "VAZIA",
    "MEIA":        "MEIA",
    "MEIA_LOTACAO":"MEIA",
    "CHEIA":       "CHEIA",
    "CHEIO":       "CHEIA",
    "LOTADA":      "LOTADA",
    "FULL":        "LOTADA",
}


def _hash_id(valor: str) -> str:
    return hashlib.sha256(f"{_SALT}:{valor}".encode()).hexdigest()[:16]


def transform(df_bronze: pd.DataFrame) -> pd.DataFrame:
    df = df_bronze.copy()

    # 1. UNIX epoch → UTC timestamp
    df["timestamp_utc"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df = df.drop(columns=["timestamp"])

    # 2. Marca veículos fora de serviço e remove suas coordenadas
    fora = (df["lat"] == 0.0) & (df["lon"] == 0.0)
    df["ativo"] = ~fora
    df.loc[fora, ["lat", "lon"]] = None

    # 3. Normaliza enum de lotação
    df["lotacao"] = df["lotacao"].map(_LOTACAO_MAP).fillna("DESCONHECIDA")

    # 4. Padroniza precisão de coordenadas
    df["lat"] = df["lat"].round(5)
    df["lon"] = df["lon"].round(5)

    # 5. Anonimiza motorista (LGPD) — hash SHA-256 irreversível com salt
    df["motorista_hash"] = df["motorista_id"].apply(_hash_id)
    df = df.drop(columns=["motorista_id", "_ingested_at", "_source_system"], errors="ignore")

    df["dt_particao"] = df["timestamp_utc"].dt.date

    log.info("Silver GPS ônibus: %d registros", len(df))
    log.info("  Veículos ativos:     %d", df.ativo.sum())
    log.info("  Fora de serviço:     %d", (~df.ativo).sum())
    log.info("  Lotação normalizada: %s", sorted(df.lotacao.unique()))
    return df
