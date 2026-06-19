"""
Gera os três notebooks de análise do pipeline (Bronze / Silver / Gold).
Execute uma vez: python notebooks/create_notebooks.py
"""
import nbformat as nbf
from pathlib import Path

HERE = Path(__file__).parent


# ══════════════════════════════════════════════════════════════════════════════
# Utilitários
# ══════════════════════════════════════════════════════════════════════════════
def md(text): return nbf.v4.new_markdown_cell(text)
def code(src): return nbf.v4.new_code_cell(src)

SETUP = """\
import os, sys, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path

warnings.filterwarnings('ignore')
plt.rcParams.update({
    'figure.facecolor': '#070b14', 'axes.facecolor': '#0d1526',
    'axes.edgecolor': '#1a3050',   'grid.color': '#1a3050',
    'text.color': '#d0e4ff',       'axes.labelcolor': '#7a9ab8',
    'xtick.color': '#4a6a8a',      'ytick.color': '#4a6a8a',
    'axes.titlecolor': '#00d4ff',  'axes.titlesize': 13,
    'axes.titleweight': 'bold',    'axes.grid': True,
    'figure.dpi': 120,
})
CYAN, GREEN, PURPLE = '#00d4ff', '#00ff88', '#7b2fff'
ORANGE, PINK, GOLD  = '#ff6b00', '#ff2d78', '#ffd700'
NEON = [CYAN, GREEN, PURPLE, ORANGE, PINK, GOLD]

# Detecta raiz do projeto
BASE = Path(os.environ.get('METRO_SP_BASE', Path.cwd()))
if not (BASE / 'data').exists():
    BASE = BASE.parent
BRONZE = BASE / 'data' / 'bronze'
SILVER = BASE / 'data' / 'silver'
GOLD   = BASE / 'data' / 'gold'
print(f"📂 Projeto: {BASE}")
print(f"   Bronze:  {BRONZE.exists()} | Silver: {SILVER.exists()} | Gold: {GOLD.exists()}")
"""


