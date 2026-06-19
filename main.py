"""
Pipeline de Engenharia de Dados — Cidades Inteligentes
Metrópole SP Data Platform

Execução:
    python main.py

Produz:
    data/bronze/   — Parquets com dados brutos por fonte
    data/silver/   — Parquets limpos e padronizados
    data/gold/     — Parquets com features para ML
    reports/       — 8 gráficos PNG + resumo de métricas no console
"""
import sys
import time
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# Garante que src/ e raiz estejam no path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import BRONZE_DIR, SILVER_DIR, GOLD_DIR, REPORTS_DIR
from utils.logger import get_logger
from utils.io_helpers import write_parquet, write_parquet_partitioned

log = get_logger("main")

# ── Log em arquivo (lido pelo dashboard em tempo real) ───────────────────────
_BASE = Path(__file__).parent
LOG_DIR = _BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)
PIPELINE_LOG = LOG_DIR / "pipeline.log"
PIPELINE_STATUS = LOG_DIR / "pipeline_status.json"

def _plog(msg: str):
    """Escreve linha timestampada no log do pipeline e no stdout."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(PIPELINE_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Imports do pipeline ──────────────────────────────────────────────────────
from src.ingestion       import iot_traffic, air_quality, gps_bus, ouvidoria, weather_inmet
from src.transformation  import (clean_traffic, clean_air_quality,
                                  clean_gps_bus, clean_ouvidoria, clean_weather)
from src.feature_engineering import (gold_air_quality, gold_bus_demand,
                                      gold_occurrence_map)
from src.quality.data_quality import (
    validate_silver_traffic, validate_silver_air,
    validate_silver_gps,    validate_silver_ouvidoria,
    print_report,
)
from src.models          import isolation_forest, xgboost_demand, dbscan_risk
from src.visualization   import (plot_pipeline, plot_air_quality,
                                   plot_transport, plot_risk_map)


def banner(titulo: str):
    largura = 70
    print()
    print("=" * largura)
    print(f"  {titulo}")
    print("=" * largura)


def main():
    import json
    t0 = time.time()

    # Inicializa arquivo de log limpo para esta execução
    PIPELINE_LOG.write_text(f"[{datetime.now().strftime('%H:%M:%S')}] PIPELINE INICIADO\n",
                            encoding="utf-8")
    PIPELINE_STATUS.write_text(json.dumps({"status": "running", "started": datetime.now().isoformat()}),
                               encoding="utf-8")

    # ────────────────────────────────────────────────────────────────────────
    # ETAPA 1 — BRONZE: Ingestão dos dados brutos
    # ────────────────────────────────────────────────────────────────────────
    _plog("ETAPA 1/6 — BRONZE: Ingestão Bruta")

    df_traffic_b  = iot_traffic.generate()
    _plog(f"  IoT Tráfego     → {len(df_traffic_b):,} registros")
    df_ar_b       = air_quality.generate()
    _plog(f"  Qualidade do Ar → {len(df_ar_b):,} registros")
    df_gps_b      = gps_bus.generate()
    _plog(f"  GPS Ônibus      → {len(df_gps_b):,} registros")
    df_ouvidoria_b= ouvidoria.generate()
    _plog(f"  Ouvidoria       → {len(df_ouvidoria_b):,} registros")
    df_weather_b  = weather_inmet.generate()
    _plog(f"  Meteorologia    → {len(df_weather_b):,} registros")

    write_parquet(df_traffic_b,   BRONZE_DIR / "iot_traffic_raw.parquet")
    write_parquet(df_ar_b,        BRONZE_DIR / "air_quality_raw.parquet")
    write_parquet(df_gps_b,       BRONZE_DIR / "gps_bus_raw.parquet")
    write_parquet(df_ouvidoria_b, BRONZE_DIR / "ouvidoria_cdc_raw.parquet")
    write_parquet(df_weather_b,   BRONZE_DIR / "weather_inmet_raw.parquet")

    # Escrita particionada para os dois datasets de maior volume
    # GPS → particionado por região (push-down filtra toda uma região de uma vez)
    if "regiao" in df_gps_b.columns:
        write_parquet_partitioned(df_gps_b,
                                  BRONZE_DIR / "gps_bus_partitioned",
                                  partition_cols=["regiao"])
    # IoT Tráfego → particionado por tipo_via
    if "tipo_via" in df_traffic_b.columns:
        write_parquet_partitioned(df_traffic_b,
                                  BRONZE_DIR / "iot_traffic_partitioned",
                                  partition_cols=["tipo_via"])
    _plog("  Bronze salvo em data/bronze/  [OK]  (+ particionado por regiao/tipo_via)")

    volumes = {
        "IoT Tráfego":    {"bronze": len(df_traffic_b)},
        "Qualidade do Ar":{"bronze": len(df_ar_b)},
        "GPS Ônibus":     {"bronze": len(df_gps_b)},
        "Ouvidoria":      {"bronze": len(df_ouvidoria_b)},
        "Meteorologia":   {"bronze": len(df_weather_b)},
    }

    # ────────────────────────────────────────────────────────────────────────
    # ETAPA 2 — SILVER: Limpeza e Padronização
    # ────────────────────────────────────────────────────────────────────────
    _plog("ETAPA 2/6 — SILVER: Limpeza e Padronização")

    df_traffic_s   = clean_traffic.transform(df_traffic_b)
    _plog(f"  IoT Tráfego     → {len(df_traffic_s):,} registros limpos")
    df_ar_s        = clean_air_quality.transform(df_ar_b)
    _plog(f"  Qualidade do Ar → {len(df_ar_s):,} registros limpos")
    df_gps_s       = clean_gps_bus.transform(df_gps_b)
    _plog(f"  GPS Ônibus      → {len(df_gps_s):,} registros limpos  (PII anonimizado)")
    df_ouvidoria_s = clean_ouvidoria.transform(df_ouvidoria_b)
    _plog(f"  Ouvidoria       → {len(df_ouvidoria_s):,} registros limpos")
    df_weather_s   = clean_weather.transform(df_weather_b)
    _plog(f"  Meteorologia    → {len(df_weather_s):,} registros limpos")

    write_parquet(df_traffic_s,   SILVER_DIR / "iot_traffic_clean.parquet")
    write_parquet(df_ar_s,        SILVER_DIR / "air_quality_clean.parquet")
    write_parquet(df_gps_s,       SILVER_DIR / "gps_bus_clean.parquet")
    write_parquet(df_ouvidoria_s, SILVER_DIR / "ouvidoria_clean.parquet")
    write_parquet(df_weather_s,   SILVER_DIR / "weather_clean.parquet")
    _plog("  Silver salvo em data/silver/  [OK]")

    for fonte, v in zip(["IoT Tráfego", "Qualidade do Ar", "GPS Ônibus", "Ouvidoria", "Meteorologia"],
                        [df_traffic_s, df_ar_s, df_gps_s, df_ouvidoria_s, df_weather_s]):
        volumes[fonte]["silver"] = len(v)

    # ────────────────────────────────────────────────────────────────────────
    # ETAPA 3 — VALIDAÇÃO DE QUALIDADE
    # ────────────────────────────────────────────────────────────────────────
    _plog("ETAPA 3/6 — QUALIDADE DE DADOS (validação Silver)")

    resultados_qualidade = [
        validate_silver_traffic(df_traffic_s),
        validate_silver_air(df_ar_s),
        validate_silver_gps(df_gps_s),
        validate_silver_ouvidoria(df_ouvidoria_s),
    ]
    for r in resultados_qualidade:
        score = r.get("score", 0)
        nome  = r.get("tabela", "?")
        _plog(f"  {nome:<25} score={score:.1%}")
    print_report(resultados_qualidade)

    # ────────────────────────────────────────────────────────────────────────
    # ETAPA 4 — GOLD: Feature Engineering
    # ────────────────────────────────────────────────────────────────────────
    _plog("ETAPA 4/6 — GOLD: Feature Engineering")

    df_gold_ar   = gold_air_quality.build(df_ar_s, df_weather_s)
    _plog(f"  gold_air_quality    → {len(df_gold_ar):,} linhas, {df_gold_ar.shape[1]} colunas")
    df_gold_bus  = gold_bus_demand.build(df_gps_s, df_weather_s)
    _plog(f"  gold_bus_demand     → {len(df_gold_bus):,} linhas, {df_gold_bus.shape[1]} colunas")
    df_gold_risk = gold_occurrence_map.build(df_ouvidoria_s, df_ar_s)
    _plog(f"  gold_occurrence_map → {len(df_gold_risk):,} linhas, {df_gold_risk.shape[1]} colunas")

    write_parquet(df_gold_ar,   GOLD_DIR / "air_quality_anomaly.parquet")
    write_parquet(df_gold_bus,  GOLD_DIR / "bus_demand_forecast.parquet")
    write_parquet(df_gold_risk, GOLD_DIR / "occurrence_heatmap.parquet")

    # Gold particionado por categoria de IQAr — permite push-down por severidade
    if "iqar_categoria" in df_gold_ar.columns:
        write_parquet_partitioned(df_gold_ar,
                                  GOLD_DIR / "air_quality_partitioned",
                                  partition_cols=["iqar_categoria"])
    # Gold bus particionado por dia_semana — treino/inferência por período
    if "dia_semana" in df_gold_bus.columns:
        write_parquet_partitioned(df_gold_bus,
                                  GOLD_DIR / "bus_demand_partitioned",
                                  partition_cols=["dia_semana"])
    _plog("  Gold salvo em data/gold/  [OK]  (+ particionado por iqar_categoria/dia_semana)")

    volumes["Qualidade do Ar"]["gold"] = len(df_gold_ar)
    volumes["GPS Ônibus"]["gold"]      = len(df_gold_bus)
    volumes["Ouvidoria"]["gold"]       = len(df_gold_risk)

    # ────────────────────────────────────────────────────────────────────────
    # ETAPA 5 — MODELOS DE IA
    # ────────────────────────────────────────────────────────────────────────
    _plog("ETAPA 5/6 — MODELOS DE IA")

    _plog("  Treinando Isolation Forest (anomalias de ar)...")
    df_gold_ar, metricas_iso = isolation_forest.train_and_predict(df_gold_ar)
    write_parquet(df_gold_ar, GOLD_DIR / "air_quality_with_anomalies.parquet")
    n_anom = int(df_gold_ar["anomalia_pred"].sum()) if "anomalia_pred" in df_gold_ar.columns else 0
    _plog(f"  Isolation Forest    → {n_anom} anomalias detectadas  [OK]")

    _plog("  Treinando XGBoost (previsao de demanda)...")
    modelo_xgb, result_xgb, metricas_xgb = xgboost_demand.train_and_evaluate(df_gold_bus)
    _plog(f"  XGBoost             → MAE={metricas_xgb['mae']:.4f}  R²={metricas_xgb['r2']:.3f}  [OK]")

    _plog("  Executando DBSCAN (mapa de risco)...")
    df_gold_risk, df_clusters = dbscan_risk.cluster(df_gold_risk)
    write_parquet(df_gold_risk, GOLD_DIR / "occurrence_clusters.parquet")
    if not df_clusters.empty:
        write_parquet(df_clusters, GOLD_DIR / "risk_clusters_summary.parquet")
    _plog(f"  DBSCAN              → {len(df_clusters)} clusters identificados  [OK]")

    # ────────────────────────────────────────────────────────────────────────
    # ETAPA 6 — VISUALIZAÇÕES
    # ────────────────────────────────────────────────────────────────────────
    _plog("ETAPA 6/6 — VISUALIZACOES (gerando 8 graficos PNG)")

    plot_pipeline.plot_volumes(volumes, REPORTS_DIR)
    plot_pipeline.plot_quality_heatmap(resultados_qualidade, REPORTS_DIR)
    plot_air_quality.plot_iqar_timeseries(df_ar_s, REPORTS_DIR)
    plot_air_quality.plot_anomalias(df_gold_ar, REPORTS_DIR)
    plot_transport.plot_demand_prediction(result_xgb, metricas_xgb, REPORTS_DIR)
    plot_transport.plot_lotacao_distribution(df_gps_s, REPORTS_DIR)
    plot_risk_map.plot_clusters(df_gold_risk, df_clusters, REPORTS_DIR)
    plot_risk_map.plot_ocorrencias_bairro(df_gold_risk, REPORTS_DIR)
    _plog("  Graficos salvos em reports/  [OK]")

    # ────────────────────────────────────────────────────────────────────────
    # RESUMO FINAL
    # ────────────────────────────────────────────────────────────────────────
    t1 = time.time()
    elapsed = round(t1 - t0, 1)
    _plog(f"PIPELINE CONCLUIDO em {elapsed}s")
    _plog(f"  Bronze: {sum(v.get('bronze',0) for v in volumes.values()):,} registros")
    _plog(f"  Silver: {sum(v.get('silver',0) for v in volumes.values()):,} registros")
    _plog(f"  Gold:   {sum(v.get('gold',0)   for v in volumes.values()):,} registros")

    PIPELINE_STATUS.write_text(
        json.dumps({
            "status": "done",
            "started": PIPELINE_STATUS.read_text(),
            "finished": datetime.now().isoformat(),
            "elapsed": elapsed,
            "anomalias": n_anom,
            "mae": round(metricas_xgb["mae"], 4),
            "r2":  round(metricas_xgb["r2"],  3),
            "clusters": len(df_clusters),
        }),
        encoding="utf-8")

    print(f"\n  {'Fonte':<20} {'Bronze':>8} {'Silver':>8} {'Gold':>8}")
    print(f"  {'-'*46}")
    total_b = total_s = total_g = 0
    for fonte, v in volumes.items():
        b = v.get("bronze", 0)
        s = v.get("silver", 0)
        g = v.get("gold", 0)
        total_b += b; total_s += s; total_g += g
        print(f"  {fonte:<20} {b:>8,} {s:>8,} {g:>8,}")
    print(f"  {'-'*46}")
    print(f"  {'TOTAL':<20} {total_b:>8,} {total_s:>8,} {total_g:>8,}")
    print(f"\n  Tempo total: {elapsed}s")
    print()


if __name__ == "__main__":
    main()
