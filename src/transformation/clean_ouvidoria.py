"""
Silver — Limpeza da Ouvidoria Municipal
- Remove PII do texto livre via regex (CPF, telefone) — LGPD
- Normaliza abreviações de logradouro
- Padroniza status PT/EN
- Geocodifica registros sem coordenadas (simula Nominatim)
"""
import re
import pandas as pd
import numpy as np
from utils.logger import get_logger
from config.settings import BAIRROS, RANDOM_SEED

log  = get_logger("silver.ouvidoria")
rng  = np.random.default_rng(RANDOM_SEED + 5)

_STATUS_MAP = {
    "ABERTA": "ABERTA", "EM_ANDAMENTO": "EM_ANDAMENTO",
    "FECHADA": "FECHADA", "OPEN": "ABERTA", "CLOSED": "FECHADA",
}

_PII_PATTERNS = [
    (r"\d{3}\.\d{3}\.\d{3}-\d{2}", "[CPF_REMOVIDO]"),
    (r"\(?\d{2}\)?\s?9?\d{4}[\s\-]\d{4}", "[TEL_REMOVIDO]"),
    (r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_REMOVIDO]"),
]

_ABREV_NORM = [
    (r"^R\.\s",    "Rua "),
    (r"^r\.\s",    "Rua "),
    (r"^RUA\s",    "Rua "),
    (r"^rua\s",    "Rua "),
    (r"^Av\.\s",   "Avenida "),
    (r"^AV\.\s",   "Avenida "),
    (r"^Al\.\s",   "Alameda "),
    (r"^Pç\.\s",   "Praça "),
]

_BAIRRO_COORDS = {b["nome"]: (b["lat"], b["lon"]) for b in BAIRROS}


def _remover_pii(texto: str) -> str:
    if pd.isna(texto):
        return texto
    for pattern, replacement in _PII_PATTERNS:
        texto = re.sub(pattern, replacement, texto)
    return texto


def _normalizar_logradouro(logradouro: str) -> str:
    if pd.isna(logradouro):
        return logradouro
    for pattern, replacement in _ABREV_NORM:
        logradouro = re.sub(pattern, replacement, logradouro)
    return logradouro


def _geocodificar(row: pd.Series) -> tuple:
    """Simula geocodificação via Nominatim usando o centroide do bairro + jitter."""
    coords = _BAIRRO_COORDS.get(row["bairro"], (-23.5505, -46.6333))
    lat = coords[0] + float(rng.normal(0, 0.005))
    lon = coords[1] + float(rng.normal(0, 0.005))
    return round(lat, 6), round(lon, 6)


def transform(df_bronze: pd.DataFrame) -> pd.DataFrame:
    df = df_bronze.copy()

    # 1. Remove PII do texto livre (LGPD)
    antes_pii = df["descricao_livre"].str.contains(r"CPF:|Tel:", case=False, na=False).sum()
    df["descricao_anonimizada"] = df["descricao_livre"].apply(_remover_pii)
    df = df.drop(columns=["descricao_livre"])

    # 2. Normaliza abreviações de logradouro
    df["logradouro"] = df["logradouro"].apply(_normalizar_logradouro)

    # 3. Padroniza status (PT/EN → PT)
    df["status"] = df["status"].map(_STATUS_MAP).fillna(df["status"])

    # 4. Converte datas
    df["dt_abertura"]   = pd.to_datetime(df["dt_abertura"],   utc=True)
    df["dt_fechamento"] = pd.to_datetime(df["dt_fechamento"], utc=True, errors="coerce")

    # 5. Geocodifica registros sem coordenadas
    sem_coord = df["lat"].isna()
    for idx in df[sem_coord].index:
        df.at[idx, "lat"], df.at[idx, "lon"] = _geocodificar(df.loc[idx])
    df["coord_geocodificada"] = sem_coord

    df = df.drop(columns=["_ingested_at", "_source_system"], errors="ignore")
    df["dt_particao"] = df["dt_abertura"].dt.date

    log.info("Silver ouvidoria: %d registros", len(df))
    log.info("  PII removido de %d textos", antes_pii)
    log.info("  Geocodificados:  %d registros", sem_coord.sum())
    log.info("  Status únicos:   %s", sorted(df.status.unique()))
    return df