# ══════════════════════════════════════════════════════════════════════════════
# NOTEBOOK 1 — BRONZE
# ══════════════════════════════════════════════════════════════════════════════
def create_bronze():
    nb = nbf.v4.new_notebook()
    nb.cells = [

        md("""\
# 📥 Análise Bronze — Diagnóstico de Qualidade dos Dados Brutos
**Pipeline Metrópole SP · Arquitetura Medallion**

> Esta camada armazena os dados **exatamente como chegam** das fontes.
> O objetivo deste notebook é **perfilar**, **diagnosticar** e **documentar** os problemas de qualidade.
"""),

        code(SETUP),

        code("""\
# ─── Carrega todas as fontes Bronze ──────────────────────────────────────────
arquivos = {
    'IoT Tráfego':    BRONZE / 'iot_traffic_raw.parquet',
    'Qualidade do Ar': BRONZE / 'air_quality_raw.parquet',
    'GPS Ônibus':     BRONZE / 'gps_bus_raw.parquet',
    'Ouvidoria':      BRONZE / 'ouvidoria_cdc_raw.parquet',
    'Meteorologia':   BRONZE / 'weather_inmet_raw.parquet',
}

dfs = {}
for nome, path in arquivos.items():
    if path.exists():
        dfs[nome] = pd.read_parquet(path)
        print(f"  ✅ {nome:<22} {len(dfs[nome]):>5,} registros  |  {len(dfs[nome].columns)} colunas")
    else:
        print(f"  ❌ {nome:<22} ARQUIVO NÃO ENCONTRADO — rode main.py primeiro")
"""),

        code("""\
# ─── Perfil de Qualidade por Fonte ───────────────────────────────────────────
rows = []
for nome, df in dfs.items():
    rows.append({
        'Fonte': nome,
        'Registros': len(df),
        'Colunas': len(df.columns),
        'Nulos (%)': f"{df.isna().mean().mean()*100:.1f}%",
        'Duplicados': df.duplicated().sum(),
        'Tipos únicos': df.dtypes.nunique(),
    })

perfil = pd.DataFrame(rows).set_index('Fonte')
print("\\n──────────────────────────────────────────────────────")
print("  PERFIL DE QUALIDADE — CAMADA BRONZE")
print("──────────────────────────────────────────────────────")
print(perfil.to_string())
print("──────────────────────────────────────────────────────")
perfil
"""),

        code("""\
# ─── Mapa de Nulos por Fonte ──────────────────────────────────────────────────
fig, axes = plt.subplots(1, len(dfs), figsize=(18, 5), facecolor='#070b14')
fig.suptitle('Mapa de Valores Nulos — Camada Bronze', fontsize=14,
             color=CYAN, fontweight='bold', y=1.02)

for ax, (nome, df) in zip(axes, dfs.items()):
    null_pct = df.isna().mean() * 100
    null_pct = null_pct[null_pct > 0] if (null_pct > 0).any() else null_pct.head(8)
    bars = ax.barh(null_pct.index, null_pct.values, color=ORANGE, alpha=0.85)
    ax.set_title(nome, fontsize=9, color=CYAN)
    ax.set_xlabel('Nulos (%)', fontsize=8)
    ax.set_xlim(0, 100)
    for bar, val in zip(bars, null_pct.values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', fontsize=7, color='#d0e4ff')
    ax.tick_params(labelsize=7)

plt.tight_layout()
plt.show()
"""),

        code("""\
# ─── IoT Tráfego — Análise dos Sensores ───────────────────────────────────────
if 'IoT Tráfego' in dfs:
    df_tr = dfs['IoT Tráfego']
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), facecolor='#070b14')
    fig.suptitle('IoT Tráfego — Problemas da Camada Bronze', color=CYAN, fontweight='bold')

    # Contagem de veículos (inclui -1 para sensores em manutenção)
    axes[0].hist(df_tr['contagem_veiculos'].dropna(), bins=40, color=CYAN, alpha=0.8, edgecolor='none')
    axes[0].axvline(-1, color=PINK, linestyle='--', linewidth=2, label='Sensor em manutenção (=-1)')
    axes[0].set_title('Contagem de Veículos (com anomalias)', fontsize=10)
    axes[0].legend(fontsize=8)

    # Bateria (%)
    axes[1].hist(df_tr['bateria_pct'].dropna(), bins=30, color=GREEN, alpha=0.8, edgecolor='none')
    axes[1].set_title('Nível de Bateria dos Sensores (%)', fontsize=10)

    # Velocidade (null quando contagem=0)
    null_vel = df_tr['velocidade_media_kmh'].isna().sum()
    ok_vel   = df_tr['velocidade_media_kmh'].notna().sum()
    axes[2].bar(['Com velocidade', 'Velocidade nula'], [ok_vel, null_vel],
                color=[CYAN, ORANGE], alpha=0.85)
    axes[2].set_title(f'Velocidade: {null_vel} nulos ({null_vel/len(df_tr):.1%})', fontsize=10)

    plt.tight_layout()
    plt.show()
    print(f"\\n⚠  Sensores em manutenção (contagem=-1): {(df_tr['contagem_veiculos']==-1).sum()}")
    print(f"⚠  Velocidade nula:                       {null_vel} registros")
    print(f"⚠  Timestamps sem timezone explícito:      {len(df_tr)} registros (todos)")
"""),

        code("""\
# ─── Qualidade do Ar — Problemas de Formato ────────────────────────────────────
if 'Qualidade do Ar' in dfs:
    df_ar = dfs['Qualidade do Ar']
    print("Tipos de dados originais (Bronze — tudo como object):")
    print(df_ar.dtypes.to_string())
    print(f"\\nColunas de string com valores vazios '':")
    for col in df_ar.select_dtypes(include='object').columns:
        n_empty = (df_ar[col] == '').sum()
        if n_empty > 0:
            print(f"  {col:<12}: {n_empty:>4} vazios ({n_empty/len(df_ar):.1%})")
"""),

        code("""\
# ─── GPS Ônibus — PII e Coordenadas ───────────────────────────────────────────
if 'GPS Ônibus' in dfs:
    df_gps = dfs['GPS Ônibus']

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), facecolor='#070b14')
    fig.suptitle('GPS Ônibus — Problemas Bronze', color=CYAN, fontweight='bold')

    # Coordenadas 0,0 (bug de fora de serviço)
    coord_zero = ((df_gps['lat'] == 0) & (df_gps['lon'] == 0)).sum()
    coord_ok   = len(df_gps) - coord_zero
    axes[0].bar(['Coordenadas válidas', 'Coord (0,0) — bug'], [coord_ok, coord_zero],
                color=[GREEN, PINK], alpha=0.85)
    axes[0].set_title(f'Coordenadas inválidas: {coord_zero} ({coord_zero/len(df_gps):.1%})', fontsize=10)

    # Enum de lotação inconsistente
    axes[1].barh(df_gps['lotacao'].value_counts().index,
                 df_gps['lotacao'].value_counts().values,
                 color=[CYAN,PURPLE,GREEN,ORANGE,PINK,GOLD,'#888'][:len(df_gps['lotacao'].unique())],
                 alpha=0.85)
    axes[1].set_title('Enum de Lotação (PT/EN misturado)', fontsize=10)

    plt.tight_layout()
    plt.show()

    print(f"\\n🔒 LGPD: motorista_id exposto em {df_gps['motorista_id'].notna().sum():,} registros")
    print(f"   Exemplo: {df_gps['motorista_id'].iloc[0]}")
"""),

        code("""\
# ─── Sumário de Problemas Identificados ───────────────────────────────────────
problemas = {
    'IoT Tráfego':     ['contagem_veiculos = -1 (manutenção)',
                         'timestamps sem timezone (BRT sem marcador)',
                         'velocidade_media_kmh nula quando contagem=0'],
    'Qualidade do Ar': ['datas em DD/MM/YYYY (não ISO)',
                         'campos ausentes como "" em vez de NaN',
                         'CO em ppm para estação CAC001 (deveria ser µg/m³)',
                         'MP2.5 negativo (sensor com defeito)'],
    'GPS Ônibus':      ['timestamp UNIX epoch sem fuso horário',
                         'enum lotação inconsistente (CHEIO, CHEIA, FULL)',
                         'coordenadas (0,0) para veículos fora de serviço',
                         'motorista_id exposto (PII — LGPD Art. 5)'],
    'Ouvidoria':       ['CPF e telefone em texto livre (PII — LGPD)',
                         'status PT/EN misturado (OPEN, CLOSED, ABERTO)',
                         '~12% sem coordenadas geográficas',
                         'abreviações inconsistentes de logradouro'],
    'Meteorologia':    ['todos os campos numéricos chegam como string',
                         'ausentes representados pela string "null"'],
}

print("=" * 65)
print("  DIAGNÓSTICO BRONZE — PROBLEMAS IDENTIFICADOS POR FONTE")
print("=" * 65)
total = 0
for fonte, issues in problemas.items():
    print(f"\\n  📂 {fonte}")
    for issue in issues:
        print(f"      ⚠  {issue}")
        total += 1
print(f"\\n  Total de problemas mapeados: {total}")
print("=" * 65)
print("\\n→ Estes problemas são corrigidos na camada SILVER.")
"""),
    ]
    return nb


