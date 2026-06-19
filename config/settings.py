from pathlib import Path

# ── Caminhos ────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
DATA_DIR    = BASE_DIR / "data"
BRONZE_DIR  = DATA_DIR / "bronze"
SILVER_DIR  = DATA_DIR / "silver"
GOLD_DIR    = DATA_DIR / "gold"
REPORTS_DIR = BASE_DIR / "reports"

for _d in (BRONZE_DIR, SILVER_DIR, GOLD_DIR, REPORTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ── Reprodutibilidade ────────────────────────────────────────────────────────
RANDOM_SEED = 42

# ── Volumes de dados simulados ───────────────────────────────────────────────
N_TRAFFIC_RECORDS  = 600   # registros de sensores de tráfego
N_AIR_HOURS        = 48    # horas de qualidade do ar (7 estações × 48h = 336 registros)
N_GPS_RECORDS      = 400   # registros GPS de ônibus
N_OUVIDORIA        = 250   # ocorrências de ouvidoria
N_WEATHER_HOURS    = 192   # horas de dados meteorológicos (8 dias)

# ── Definições geográficas ───────────────────────────────────────────────────
VIAS = [
    {"id": "AV_PAULISTA_NS",    "via": "Av. Paulista",       "sentido": "Norte-Sul",    "lat": -23.5613, "lon": -46.6547},
    {"id": "AV_PAULISTA_SN",    "via": "Av. Paulista",       "sentido": "Sul-Norte",    "lat": -23.5613, "lon": -46.6547},
    {"id": "MARGINAL_TIETE",    "via": "Marginal Tietê",     "sentido": "Leste-Oeste",  "lat": -23.5125, "lon": -46.6395},
    {"id": "MARGINAL_PINHEIROS","via": "Marginal Pinheiros", "sentido": "Norte-Sul",    "lat": -23.5745, "lon": -46.6992},
    {"id": "AV_23_MAIO",        "via": "Av. 23 de Maio",     "sentido": "Norte-Sul",    "lat": -23.5847, "lon": -46.6404},
    {"id": "RADIAL_LESTE",      "via": "Radial Leste",       "sentido": "Leste-Oeste",  "lat": -23.5441, "lon": -46.5957},
]

ESTACOES_AR = [
    {"id": "PIN001", "nome": "Pinheiros",       "lat": -23.5618, "lon": -46.7027},
    {"id": "OSA001", "nome": "Osasco",          "lat": -23.5329, "lon": -46.7920},
    {"id": "IBI001", "nome": "Ibirapuera",      "lat": -23.5874, "lon": -46.6576},
    {"id": "SAO001", "nome": "Santo André",     "lat": -23.6640, "lon": -46.5322},
    {"id": "GUA001", "nome": "Guarulhos",       "lat": -23.4543, "lon": -46.5330},
    {"id": "CAC001", "nome": "Caçapava",        "lat": -23.1006, "lon": -45.7086},  # usa CO em ppm
    {"id": "MOO001", "nome": "Mogi das Cruzes", "lat": -23.5230, "lon": -46.1920},
]

ESTACAO_INMET = "A701"

LINHAS_ONIBUS = [
    {"id": "875P-10", "descricao": "Pinheiros → Centro"},
    {"id": "702U-10", "descricao": "USP → Butantã"},
    {"id": "6450-10", "descricao": "Jabaquara → Aeroporto"},
    {"id": "8000-10", "descricao": "Santo André → SP"},
    {"id": "5100-10", "descricao": "Lapa → Barra Funda"},
]

BAIRROS = [
    {"nome": "Vila Madalena", "lat": -23.5489, "lon": -46.6882},
    {"nome": "Pinheiros",     "lat": -23.5618, "lon": -46.7027},
    {"nome": "Moema",         "lat": -23.6014, "lon": -46.6681},
    {"nome": "Itaim Bibi",    "lat": -23.5851, "lon": -46.6745},
    {"nome": "Perdizes",      "lat": -23.5347, "lon": -46.6647},
    {"nome": "Lapa",          "lat": -23.5193, "lon": -46.7069},
    {"nome": "Butantã",       "lat": -23.5782, "lon": -46.7269},
    {"nome": "Guarulhos",     "lat": -23.4543, "lon": -46.5330},
    {"nome": "Santo André",   "lat": -23.6640, "lon": -46.5322},
    {"nome": "São Bernardo",  "lat": -23.6941, "lon": -46.5649},
]

CATEGORIAS_OUVIDORIA = [
    "ILUMINAÇÃO PÚBLICA",
    "BURACOS E PAVIMENTAÇÃO",
    "COLETA DE LIXO",
    "TRANSPORTE PÚBLICO",
    "SEGURANÇA PÚBLICA",
    "ÁRVORES E PODA",
    "ESGOTO E DRENAGEM",
    "CALÇADAS",
    "PERTURBAÇÃO DO SOSSEGO",
]

CATEGORIA_HIERARQUIA = {
    "ILUMINAÇÃO PÚBLICA":     ("INFRAESTRUTURA", "ILUMINACAO"),
    "BURACOS E PAVIMENTAÇÃO": ("INFRAESTRUTURA", "PAVIMENTACAO"),
    "CALÇADAS":               ("INFRAESTRUTURA", "CALCADAS"),
    "COLETA DE LIXO":         ("MEIO_AMBIENTE",  "RESIDUOS"),
    "ÁRVORES E PODA":         ("MEIO_AMBIENTE",  "ARBORIZACAO"),
    "ESGOTO E DRENAGEM":      ("MEIO_AMBIENTE",  "SANEAMENTO"),
    "TRANSPORTE PÚBLICO":     ("MOBILIDADE",     "TRANSPORTE_COLETIVO"),
    "SEGURANÇA PÚBLICA":      ("SEGURANCA",      "OCORRENCIAS"),
    "PERTURBAÇÃO DO SOSSEGO": ("SEGURANCA",      "PERTURBACAO"),
}

# ── Breakpoints IQAr (metodologia CETESB) ───────────────────────────────────
IQAR_BREAKPOINTS = {
    "mp10": [(0,50,0,40),(50,150,41,80),(150,250,81,120),(250,420,121,200),(420,600,201,400)],
    "mp25": [(0,25,0,40),(25,60,41,80),(60,150,81,120),(150,250,121,200),(250,500,201,400)],
    "o3":   [(0,100,0,40),(100,160,41,80),(160,200,81,120),(200,800,121,200),(800,2000,201,400)],
    "no2":  [(0,200,0,40),(200,240,41,80),(240,320,81,120),(320,1130,121,200),(1130,3000,201,400)],
    "co":   [(0,9,0,40),(9,11,41,80),(11,13.5,81,120),(13.5,15,121,200),(15,40,201,400)],
    "so2":  [(0,40,0,40),(40,365,41,80),(365,800,81,120),(800,1600,121,200),(1600,2620,201,400)],
}

# ── Hiperparâmetros dos modelos ──────────────────────────────────────────────
ISOLATION_FOREST_PARAMS = {
    "n_estimators": 150,
    "contamination": 0.05,
    "random_state": RANDOM_SEED,
}

XGBOOST_PARAMS = {
    "n_estimators":    300,
    "max_depth":       5,
    "learning_rate":   0.05,
    "subsample":       0.8,
    "colsample_bytree":0.8,
    "random_state":    RANDOM_SEED,
    "early_stopping_rounds": 30,
}

DBSCAN_PARAMS = {
    "eps":         0.008,   # ~800m em graus (aprox.)
    "min_samples": 5,
    "metric":      "euclidean",
}

# ── Qualidade de dados — thresholds ─────────────────────────────────────────
QUALITY_NULL_THRESHOLD   = 0.05   # máximo 5% de nulos em campos críticos
QUALITY_DUPLICATE_LIMIT  = 0       # zero duplicatas na Silver
