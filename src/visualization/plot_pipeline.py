"""
Visualização — Visão geral do pipeline: volumes e taxas de rejeição por camada.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from utils.logger import get_logger

log = get_logger("viz.pipeline")


def plot_volumes(volumes: dict, output_dir: Path):
    """
    volumes = {
        "fonte": {"bronze": int, "silver": int, "gold": int},
        ...
    }
    """
    fontes  = list(volumes.keys())
    bronze  = [volumes[f]["bronze"] for f in fontes]
    silver  = [volumes[f]["silver"] for f in fontes]
    gold_v  = [volumes[f].get("gold", 0) for f in fontes]

    x      = np.arange(len(fontes))
    width  = 0.25
    colors = ["#CD7F32", "#C0C0C0", "#FFD700"]  # bronze, prata, ouro

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Pipeline Medallion — Volume por Camada", fontsize=13, fontweight="bold")

    # Gráfico de barras agrupadas
    ax = axes[0]
    ax.bar(x - width, bronze, width, label="Bronze", color=colors[0], edgecolor="white")
    ax.bar(x,         silver, width, label="Silver", color=colors[1], edgecolor="white")
    ax.bar(x + width, gold_v, width, label="Gold",   color=colors[2], edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(fontes, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Número de registros")
    ax.set_title("Volume por Fonte e Camada")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")

    # Pizza: distribuição total Bronze
    ax2 = axes[1]
    ax2.pie(bronze, labels=fontes, autopct="%1.1f%%",
            colors=plt.cm.Set2.colors[:len(fontes)],
            startangle=90, pctdistance=0.8)
    ax2.set_title(f"Distribuição Bronze\n(Total: {sum(bronze):,} registros)")

    plt.tight_layout()
    path = output_dir / "01_pipeline_volumes.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    log.info("Salvo: %s", path.name)


def plot_quality_heatmap(resultados: list, output_dir: Path):
    """Heatmap de checks de qualidade: verde=OK, vermelho=falhou."""
    if not resultados:
        return

    fontes = [r.fonte for r in resultados]
    nomes  = sorted({c["nome"] for r in resultados for c in r.checks})
    matrix = np.full((len(nomes), len(fontes)), np.nan)

    for j, r in enumerate(resultados):
        lookup = {c["nome"]: c["ok"] for c in r.checks}
        for i, nome in enumerate(nomes):
            if nome in lookup:
                matrix[i, j] = 1 if lookup[nome] else 0

    fig, ax = plt.subplots(figsize=(max(8, len(fontes) * 2), max(5, len(nomes) * 0.4 + 2)))
    cmap = plt.get_cmap("RdYlGn")
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(fontes)))
    ax.set_xticklabels(fontes, rotation=30, ha="right")
    ax.set_yticks(range(len(nomes)))
    ax.set_yticklabels(nomes, fontsize=8)
    ax.set_title("Checks de Qualidade Silver — Verde=OK  Vermelho=Falhou", fontsize=11)

    for i in range(len(nomes)):
        for j in range(len(fontes)):
            v = matrix[i, j]
            if not np.isnan(v):
                ax.text(j, i, "✓" if v else "✗", ha="center", va="center",
                        fontsize=10, color="white")

    plt.tight_layout()
    path = output_dir / "02_quality_heatmap.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    log.info("Salvo: %s", path.name)
