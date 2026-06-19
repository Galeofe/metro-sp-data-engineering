"""
Ingestion — GPS de Frota de Ônibus (SPTrans)
Simula payloads WebSocket com UNIX epoch sem fuso, lotação com valores
inconsistentes PT/EN, coordenadas 0,0 para veículos fora de serviço
e motorista_id como PII sujeito à LGPD.
"""
from datetime import datetime, timezone
import numpy as np
import pandas as pd

from config.settings import LINHAS_ONIBUS, N_GPS_RECORDS, RANDOM_SEED
from utils.logger import get_logger

log = get_logger("ingestion.gps_bus")
rng = np.random.default_rng(RANDOM_SEED + 2)

_LOTACAO_POOL = ["VAZIA", "MEIA", "MEIA_LOTACAO", "CHEIA", "CHEIO", "LOTADA", "FULL"]
_LOTACAO_PROBS = [0.10, 0.20, 0.05, 0.28, 0.12, 0.15, 0.10]


def generate() -> pd.DataFrame:
    # Espalha 400 registros ao longo de 48h (~7 min entre eventos) para gerar
    # dados suficientes para lags de 1h e 24h no dataset Gold.
    base_ts = int(datetime(2026, 6, 17, 7, 0, 0, tzinfo=timezone.utc).timestamp())
    records = []

    for i in range(N_GPS_RECORDS):
        linha = LINHAS_ONIBUS[i % len(LINHAS_ONIBUS)]
        ts    = base_ts + i * 432  # 432s = 7.2 min → 400 registros ≈ 48h

        lat = round(-23.56 + float(rng.normal(0, 0.05)), 4 + int(rng.integers(0, 3)))
        lon = round(-46.65 + float(rng.normal(0, 0.05)), 4 + int(rng.integers(0, 3)))

        # Bug: veículos fora de serviço reportam (0, 0) — linha do Equador/Meridiano
        if rng.random() < 0.03:
            lat, lon = 0.0, 0.0

        lotacao     = str(rng.choice(_LOTACAO_POOL, p=_LOTACAO_PROBS))
        motorista   = f"MTR-{int(rng.integers(100, 999)):05d}"  # PII — LGPD Art. 5

        records.append({
            "prefixo":        f"2-{int(rng.integers(80000, 99999))}",
            "linha":          linha["id"],
            "lat":            lat,
            "lon":            lon,
            "timestamp":      ts,           # UNIX epoch — sem timezone explícito
            "velocidade":     int(rng.integers(0, 60)),
            "sentido":        int(rng.integers(0, 2)),
            "acessibilidade": bool(rng.random() < 0.72),
            "lotacao":        lotacao,       # enum inconsistente PT/EN
            "ar_condicionado": bool(rng.random() < 0.85),
            "motorista_id":   motorista,    # PII — deve ser anonimizado na Silver
            "_ingested_at":   datetime.utcnow().isoformat() + "Z",
            "_source_system": "gps_bus_sptrans",
        })

    df = pd.DataFrame(records)
    log.info("Gerados %d registros GPS de ônibus (Bronze)", len(df))
    log.info("  Coordenadas 0,0 (fora de serviço): %d", ((df.lat == 0) & (df.lon == 0)).sum())
    log.info("  Valores únicos de lotação: %s", sorted(df.lotacao.unique()))
    return df
