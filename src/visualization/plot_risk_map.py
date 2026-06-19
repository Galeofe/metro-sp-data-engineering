"""
Visualização — Mapa de Risco: scatter geoespacial com clusters DBSCAN.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from pathlib import Path
from utils.logger import get_logger

log = get_logger("viz.risk_map")

_CAT_CORES = {
    "INFRAESTRUTURA": "#2196F3",
    "MEIO_AMBIENTE":  "#4CAF50",
    "MOBILIDADE":     "#FF9800",
    "SEGURANCA":      "#F44336",
    "OUTROS":         "#9E9E9E",
}


def plot_clusters(df_gold: pd.DataFrame, df_clusters: pd.DataFrame, output_dir: Path):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("DBSCAN — Mapa de Risco Urbano", fontsize=13, fontweight="bold")

    # Esquerda: todos os pontos coloridos por categoria
    ax1 = axes[0]
    for cat, cor in _CAT_CORES.items():
        mask = df_gold["categoria_l1"] == cat
        if mask.sum() > 0:
            ax1.scatter(df_gold.loc[mask, "lon"], df_gold.loc[mask, "lat"],
                        c=cor, s=20, alpha=0.6, label=cat, edgecolors="none")
    ax1.set_xlabel("Longitude")
    ax1.set_ylabel("Latitude")
    ax1.set_title("Ocorrências por Categoria")
    ax1.legend(fontsize=8, loc="upper right")
    ax1.grid(alpha=0.3)

    # Direita: pontos coloridos por cluster_id
    ax2 = axes[1]
    n_clusters = df_gold["cluster_id"].max() + 1 if "cluster_id" in df_gold.columns else 0

    if "cluster_id" in df_gold.columns:
        ruido  = df_gold[df_gold["cluster_id"] == -1]
        clustered = df_gold[df_gold["cluster_id"] >= 0]

        ax2.scatter(ruido["lon"], ruido["lat"],
                    c="#CCCCCC", s=10, alpha=0.4, label="Ruído", edgecolors="none")

        if len(clustered) > 0:
            cmap = plt.cm.tab20
            scatter = ax2.scatter(clustered["lon"], clustered["lat"],
                                  c=clustered["cluster_id"],
                                  cmap=cmap, s=35, alpha=0.8, edgecolors="white", linewidths=0.3)
            plt.colorbar(scatter, ax=ax2, label="Cluster ID")

        # Centroides dos clusters
        if not df_clusters.empty:
            for _, row in df_clusters.iterrows():
                ax2.annotate(
                    f"C{int(row['cluster_id'])}\n{row['categoria_dom'][:4]}",
                    xy=(row["lon_centro"], row["lat_centro"]),
                    fontsize=6, ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.6),
                )

    ax2.set_xlabel("Longitude")
    ax2.set_ylabel("Latitude")
    ax2.set_title(f"Clusters de Risco ({n_clusters} áreas identificadas)")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    path = output_dir / "07_mapa_risco_clusters.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    log.info("Salvo: %s", path.name)


def plot_ocorrencias_bairro(df_gold: pd.DataFrame, output_dir: Path):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Ocorrências por Bairro e Prioridade", fontsize=12, fontweight="bold")

    top_bairros = df_gold["bairro"].value_counts().head(10)
    cores_bairro = plt.cm.Blues(np.linspace(0.4, 0.9, len(top_bairros)))

    axes[0].barh(top_bairros.index[::-1], top_bairros.values[::-1],
                 color=cores_bairro[::-1], edgecolor="white")
    axes[0].set_xlabel("Número de ocorrências")
    axes[0].set_title("Top 10 Bairros com Mais Ocorrências")
    axes[0].grid(alpha=0.3, axis="x")

    prio = df_gold["prioridade"].value_counts().sort_index()
    cores_p = ["#4CAF50", "#8BC34A", "#FFC107", "#FF5722", "#F44336"]
    bars = axes[1].bar(prio.index, prio.values, color=cores_p, edgecolor="white")
    axes[1].set_xlabel("Prioridade (1=Baixa, 5=Crítica)")
    axes[1].set_ylabel("Ocorrências")
    axes[1].set_title("Distribuição por Prioridade")
    for bar, v in zip(bars, prio.values):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     str(v), ha="center", fontsize=10)
    axes[1].grid(alpha=0.3, axis="y")

    plt.tight_layout()
    path = output_dir / "08_ocorrencias_bairro.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    log.info("Salvo: %s", path.name)
