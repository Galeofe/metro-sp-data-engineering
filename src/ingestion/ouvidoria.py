"""
Ingestion — Ouvidoria Municipal (CDC via Debezium)
Simula registros extraídos de PostgreSQL com CDC. Inclui PII em texto livre
(CPF, telefone), abreviações inconsistentes de logradouro, status em PT/EN
misturados e ~12% dos registros sem coordenadas geográficas.
"""
import re
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from config.settings import BAIRROS, CATEGORIAS_OUVIDORIA, N_OUVIDORIA, RANDOM_SEED
from utils.logger import get_logger

log = get_logger("ingestion.ouvidoria")
rng = np.random.default_rng(RANDOM_SEED + 3)

_ABREVS = ["R.", "Rua", "RUA", "rua", "Av.", "AV.", "Avenida"]

_TEMPLATES = [
    "Poste apagado na {rua} {num} há {dias} dias. Perigoso à noite.",
    "Buraco enorme na {rua} {num} sentido {bairro}. Danifiquei meu carro. CPF: {cpf}",
    "Lixo acumulado há {dias} dias na calçada {rua} {num}. Tel: {tel}",
    "Ônibus linha {linha} atrasado toda manhã. Impossível chegar ao trabalho.",
    "Barulho excessivo no estabelecimento da {rua} {num} até 3h da manhã.",
    "Árvore caída bloqueando a {rua} próximo ao {num}. Situação de risco!",
    "Bueiro entupido na {rua} {num}. Causa alagamento em dias de chuva.",
    "Calçada destruída na {rua} {num}. Idosos e cadeirantes em perigo.",
]

_STATUS_POOL  = ["ABERTA", "EM_ANDAMENTO", "FECHADA", "OPEN", "CLOSED"]
_STATUS_PROBS = [0.35, 0.18, 0.32, 0.08, 0.07]


def _cpf():
    d = rng.integers(0, 10, 9)
    return f"{''.join(map(str,d[:3]))}.{''.join(map(str,d[3:6]))}.{''.join(map(str,d[6:9]))}-{int(rng.integers(10,99))}"


def _tel():
    return f"({int(rng.integers(11,99))}) 9{int(rng.integers(1000,9999))}-{int(rng.integers(1000,9999))}"


def generate() -> pd.DataFrame:
    base = datetime(2026, 6, 15, 0, 0, 0)
    records = []

    for i in range(N_OUVIDORIA):
        bairro_info = BAIRROS[i % len(BAIRROS)]
        categoria   = CATEGORIAS_OUVIDORIA[i % len(CATEGORIAS_OUVIDORIA)]
        abrev       = _ABREVS[i % len(_ABREVS)]
        num         = int(rng.integers(10, 2000))
        dias        = int(rng.integers(1, 30))
        linha_bus   = rng.choice(["875P", "702U", "5100", "8000"])

        tmpl    = _TEMPLATES[i % len(_TEMPLATES)]
        descricao = tmpl.format(
            rua=f"{abrev} das Flores",
            num=num,
            dias=dias,
            bairro=bairro_info["nome"],
            cpf=_cpf(),
            tel=_tel(),
            linha=linha_bus,
        )

        dt_ab = base + timedelta(
            days=int(rng.integers(0, 4)),
            hours=int(rng.integers(6, 22)),
            minutes=int(rng.integers(0, 60)),
        )

        has_coords = rng.random() > 0.12  # ~12% sem coordenadas
        lat = round(bairro_info["lat"] + float(rng.normal(0, 0.008)), 6) if has_coords else None
        lon = round(bairro_info["lon"] + float(rng.normal(0, 0.008)), 6) if has_coords else None

        records.append({
            "id":             845900 + i,
            "protocolo":      f"2026-{dt_ab.strftime('%m%d')}-{dt_ab.strftime('%H%M%S')}-{i:04d}",
            "dt_abertura":    dt_ab.isoformat(),
            "dt_fechamento":  None if rng.random() > 0.55
                              else (dt_ab + timedelta(days=int(rng.integers(1, 10)))).isoformat(),
            "categoria":      categoria,
            "descricao_livre": descricao,
            "logradouro":     f"{abrev} das Flores, {num}",
            "bairro":         bairro_info["nome"],
            "cep":            f"{int(rng.integers(1000,9999)):04d}{int(rng.integers(100,999)):03d}",
            "lat":            lat,
            "lon":            lon,
            "status":         str(rng.choice(_STATUS_POOL, p=_STATUS_PROBS)),
            "prioridade":     int(rng.integers(1, 6)),
            "origem":         str(rng.choice(["APP", "PORTAL", "156"], p=[0.50, 0.30, 0.20])),
            "_ingested_at":   datetime.utcnow().isoformat() + "Z",
            "_source_system": "ouvidoria_db_cdc",
        })

    df = pd.DataFrame(records)
    log.info("Gerados %d registros de ouvidoria (Bronze)", len(df))
    log.info("  Sem coordenadas: %d (%.1f%%)",
             df.lat.isna().sum(), df.lat.isna().mean() * 100)
    log.info("  Status inconsistentes (OPEN/CLOSED): %d",
             df.status.isin(["OPEN", "CLOSED"]).sum())
    log.info("  Registros com PII (CPF/tel) no texto: %d",
             df.descricao_livre.str.contains(r"CPF:|Tel:", case=False).sum())
    return df