# ══════════════════════════════════════════════════════════════════════════════
# NOTEBOOK 2 — SILVER
# ══════════════════════════════════════════════════════════════════════════════
def create_silver():
    nb = nbf.v4.new_notebook()
    nb.cells = [

        md("""\
# ◆ Análise Silver — Dados Limpos e Padronizados
**Pipeline Metrópole SP · Arquitetura Medallion**

> A camada Silver contém os dados após **limpeza, padronização e validação**.
> Este notebook compara Bronze vs Silver e analisa a qualidade resultante.
"""),

        code(SETUP),

        code("""\
# ─── Carrega Bronze e Silver para comparação ─────────────────────────────────
br_ar   = pd.read_parquet(BRONZE / 'air_quality_raw.parquet')
sv_ar   = pd.read_parquet(SILVER / 'air_quality_clean.parquet')
br_gps  = pd.read_parquet(BRONZE / 'gps_bus_raw.parquet')
sv_gps  = pd.read_parquet(SILVER / 'gps_bus_clean.parquet')
br_tr   = pd.read_parquet(BRONZE / 'iot_traffic_raw.parquet')
sv_tr   = pd.read_parquet(SILVER / 'iot_traffic_clean.parquet')
br_ouv  = pd.read_parquet(BRONZE / 'ouvidoria_cdc_raw.parquet')
sv_ouv  = pd.read_parquet(SILVER / 'ouvidoria_clean.parquet')

print("  Fonte               Bronze     Silver    Retenção")
print("  " + "-"*50)
for nome, b, s in [
    ('Qualidade do Ar', br_ar, sv_ar),
    ('GPS Ônibus',      br_gps, sv_gps),
    ('IoT Tráfego',    br_tr, sv_tr),
    ('Ouvidoria',       br_ouv, sv_ouv),
]:
    ret = s is not None and b is not None
    n_b = len(b); n_s = len(s)
    print(f"  {nome:<20} {n_b:>6,}  →  {n_s:>6,}   {n_s/n_b:.1%}")
"""),

        code("""\
# ─── Qualidade do Ar: Antes × Depois ─────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(16, 8), facecolor='#070b14')
fig.suptitle('Qualidade do Ar — Bronze vs Silver', color=CYAN, fontweight='bold', fontsize=14)

poluentes = ['mp10', 'mp25', 'o3', 'no2', 'co', 'so2']
for ax, pol in zip(axes.flat, poluentes):
    # Bronze: tenta converter (chega como string/object)
    b_vals = pd.to_numeric(br_ar[pol].replace('', np.nan), errors='coerce').dropna()
    s_vals = sv_ar[pol].dropna()

    ax.hist(b_vals, bins=30, alpha=0.5, color=ORANGE, label='Bronze', density=True)
    ax.hist(s_vals, bins=30, alpha=0.7, color=CYAN,   label='Silver', density=True)
    ax.set_title(pol.upper(), fontsize=10)
    ax.legend(fontsize=7)
    # Marca negativos
    n_neg_b = (b_vals < 0).sum()
    if n_neg_b > 0:
        ax.axvline(0, color=PINK, linestyle='--', linewidth=1.2,
                   label=f'{n_neg_b} negativos removidos')
        ax.legend(fontsize=7)

plt.tight_layout()
plt.show()
print("\\nTransformações aplicadas na Silver:")
print("  ✅ Strings vazias → NaN")
print("  ✅ Datas DD/MM/YYYY → timestamp_utc (UTC+0)")
print("  ✅ CAC001 CO: ppm × 1.165 → µg/m³")
print("  ✅ MP2.5 negativos → removidos")
print("  ✅ IQAr calculado pela metodologia CETESB")
"""),

        code("""\
# ─── IQAr: Série Temporal e Distribuição ─────────────────────────────────────
sv_ar['hora'] = pd.to_datetime(sv_ar['timestamp_utc']).dt.floor('h')
agg = sv_ar.groupby(['hora', 'estacao_id'])['iqar'].mean().reset_index()

fig, axes = plt.subplots(1, 2, figsize=(15, 5), facecolor='#070b14')
fig.suptitle('IQAr — Camada Silver (Análise)', color=CYAN, fontweight='bold')

estacoes = agg['estacao_id'].unique()
for i, est in enumerate(estacoes):
    d = agg[agg.estacao_id == est]
    axes[0].plot(d['hora'], d['iqar'], label=est, color=NEON[i % len(NEON)],
                 linewidth=1.5, alpha=0.85)
axes[0].axhline(80, color=ORANGE, linestyle='--', linewidth=1.2, label='Limite RUIM')
axes[0].axhline(40, color=GREEN,  linestyle='--', linewidth=1.0, label='Limite MODERADO')
axes[0].set_title('IQAr por Estação — Série Temporal')
axes[0].legend(fontsize=8, loc='upper right')
axes[0].set_ylabel('IQAr')

axes[1].hist(sv_ar['iqar'].dropna(), bins=40, color=PURPLE, alpha=0.85, edgecolor='none')
axes[1].axvline(sv_ar['iqar'].mean(), color=CYAN,  linestyle='--', linewidth=2,
                label=f"Média = {sv_ar['iqar'].mean():.1f}")
axes[1].axvline(80, color=ORANGE, linestyle='--', linewidth=1.5, label='Limite RUIM')
axes[1].set_title('Distribuição do IQAr')
axes[1].legend(fontsize=8)

plt.tight_layout()
plt.show()
n_ruim = (sv_ar['iqar'] > 80).sum()
print(f"\\n  Registros com IQAr RUIM ou pior: {n_ruim} ({n_ruim/len(sv_ar):.1%})")
"""),

        code("""\
# ─── GPS: Lotação após Padronização ──────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor='#070b14')
fig.suptitle('GPS Ônibus — Silver: Lotação e Posição', color=CYAN, fontweight='bold')

CLR_LOT = {'VAZIA': GREEN, 'MEIA': '#8bc34a', 'CHEIA': GOLD, 'LOTADA': PINK,
           'DESCONHECIDA': '#607090'}

# Bronze: enum caótico
axes[0].barh(br_gps['lotacao'].value_counts().index,
             br_gps['lotacao'].value_counts().values,
             color=ORANGE, alpha=0.75)
axes[0].set_title('Bronze: Enum de Lotação (bruto)')

# Silver: padronizado
sv_atv = sv_gps[sv_gps['ativo']]
cnt = sv_atv['lotacao'].value_counts()
colors = [CLR_LOT.get(k, '#888') for k in cnt.index]
axes[1].bar(cnt.index, cnt.values, color=colors, alpha=0.85, edgecolor='none')
axes[1].set_title('Silver: Lotação Padronizada (veículos ativos)')

plt.tight_layout()
plt.show()

print(f"\\n  Veículos ativos na Silver:         {sv_gps['ativo'].sum():,}")
print(f"  Fora de serviço (coord 0,0 rem.): {(~sv_gps['ativo']).sum():,}")
print(f"  🔒 LGPD: motorista_id → motorista_hash (SHA-256)")
if 'motorista_hash' in sv_gps.columns:
    print(f"     Exemplo hash: {sv_gps['motorista_hash'].iloc[0]}")
"""),

        code("""\
# ─── Ouvidoria: Geocodificação e PII ─────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor='#070b14')
fig.suptitle('Ouvidoria — Silver: Geocodificação e Status', color=CYAN, fontweight='bold')

# Mapa de pontos geocodificados
df_geo = sv_ouv.dropna(subset=['lat', 'lon'])
CLR_CAT = {'INFRAESTRUTURA': CYAN, 'MEIO_AMBIENTE': GREEN,
           'MOBILIDADE': ORANGE, 'SEGURANCA': PINK, 'OUTROS': '#607090'}
for cat, grp in df_geo.groupby('categoria'):
    axes[0].scatter(grp['lon'], grp['lat'],
                    color=CLR_CAT.get(cat, '#888'),
                    alpha=0.6, s=15, label=cat)
axes[0].set_title('Geocodificação por Categoria')
axes[0].legend(fontsize=7, loc='lower right')
axes[0].set_xlabel('Longitude'); axes[0].set_ylabel('Latitude')

# Status Silver
cnt = sv_ouv['status'].value_counts()
axes[1].bar(cnt.index, cnt.values,
            color=[GREEN, GOLD, PINK, ORANGE][:len(cnt)], alpha=0.85)
axes[1].set_title('Status das Ocorrências (Silver)')

plt.tight_layout()
plt.show()

print(f"\\n  Ocorrências Silver:          {len(sv_ouv):,}")
geo_ok = sv_ouv['coord_geocodificada'].sum() if 'coord_geocodificada' in sv_ouv.columns else df_geo.__len__()
print(f"  Geocodificadas:              {geo_ok:,} ({geo_ok/len(sv_ouv):.1%})")
print("\\n  🔒 LGPD: CPF e telefone removidos via regex das descrições")
"""),

        code("""\
# ─── Score de Qualidade Silver ────────────────────────────────────────────────
print("\\n" + "="*65)
print("  QUALIDADE DE DADOS — SILVER (SLA: ≥ 95%)")
print("="*65)

checks = [
    ("Tráfego — timestamps UTC-aware",
     sv_tr['timestamp_utc'].notna().mean() * 100, 100),
    ("Qualidade Ar — nulos MP2.5",
     (1 - sv_ar['mp25'].isna().mean()) * 100, 95),
    ("Qualidade Ar — IQAr calculado",
     sv_ar['iqar'].notna().mean() * 100, 100),
    ("GPS — coordenadas válidas",
     sv_gps[sv_gps['ativo']]['lat'].notna().mean() * 100, 99),
    ("GPS — lotação padronizada",
     sv_gps['lotacao'].isin(['VAZIA','MEIA','CHEIA','LOTADA','DESCONHECIDA']).mean() * 100, 100),
    ("Ouvidoria — sem PII exposto",
     (1 - sv_ouv.get('texto_original', pd.Series([''])).str.contains(r'\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}', na=False).mean()) * 100, 100),
]

all_pass = True
for nome, valor, sla in checks:
    status = "PASS ✅" if valor >= sla else "FAIL ❌"
    bar = "█" * int(valor // 5) + "░" * (20 - int(valor // 5))
    print(f"  {status}  {nome:<40} [{bar}] {valor:.1f}%  (SLA:{sla}%)")
    if valor < sla:
        all_pass = False

print("="*65)
print(f"  Resultado: {'✅ TODOS OS CHECKS PASSARAM' if all_pass else '❌ FALHAS DETECTADAS'}")
"""),
    ]
    return nb


