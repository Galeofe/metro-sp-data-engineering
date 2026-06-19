"""
Ingestion — IoT Sensores de Tráfego (CET-SP)
Simula payloads MQTT de laços de indução e câmeras com visão computacional.
Introduz problemas reais: timestamps BRT sem aviso, contagem -1 (manutenção),
velocidade nula quando sem veículos.
"""
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

from config.settings import VIAS, N_TRAFFIC_RECORDS, RANDOM_SEED
from utils.logger import get_logger

log = get_logger("ingestion.iot_traffic")
rng = np.random.default_rng(RANDOM_SEED)


def generate() -> pd.DataFrame:
    records = []
    base = datetime(2026, 6, 19, 6, 0, 0, tzinfo=timezone.utc)

    for i in range(N_TRAFFIC_RECORDS):
        via = VIAS[i % len(VIAS)]
        ts  = base + timedelta(seconds=i * 30)

        hora         = ts.hour
        fator_pico   = 1 + 1.5 * (
            np.exp(-((hora - 8) ** 2) / 4.0) +
            np.exp(-((hora - 18) ** 2) / 5.0)
        )
        contagem     = int(rng.poisson(28 * fator_pico))
        velocidade   = float(rng.normal(48.0 / fator_pico, 8.0))
        velocidade   = max(4.0, velocidade)
        ocupacao     = float(np.clip(rng.normal(38.0 * fator_pico, 10.0), 0, 100))

        # Bug 1: sensor em manutenção (~5%)
        em_manutencao = rng.random() < 0.05
        if em_manutencao:
            contagem  = -1
            velocidade = None
            ocupacao   = None

        # Bug 2: velocidade nula quando nenhum veículo passou
        elif contagem == 0:
            velocidade = None

        # Bug 3: ~2% enviam timestamp em BRT (UTC-3) sem identificação de fuso
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}"
        if rng.random() < 0.02:
            ts_local = ts - timedelta(hours=3)
            ts_str = ts_local.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts_local.microsecond // 1000:03d}"
        else:
            ts_str += "Z"

        n_car = int(contagem * 0.80) if contagem > 0 else 0
        n_mot = int(contagem * 0.13) if contagem > 0 else 0
        n_oni = max(0, contagem - n_car - n_mot) if contagem > 0 else 0

        records.append({
            "sensor_id":             f"CET-SP-{(800 + i % 200):04d}",
            "lat":                   round(via["lat"] + float(rng.normal(0, 0.001)), 6),
            "lon":                   round(via["lon"] + float(rng.normal(0, 0.001)), 6),
            "timestamp_raw":         ts_str,
            "via":                   via["via"],
            "sentido":               via["sentido"],
            "contagem_veiculos":     contagem,
            "velocidade_media_kmh":  round(velocidade, 1) if velocidade is not None else None,
            "ocupacao_pct":          round(ocupacao, 1) if ocupacao is not None else None,
            "n_carros":              n_car,
            "n_motos":               n_mot,
            "n_onibus":              n_oni,
            "firmware_version":      "2.1.4",
            "bateria_pct":           int(rng.integers(60, 100)),
            "_ingested_at":          datetime.utcnow().isoformat() + "Z",
            "_source_system":        "iot_traffic_cet",
        })

    df = pd.DataFrame(records)
    log.info("Gerados %d registros de sensores de tráfego (Bronze)", len(df))
    log.info("  Sensores em manutenção (contagem=-1): %d", (df.contagem_veiculos == -1).sum())
    log.info("  Velocidade nula (sem veículos):       %d", df.velocidade_media_kmh.isna().sum())
    return df
