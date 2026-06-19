"""
Visualização — Transporte Público: real vs predito + feature importance.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from utils.logger import get_logger

log = get_logger("viz.transport")


def plot_demand_prediction(result_df: pd.DataFrame, metrics: dict, output_dir: Path):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("XGBoost — Previsão de Demanda de Transporte", fontsize=13, fontweight="bold")

    # Real vs Predito
    ax1 = axes[0]
    n = min(150, len(result_df))
    idx = range(n)
    ax1.plot(idx, result_df["y_real"].iloc[:n].values,
             label="Real", color="#2196F3", linewidth=1.5)
    ax1.plot(idx, result_df["y_pred"].iloc[:n].values,
             label="Predito", color="#FF9800", linewidth=1.2, linestyle="--")
    ax1.set_xlabel("Amostras de teste")
    ax1.set_ylabel("Lotação média (0–1)")
    ax1.set_title(
        f"Real vs Predito\nMAE={metrics['mae']:.4f}  R²={metrics['r2']:.3f}"
    )
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Feature importance
    ax2 = axes[1]
    fi = metrics.get("feature_importance", {})
    if fi:
        features = list(fi.keys())[:10]
        values   = [fi[f] for f in features]
        y_pos    = range(len(features))
        bars     = ax2.barh(y_pos, values, color="#4CAF50", edgecolor="white")
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(features, fontsize=8)
        ax2.set_xlabel("Importância")
        ax2.set_title("Top-10 Features Mais Importantes")
        ax2.grid(alpha=0.3, axis="x")
    else:
        ax2.text(0.5, 0.5, "Feature importance\nnão disponível",
                 ha="center", va="center", transform=ax2.transAxes)

    plt.tight_layout()
    path = output_dir / "05_demanda_transporte.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    log.info("Salvo: %s", path.name)


def plot_lotacao_distribution(df_silver_gps: pd.DataFrame, output_dir: Path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("GPS Ônibus — Distribuição de Lotação", fontsize=12, fontweight="bold")

    ordem = ["VAZIA", "MEIA", "CHEIA", "LOTADA", "DESCONHECIDA"]
    cores  = ["#4CAF50", "#8BC34A", "#FFC107", "#F44336", "#9E9E9E"]

    # Contagem
    vc = df_silver_gps[df_silver_gps["ativo"]]["lotacao"].value_counts().reindex(ordem).fillna(0)
    axes[0].bar(vc.index, vc.values, color=cores[:len(vc)], edgecolor="white")
    axes[0].set_title("Contagem por Nível de Lotação (ônibus ativos)")
    axes[0].set_ylabel("Registros")
    axes[0].grid(alpha=0.3, axis="y")
    for bar, v in zip(axes[0].patches, vc.values):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     str(int(v)), ha="center", fontsize=9)

    # Pie de linhas × lotação
    linha_lot = (
        df_silver_gps[df_silver_gps["ativo"]]
        .groupby("linha")["lotacao"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
        .reindex(columns=ordem, fill_value=0)
    )
    linha_lot.plot(kind="bar", ax=axes[1], stacked=True,
                   color=cores, edgecolor="white", width=0.7)
    axes[1].set_title("Composição de Lotação por Linha")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Proporção")
    axes[1].legend(fontsize=8, loc="upper right")
    axes[1].tick_params(axis="x", rotation=15)
    axes[1].grid(alpha=0.3, axis="y")

    plt.tight_layout()
    path = output_dir / "06_lotacao_onibus.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    log.info("Salvo: %s", path.name)
