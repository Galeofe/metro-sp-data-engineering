"""
Ingestion — API Meteorológica INMET
Simula resposta da API REST do INMET onde todos os campos numéricos chegam
como strings e valores ausentes são representados pela string "null".
"""
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from config.settings import ESTACAO_INMET, N_WEATHER_HOURS, RANDOM_SEED
from utils.logger import get_logger

log = get_logger("ingestion.weather_inmet")
rng = np.random.default_rng(RANDOM_SEED + 4)


def generate() -> pd.DataFrame:
    base = datetime(2026, 6, 11, 0, 0, 0)
    records = []

    for h in range(N_WEATHER_HOURS):
        dt   = base + timedelta(hours=h)
        hora = dt.hour
        temp = 19.0 + 5.0 * np.sin(hora * np.pi / 12.0) + float(rng.normal(0, 1.5))
        umid = float(np.clip(rng.normal(70.0, 10.0), 20, 100))
        chuva_day = dt.day in (13, 14, 17)
        chuva = float(rng.exponential(4.0)) if (chuva_day and 14 <= hora <= 19) else 0.0
        press = float(rng.normal(931.5, 3.0))
        vento = float(rng.exponential(3.5))
        vdir  = float(rng.uniform(0, 360))
        rad   = max(0.0, 800.0 * np.sin(hora * np.pi / 12.0) + float(rng.normal(0, 50)))

        def sv(v, null_prob=0.03):
            """Serializa como string, com chance de ser 'null' (bug da API)."""
            if rng.random() < null_prob:
                return "null"
            return str(round(v, 1))

        records.append({
            "DT_MEDICAO":             dt.strftime("%Y-%m-%d"),
            "HR_MEDICAO":             dt.strftime("%H00"),
            "CD_ESTACAO":             ESTACAO_INMET,
            "VL_TEMPERATURA":         sv(temp),
            "VL_TEMPERATURA_MAX":     sv(temp + float(rng.uniform(0, 3))),
            "VL_TEMPERATURA_MIN":     sv(temp - float(rng.uniform(0, 3))),
            "VL_UMIDADE_REL_AR":      sv(umid),
            "VL_PRESSAO_ATM_EST":     sv(press),
            "VL_VENTO_VELOCIDADE":    sv(vento),
            "VL_VENTO_DIRECAO":       sv(vdir),
            "VL_PRECIPITACAO_TOTAL":  sv(chuva, null_prob=0.01),
            "VL_RADIACAO_GLOBAL":     sv(rad, null_prob=0.05),
            "CD_SITUACAO":            "Operante",
        })

    df = pd.DataFrame(records)
    log.info("Gerados %d registros meteorológicos INMET (Bronze)", len(df))
    log.info("  Campos com valor 'null' (string): %d",
             (df == "null").sum().sum())
    return df