# ══════════════════════════════════════════════════════════════════════════════
# NOTEBOOK 3 — GOLD / ML
# ══════════════════════════════════════════════════════════════════════════════
def create_gold():
    nb = nbf.v4.new_notebook()
    nb.cells = [

        md("""\
# ◈ Análise Gold — Feature Engineering & Modelos de IA
**Pipeline Metrópole SP · Arquitetura Medallion**

> A camada Gold contém **features prontas para ML** e os resultados dos modelos treinados.
> Este notebook analisa correlações, desempenho dos modelos e insights gerados.
"""),

        code(SETUP),

        code("""\
# ─── Carrega datasets Gold ────────────────────────────────────────────────────
g_anom  = pd.read_parquet(GOLD / 'air_quality_with_anomalies.parquet')
g_bus   = pd.read_parquet(GOLD / 'bus_demand_forecast.parquet')
g_occ   = pd.read_parquet(GOLD / 'occurrence_clusters.parquet')
g_clust = pd.read_parquet(GOLD / 'risk_clusters_summary.parquet') \\
          if (GOLD / 'risk_clusters_summary.parquet').exists() else None

print("  Dataset                         Registros  Features")
print("  " + "-"*52)
for nome, df in [('air_quality + anomalias', g_anom),
                  ('bus demand forecast',     g_bus),
                  ('occurrence clusters',     g_occ)]:
    print(f"  {nome:<35} {len(df):>5,}  {len(df.columns):>7}")
"""),

        code("""\
# ─── Correlação de Features — Qualidade do Ar ────────────────────────────────
feats_ar = ['mp10','mp25','o3','no2','co','so2',
            'temp_c','umidade_pct','vento_vel_ms',
            'z_mp10','z_mp25','z_o3','z_no2','iqar']
feats_ar = [c for c in feats_ar if c in g_anom.columns]

corr = g_anom[feats_ar].corr()

fig, ax = plt.subplots(figsize=(11, 9), facecolor='#070b14')
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

# Heatmap customizado (tema cyber)
import matplotlib.colors as mcolors
cmap = mcolors.LinearSegmentedColormap.from_list(
    'cyber', ['#ff2d78', '#070b14', '#00d4ff'])
im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1, aspect='auto')
plt.colorbar(im, ax=ax, shrink=0.8, label='Correlação de Pearson')

ax.set_xticks(range(len(corr))); ax.set_yticks(range(len(corr)))
ax.set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(corr.columns, fontsize=9)
ax.set_title('Matriz de Correlação — Features Gold (Qualidade do Ar)',
             color=CYAN, fontweight='bold', pad=15)

for i in range(len(corr)):
    for j in range(len(corr)):
        val = corr.values[i, j]
        if abs(val) > 0.3:
            ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                    fontsize=7, color='white' if abs(val) > 0.6 else '#d0e4ff')

plt.tight_layout()
plt.show()
"""),

        code("""\
# ─── Isolation Forest — Análise de Anomalias ─────────────────────────────────
if 'anomalia_pred' in g_anom.columns:
    n_total = len(g_anom)
    n_anom  = g_anom['anomalia_pred'].sum()

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), facecolor='#070b14')
    fig.suptitle('Isolation Forest — Detecção de Anomalias (Qualidade do Ar)',
                 color=CYAN, fontweight='bold')

    # Score distribution
    axes[0].hist(g_anom[g_anom.anomalia_pred==0]['anomaly_score'], bins=40,
                 color=CYAN, alpha=0.7, label='Normal', density=True)
    axes[0].hist(g_anom[g_anom.anomalia_pred==1]['anomaly_score'], bins=20,
                 color=PINK, alpha=0.85, label='Anomalia', density=True)
    axes[0].set_title('Distribuição do Anomaly Score')
    axes[0].set_xlabel('Score (menor = mais anômalo)')
    axes[0].legend()

    # IQAr vs Score scatter
    axes[1].scatter(g_anom[g_anom.anomalia_pred==0]['iqar'],
                    g_anom[g_anom.anomalia_pred==0]['anomaly_score'],
                    color=CYAN, alpha=0.3, s=8, label='Normal')
    axes[1].scatter(g_anom[g_anom.anomalia_pred==1]['iqar'],
                    g_anom[g_anom.anomalia_pred==1]['anomaly_score'],
                    color=PINK, alpha=0.8, s=20, label='Anomalia', zorder=5)
    axes[1].set_title('IQAr vs Anomaly Score')
    axes[1].set_xlabel('IQAr'); axes[1].set_ylabel('Anomaly Score')
    axes[1].legend()

    # Por estação
    if 'estacao_id' in g_anom.columns:
        est_anom = g_anom.groupby('estacao_id')['anomalia_pred'].mean() * 100
        bars = axes[2].bar(est_anom.index, est_anom.values,
                           color=[PINK if v > 5 else CYAN for v in est_anom.values],
                           alpha=0.85)
        axes[2].axhline(5, color=ORANGE, linestyle='--', linewidth=1.2,
                        label='Threshold 5%')
        axes[2].set_title('Taxa de Anomalia por Estação (%)')
        axes[2].legend()
        axes[2].tick_params(axis='x', rotation=30, labelsize=8)

    plt.tight_layout()
    plt.show()
    print(f"\\n  Anomalias detectadas: {n_anom} / {n_total} ({n_anom/n_total:.1%})")
    print(f"  Contamination param: 5%  |  n_estimators: 150")
"""),

        code("""\
# ─── XGBoost — Análise de Demanda de Transporte ───────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5), facecolor='#070b14')
fig.suptitle('XGBoost — Previsão de Demanda de Transporte', color=CYAN, fontweight='bold')

# Distribuição do target
axes[0].hist(g_bus['target'].dropna(), bins=30, color=PURPLE, alpha=0.85, edgecolor='none')
axes[0].axvline(g_bus['target'].mean(), color=CYAN, linestyle='--', linewidth=2,
                label=f"Média={g_bus['target'].mean():.2f}")
axes[0].set_title('Distribuição do Target (lotação t+1h)')
axes[0].legend(fontsize=8)

# Target por hora do dia
agg_hora = g_bus.groupby('hora_do_dia')['target'].agg(['mean','std']).reset_index()
axes[1].fill_between(agg_hora['hora_do_dia'],
                     agg_hora['mean'] - agg_hora['std'],
                     agg_hora['mean'] + agg_hora['std'],
                     alpha=0.2, color=CYAN)
axes[1].plot(agg_hora['hora_do_dia'], agg_hora['mean'],
             color=CYAN, linewidth=2.5, marker='o', markersize=5)
axes[1].set_title('Lotação Média por Hora do Dia')
axes[1].set_xlabel('Hora'); axes[1].set_ylabel('Lotação (0–1)')
axes[1].set_xticks(range(0, 24, 2))

# Correlação features vs target
feat_cols = ['hora_do_dia','dia_semana','e_feriado','e_fim_semana',
             'lag_1h','lag_24h','temperatura_c','precipitacao_mm']
feat_cols = [c for c in feat_cols if c in g_bus.columns]
corrs = g_bus[feat_cols + ['target']].corr()['target'].drop('target').abs().sort_values(ascending=True)
axes[2].barh(corrs.index, corrs.values,
             color=[CYAN if v > 0.5 else PURPLE for v in corrs.values], alpha=0.85)
axes[2].set_title('Correlação Features × Target')
axes[2].set_xlabel('|Pearson|')

plt.tight_layout()
plt.show()
print(f"\\n  Feature mais correlacionada: {corrs.idxmax()} ({corrs.max():.3f})")
"""),

        code("""\
# ─── DBSCAN — Análise dos Clusters de Risco ──────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor='#070b14')
fig.suptitle('DBSCAN — Mapa de Risco Urbano', color=CYAN, fontweight='bold')

CLR = {'INFRAESTRUTURA': CYAN, 'MEIO_AMBIENTE': GREEN,
       'MOBILIDADE': ORANGE, 'SEGURANCA': PINK, 'OUTROS': '#607090'}

df_geo = g_occ.dropna(subset=['lat','lon'])
noise  = df_geo[df_geo.cluster_id == -1]
clust  = df_geo[df_geo.cluster_id >= 0]

# Mapa geo
for cat, grp in clust.groupby('categoria_l1'):
    axes[0].scatter(grp['lon'], grp['lat'],
                    c=CLR.get(cat,'#888'), s=12, alpha=0.7, label=cat)
axes[0].scatter(noise['lon'], noise['lat'],
                c='#2a4060', s=5, alpha=0.4, label='Ruído')
if g_clust is not None and 'lon_centro' in g_clust.columns:
    axes[0].scatter(g_clust['lon_centro'], g_clust['lat_centro'],
                    marker='*', s=200, c=GOLD, zorder=10, label='Centroide')
axes[0].set_title('Clusters de Risco (eps=0.008, min=5)')
axes[0].legend(fontsize=7, loc='lower right')
axes[0].set_xlabel('Longitude'); axes[0].set_ylabel('Latitude')

# Tamanho dos clusters
if g_clust is not None and 'n_ocorrencias' in g_clust.columns:
    g_clust_sorted = g_clust.sort_values('n_ocorrencias', ascending=True)
    dom = g_clust_sorted.get('categoria_dom', pd.Series(['OUTROS']*len(g_clust_sorted)))
    colors_cl = [CLR.get(c, '#888') for c in dom]
    axes[1].barh(range(len(g_clust_sorted)), g_clust_sorted['n_ocorrencias'],
                 color=colors_cl, alpha=0.85, edgecolor='none')
    axes[1].set_yticks(range(len(g_clust_sorted)))
    axes[1].set_yticklabels(g_clust_sorted.get('cluster_id', range(len(g_clust_sorted))),
                            fontsize=9)
    axes[1].set_title('Ocorrências por Cluster')
    axes[1].set_xlabel('Nº de ocorrências')

plt.tight_layout()
plt.show()

n_cl = (g_occ.cluster_id >= 0).sum()
n_no = (g_occ.cluster_id == -1).sum()
print(f"\\n  Pontos clusterizados: {n_cl} ({n_cl/len(g_occ):.1%})")
print(f"  Ruído (outliers):     {n_no} ({n_no/len(g_occ):.1%})")
if g_clust is not None:
    print(f"  Clusters detectados: {len(g_clust)}")
"""),

        code("""\
# ─── Sumário Executivo — Camada Gold ─────────────────────────────────────────
print("\\n" + "=" * 65)
print("  SUMÁRIO EXECUTIVO — PIPELINE METRÓPOLE SP")
print("=" * 65)

print("\\n  CAMADA GOLD — DATASETS GERADOS:")
for nome, df in [('air_quality_anomaly',    g_anom),
                  ('bus_demand_forecast',    g_bus),
                  ('occurrence_clusters',    g_occ)]:
    print(f"    📁 {nome:<30}  {len(df):>5,} registros  ×  {len(df.columns):>3} features")

print("\\n  MODELOS TREINADOS:")
if 'anomalia_pred' in g_anom.columns:
    n_a = g_anom['anomalia_pred'].sum()
    print(f"    ⚡ Isolation Forest   → {n_a} anomalias ({n_a/len(g_anom):.1%})")
print(f"    📈 XGBoost            → {len(g_bus)} amostras, split 80/20 temporal")
if g_clust is not None:
    print(f"    📍 DBSCAN             → {len(g_clust)} clusters de risco")

print("\\n  QUALIDADE DO AR:")
if 'faixa_iqar' in g_anom.columns:
    for faixa, cnt in g_anom['faixa_iqar'].value_counts().items():
        pct = cnt/len(g_anom)*100
        bar = "█" * int(pct // 5)
        print(f"    {faixa:<15} [{bar:<20}] {cnt:>4} ({pct:.1f}%)")

print("\\n  → Ver dashboard: http://localhost:8501")
print("=" * 65)
"""),
    ]
    return nb


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    notebooks = {
        "bronze_analysis": create_bronze(),
        "silver_analysis": create_silver(),
        "gold_analysis":   create_gold(),
    }
    for name, nb in notebooks.items():
        path = HERE / f"{name}.ipynb"
        with open(path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)
        print(f"  OK {path.name}")

    print(f"\n  Notebooks criados em: {HERE}")
    print("  Execute: jupyter lab  (na raiz do projeto)")