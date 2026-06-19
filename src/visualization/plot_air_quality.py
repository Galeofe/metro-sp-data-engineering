"""
Visualização — Qualidade do Ar: série temporal IQAr e anomalias detectadas.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from utils.logger import get_logger

log = get_logger("viz.air_quality")

_FAIXA_CORES = {
    "BOA":        "#4CAF50",
    "MODERADA":   "#8BC34A",
    "RUIM":       "#FFC107",
    "MUITO_RUIM": "#FF5722",
    "PESSIMA":    "#F44336",
    "INDISPONIVEL":"#9E9E9E",
}


def plot_iqar_timeseries(df_silver: pd.DataFrame, output_dir: Path):
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle("Qualidade do Ar — Série Temporal IQAr", fontsize=13, fontweight="bold")

    # Agrega média horária
    df = df_silver.copy()
    df["hora"] = pd.to_datetime(df["timestamp_utc"]).dt.floor("h")
    agg = df.groupby("hora")["iqar"].agg(["mean", "max", "min"]).reset_index()
    agg.columns = ["hora", "iqar_mean", "iqar_max", "iqar_min"]

    ax1 = axes[0]
    ax1.fill_between(agg["hora"], agg["iqar_min"], agg["iqar_max"],
                     alpha=0.15, color="#9C27B0", label="Min-Max")
    ax1.plot(agg["hora"], agg["iqar_mean"], color="#9C27B0", linewidth=1.5, label="Média")
    ax1.axhline(80,  color="orange", linestyle="--", linewidth=1, label="Limite RUIM (80)")
    ax1.axhline(120, color="red",    linestyle="--", linewidth=1, label="Limite MUITO_RUIM (120)")
    ax1.set_ylabel("IQAr")
    ax1.set_title("IQAr Médio Horário — Todas as Estações")
    ax1.legend(fontsize=8)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%Hh"))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=8))
    ax1.grid(alpha=0.3)

    # Heatmap por estação × hora
    df["hora_num"] = pd.to_datetime(df["timestamp_utc"]).dt.hour
    pivot = df.pivot_table(values="iqar", index="estacao_id", columns="hora_num",
                           aggfunc="mean")
    ax2 = axes[1]
    sns.heatmap(pivot, ax=ax2, cmap="RdYlGn_r", vmin=0, vmax=120,
                linewidths=0.3, cbar_kws={"label": "IQAr médio"})
    ax2.set_title("IQAr por Estação × Hora do Dia")
    ax2.set_xlabel("Hora do dia (UTC)")
    ax2.set_ylabel("Estação")

    plt.tight_layout()
    path = output_dir / "03_iqar_timeseries.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    log.info("Salvo: %s", path.name)


def plot_anomalias(df_gold: pd.DataFrame, output_dir: Path):
    if "anomalia_pred" not in df_gold.columns:
        return

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Detecção de Anomalias — Isolation Forest", fontsize=13, fontweight="bold")

    # Scatter: score × IQAr
    ax1 = axes[0]
    cores = df_gold["anomalia_pred"].map({0: "#2196F3", 1: "#F44336"})
    ax1.scatter(
        df_gold.get("iqar", df_gold.index),
        df_gold["anomaly_score"],
        c=cores, alpha=0.5, s=15, edgecolors="none",
    )
    ax1.set_xlabel("IQAr")
    ax1.set_ylabel("Anomaly Score (menor = mais anômalo)")
    ax1.set_title("Score vs IQAr")
    from matplotlib.patches import Patch
    ax1.legend(handles=[
        Patch(color="#2196F3", label="Normal"),
        Patch(color="#F44336", label="Anomalia"),
    ], fontsize=9)
    ax1.grid(alpha=0.3)

    # Distribuição dos scores
    ax2 = axes[1]
    norm = df_gold[df_gold["anomalia_pred"] == 0]["anomaly_score"].dropna()
    anom = df_gold[df_gold["anomalia_pred"] == 1]["anomaly_score"].dropna()
    ax2.hist(norm, bins=30, color="#2196F3", alpha=0.6, label=f"Normal ({len(norm)})")
    ax2.hist(anom, bins=15, color="#F44336", alpha=0.7, label=f"Anomalia ({len(anom)})")
    ax2.set_xlabel("Anomaly Score")
    ax2.set_ylabel("Frequência")
    ax2.set_title("Distribuição dos Scores")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    path = output_dir / "04_anomalias_ar.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    log.info("Salvo: %s", path.name)
