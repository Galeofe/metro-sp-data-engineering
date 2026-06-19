"""
Metrópole SP Data Platform — Dashboard Streamlit  (Tema Cyber/Tech)
"""
import subprocess, sys, warnings
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Metrópole SP — Data Platform",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR    = Path(__file__).parent
BRONZE_DIR  = BASE_DIR / "data" / "bronze"
SILVER_DIR  = BASE_DIR / "data" / "silver"
GOLD_DIR    = BASE_DIR / "data" / "gold"
REPORTS_DIR = BASE_DIR / "reports"

# ── Design tokens ─────────────────────────────────────────────────────────────
CYAN       = "#00d4ff"
GREEN      = "#00ff88"
PURPLE     = "#7b2fff"
ORANGE     = "#ff6b00"
PINK       = "#ff2d78"
GOLD_C     = "#ffd700"
BRONZE_COL = "#cd7f32"
SILVER_COL = "#b8b8c8"
NEON       = [CYAN, GREEN, PURPLE, ORANGE, PINK, GOLD_C,
              "#00ffcc", "#ff9500", "#a78bfa", "#34d399"]

# ══════════════════════════════════════════════════════════════════════════════
# CSS — Tema Cyber
# ══════════════════════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=JetBrains+Mono:wght@300;400;600&display=swap');

:root {
    --bg:     #070b14;
    --bg2:    #0d1526;
    --cyan:   #00d4ff;
    --green:  #00ff88;
    --purple: #7b2fff;
    --orange: #ff6b00;
    --red:    #ff2d78;
    --gold:   #ffd700;
    --text:   #d0e4ff;
    --muted:  #4a6a8a;
    --border: rgba(0,212,255,0.16);
}

/* App Background */
.stApp {
    background-color: var(--bg) !important;
    background-image:
        radial-gradient(ellipse 80% 60% at 50% -10%,
            rgba(0,212,255,0.055) 0%, transparent 65%),
        linear-gradient(rgba(0,212,255,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.022) 1px, transparent 1px);
    background-size: 100% 100%, 55px 55px, 55px 55px;
    background-position: top, -1px -1px, -1px -1px;
}
.main .block-container {
    max-width: 1440px !important;
    padding: 1.5rem 2rem 3rem !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#04080f 0%,#07101e 50%,#080d1a 100%) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 6px 0 30px rgba(0,212,255,0.04) !important;
}
section[data-testid="stSidebar"] .block-container { padding-top: 0 !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span { color: var(--text) !important; }
section[data-testid="stSidebar"] hr   { border-color: var(--border) !important; margin: 12px 0 !important; }

/* Headings */
h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    background: linear-gradient(100deg,#00d4ff 0%,#4af7ff 30%,#7b2fff 65%,#00ff88 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    line-height: 1.15 !important;
    margin-bottom: 4px !important;
}
h2 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    color: var(--cyan) !important;
    font-size: 0.95rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 6px !important;
    margin: 20px 0 12px !important;
}
h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    font-size: 0.82rem !important;
    letter-spacing: 1px !important;
}
p { color: var(--text) !important; }

/* Metrics */
[data-testid="metric-container"] {
    background: linear-gradient(135deg,rgba(0,212,255,0.03) 0%,rgba(4,8,18,0.9) 100%) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 20px 18px !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.08),inset 0 0 30px rgba(0,0,0,0.4) !important;
}
[data-testid="metric-container"]::before {
    content: ''; position: absolute;
    top: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg,transparent,var(--cyan),transparent);
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    color: var(--cyan) !important;
    text-shadow: 0 0 14px rgba(0,212,255,0.55) !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--green) !important;
    font-size: 0.7rem !important;
}

/* Buttons */
[data-testid="stButton"] > button {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.68rem !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg,rgba(0,212,255,0.08),rgba(123,47,255,0.08)) !important;
    border: 1px solid rgba(0,212,255,0.5) !important;
    color: var(--cyan) !important;
    border-radius: 7px !important;
    padding: 0.55rem 1.2rem !important;
    transition: all .25s ease !important;
}
[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg,rgba(0,212,255,0.2),rgba(123,47,255,0.2)) !important;
    box-shadow: 0 0 22px rgba(0,212,255,0.35),inset 0 0 12px rgba(0,212,255,0.08) !important;
    border-color: var(--cyan) !important;
    transform: translateY(-1px) !important;
}

/* Tabs */
[data-baseweb="tab-list"] {
    background: rgba(4,8,18,0.9) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 2px !important; padding: 0 4px !important;
}
[data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.76rem !important;
    letter-spacing: 1px !important;
    color: var(--muted) !important;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
    transition: all .2s !important;
    background: transparent !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: var(--cyan) !important;
    border-bottom-color: var(--cyan) !important;
    background: rgba(0,212,255,0.05) !important;
    text-shadow: 0 0 8px rgba(0,212,255,.45) !important;
}
[data-testid="stTabsContent"] {
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    padding: 22px !important;
    background: rgba(5,10,20,0.5) !important;
}

/* Alerts */
[data-testid="stInfo"] {
    background: rgba(0,212,255,0.04) !important;
    border: 1px solid rgba(0,212,255,0.15) !important;
    border-left: 3px solid var(--cyan) !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="stWarning"] {
    background: rgba(255,107,0,0.04) !important;
    border: 1px solid rgba(255,107,0,0.15) !important;
    border-left: 3px solid var(--orange) !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="stSuccess"] {
    background: rgba(0,255,136,0.04) !important;
    border: 1px solid rgba(0,255,136,0.15) !important;
    border-left: 3px solid var(--green) !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="stInfo"] p,[data-testid="stWarning"] p,[data-testid="stSuccess"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
    background: var(--bg2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* Misc */
hr { border-color: var(--border) !important; }
.stCaption, [data-testid="stCaptionContainer"] p {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--muted) !important;
    font-size: 0.7rem !important;
    letter-spacing: .5px !important;
}
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,.55); }

/* ── Custom HTML components ── */

/* Sidebar brand */
.sb-brand {
    text-align: center;
    padding: 28px 12px 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 10px;
}
.sb-hex {
    font-size: 3.2rem; display: block;
    color: var(--cyan);
    text-shadow: 0 0 16px rgba(0,212,255,.9),0 0 40px rgba(0,212,255,.35),0 0 80px rgba(0,212,255,.1);
    animation: hex-glow 3s ease-in-out infinite;
    margin-bottom: 12px; line-height: 1;
}
@keyframes hex-glow {
    0%,100%{text-shadow:0 0 16px rgba(0,212,255,.9),0 0 40px rgba(0,212,255,.35)}
    50%{text-shadow:0 0 24px rgba(0,212,255,1),0 0 60px rgba(0,212,255,.55),0 0 100px rgba(0,212,255,.2)}
}
.sb-title {
    font-family: 'Orbitron', sans-serif;
    font-size: .82rem; font-weight: 900;
    letter-spacing: 4px; color: var(--text);
    text-transform: uppercase;
}
.sb-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: .58rem; color: var(--muted);
    letter-spacing: 2px; margin-top: 5px;
}
.status-live {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: .7rem; color: var(--green);
    padding: 8px 12px;
    background: rgba(0,255,136,.04);
    border: 1px solid rgba(0,255,136,.15);
    border-radius: 8px; width: 100%; box-sizing: border-box;
    margin-top: 8px;
}
.dot-pulse {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--green); flex-shrink: 0;
    box-shadow: 0 0 6px var(--green);
    animation: dpulse 2s ease-in-out infinite;
}
@keyframes dpulse {
    0%,100%{box-shadow:0 0 4px var(--green);opacity:1}
    50%{box-shadow:0 0 12px var(--green),0 0 22px rgba(0,255,136,.35);opacity:.65}
}
.status-offline {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: .7rem; color: var(--orange);
    padding: 8px 12px;
    background: rgba(255,107,0,.04);
    border: 1px solid rgba(255,107,0,.2);
    border-radius: 8px; width: 100%; box-sizing: border-box;
    margin-top: 8px;
}
.dot-offline {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--orange); flex-shrink: 0;
    box-shadow: 0 0 5px var(--orange);
}

/* KPI cards */
.kpi-row { display:flex; gap:14px; margin:14px 0 24px; }
.kpi-card {
    flex: 1;
    position: relative;
    background: linear-gradient(145deg,rgba(0,0,0,.6) 0%,rgba(13,21,38,.92) 100%);
    border: 1px solid rgba(0,212,255,.14);
    border-radius: 14px;
    padding: 22px 20px 18px;
    overflow: hidden;
    transition: all .3s ease;
}
.kpi-card::before {
    content: ''; position: absolute;
    top: 0; left: 8%; right: 8%; height: 1px;
    background: linear-gradient(90deg,transparent,var(--kc,#00d4ff),transparent);
}
.kpi-card::after {
    content: ''; position: absolute;
    bottom: -50px; right: -50px;
    width: 120px; height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle,var(--kc,#00d4ff) 0%,transparent 70%);
    opacity: .04;
}
.kpi-card:hover {
    border-color: rgba(0,212,255,.35);
    box-shadow: 0 0 28px rgba(0,212,255,.12),0 6px 24px rgba(0,0,0,.5);
    transform: translateY(-2px);
}
.kpi-icon { font-size: 1.3rem; margin-bottom: 10px; }
.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: .58rem; letter-spacing: 2.5px;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: 7px;
}
.kpi-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem; font-weight: 700;
    color: var(--kc,#00d4ff);
    line-height: 1.05;
}
.kpi-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: .65rem; color: var(--muted);
    margin-top: 7px;
}

/* Pipeline flow */
.pl-wrap {
    background: rgba(4,8,18,.8);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 20px;
    display: flex; align-items: stretch;
    gap: 0; overflow-x: auto;
    margin: 8px 0 20px;
}
.pl-stage { flex:1; min-width:148px; border-radius:10px; padding:16px 14px; }
.pl-bronze { background:rgba(205,127,50,.07);  border:1px solid rgba(205,127,50,.25); }
.pl-silver { background:rgba(192,192,192,.04); border:1px solid rgba(192,192,192,.18); }
.pl-gold   { background:rgba(255,215,0,.05);   border:1px solid rgba(255,215,0,.22);   }
.pl-model  { background:rgba(123,47,255,.07);  border:1px solid rgba(123,47,255,.25);  }
.pl-arrow  { display:flex; align-items:center; padding:0 14px; font-size:1.1rem; color:rgba(0,212,255,.3); flex-shrink:0; }
.pl-title  { font-family:'Orbitron',sans-serif; font-size:.6rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; margin-bottom:12px; }
.c-bronze { color:#cd7f32; text-shadow:0 0 8px rgba(205,127,50,.5); }
.c-silver { color:#b8b8c8; text-shadow:0 0 6px rgba(192,192,192,.3); }
.c-gold   { color:#ffd700; text-shadow:0 0 8px rgba(255,215,0,.55); }
.c-model  { color:#9b6fff; text-shadow:0 0 8px rgba(123,47,255,.55); }
.pl-item  {
    font-family:'JetBrains Mono',monospace;
    font-size:.65rem; color:rgba(150,175,205,.7);
    background:rgba(0,0,0,.3);
    border-left:2px solid rgba(0,212,255,.2);
    padding:3px 8px; margin:3px 0;
    border-radius:0 4px 4px 0;
}

/* Section divider */
.sec-div {
    font-family:'JetBrains Mono',monospace;
    font-size:.58rem; letter-spacing:3px;
    text-transform:uppercase; color:var(--muted);
    border-bottom:1px solid var(--border);
    padding-bottom:4px; margin:22px 0 14px;
}

/* Page header accent */
.page-header { border-left:3px solid var(--cyan); padding-left:14px; margin-bottom:20px; }
.page-header .ph-tag {
    font-family:'JetBrains Mono',monospace;
    font-size:.62rem; letter-spacing:3px;
    text-transform:uppercase; color:var(--muted);
    margin-bottom:4px;
}

/* Image card */
.img-card {
    background: rgba(4,8,18,.8);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 14px;
    transition: border-color .25s;
}
.img-card:hover { border-color: rgba(0,212,255,.4); }
.img-title {
    font-family:'Orbitron',sans-serif;
    font-size:.65rem; letter-spacing:1.5px;
    text-transform:uppercase; color:var(--cyan);
    margin-bottom:10px;
}

/* Code-style text in markdown */
code {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(0,212,255,0.08) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    color: var(--cyan) !important;
    border-radius: 4px !important;
    padding: 1px 6px !important;
    font-size: .85em !important;
}

/* ── Laboratório ─────────────────────────────────────── */
.nb-card {
    background: linear-gradient(145deg,rgba(0,0,0,.55) 0%,rgba(13,21,38,.9) 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 18px;
    position: relative; overflow: hidden;
    transition: all .3s;
}
.nb-card::before {
    content: ''; position: absolute;
    top: 0; left: 8%; right: 8%; height: 1px;
    background: linear-gradient(90deg,transparent,var(--nc,#00d4ff),transparent);
}
.nb-card:hover { border-color: rgba(0,212,255,.4);
    box-shadow: 0 0 22px rgba(0,212,255,.1); }
.nb-title {
    font-family:'Orbitron',sans-serif; font-size:.75rem;
    font-weight:700; letter-spacing:2px; margin-bottom:8px;
    color: var(--nc, #00d4ff);
}
.nb-stat {
    font-family:'JetBrains Mono',monospace; font-size:.65rem;
    color:var(--muted); margin-bottom:3px;
}
.nb-ok   { color: #00ff88; }
.nb-err  { color: #ff2d78; }
.nb-pend { color: #ff6b00; }

/* Relatórios filtro */
.report-filters {
    background: rgba(4,8,18,.85);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 20px;
}
.filter-title {
    font-family:'Orbitron',sans-serif; font-size:.65rem;
    letter-spacing:2px; text-transform:uppercase;
    color:var(--cyan); margin-bottom:14px;
}

/* Notebook cell renderer */
.nb-cell-code {
    background: rgba(0,0,0,.45);
    border: 1px solid rgba(0,212,255,.12);
    border-left: 3px solid rgba(0,212,255,.4);
    border-radius: 0 8px 8px 0;
    padding: 12px 14px;
    margin: 8px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: .78rem;
    color: #a8c4e0;
    white-space: pre-wrap;
    overflow-x: auto;
}
.nb-cell-md {
    border-left: 3px solid rgba(123,47,255,.4);
    padding: 8px 14px;
    margin: 6px 0;
    color: var(--text);
}
.nb-output {
    background: rgba(0,0,0,.3);
    border: 1px solid rgba(0,212,255,.08);
    border-radius: 6px;
    padding: 10px 14px;
    margin: 4px 0 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: .75rem; color: #7a9ab8;
    white-space: pre-wrap; overflow-x: auto;
    max-height: 300px; overflow-y: auto;
}
.nb-output-err {
    background: rgba(255,45,120,.05);
    border: 1px solid rgba(255,45,120,.2);
    border-radius: 6px;
    padding: 10px 14px; margin: 4px 0 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: .75rem; color: #ff6a90;
    white-space: pre-wrap; overflow-x: auto;
}
.sync-banner {
    display:flex; align-items:center; gap:10px;
    background: rgba(0,255,136,.05);
    border: 1px solid rgba(0,255,136,.2);
    border-radius: 10px; padding: 12px 16px;
    font-family:'JetBrains Mono',monospace;
    font-size:.75rem; color:var(--green);
    margin-bottom:16px;
}
.sync-alert {
    display:flex; align-items:center; gap:10px;
    background: rgba(255,107,0,.05);
    border: 1px solid rgba(255,107,0,.25);
    border-radius: 10px; padding: 12px 16px;
    font-family:'JetBrains Mono',monospace;
    font-size:.75rem; color:var(--orange);
    margin-bottom:16px;
}

/* Log box (pipeline em tempo real) */
.log-box {
    background: #020509;
    border: 1px solid rgba(0,212,255,0.18);
    border-radius: 10px;
    padding: 14px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: .73rem;
    color: #4af7c0;
    line-height: 1.7;
    max-height: 420px;
    overflow-y: auto;
    white-space: pre-wrap;
    box-shadow: inset 0 0 40px rgba(0,0,0,.6), 0 0 20px rgba(0,212,255,.06);
}

/* Linhagem — nó */
.lin-node {
    background: linear-gradient(135deg,rgba(0,212,255,.06),rgba(0,0,0,.7));
    border: 1px solid rgba(0,212,255,.22);
    border-radius: 12px;
    padding: 16px 14px;
    text-align: center;
    transition: all .3s;
}
.lin-node:hover { border-color: var(--cyan); box-shadow: 0 0 24px rgba(0,212,255,.18); }
.lin-node-title {
    font-family:'Orbitron',sans-serif; font-size:.65rem;
    font-weight:700; letter-spacing:2px; text-transform:uppercase;
    margin-bottom:10px;
}
.lin-item {
    font-family:'JetBrains Mono',monospace; font-size:.62rem;
    color:rgba(150,175,205,.7);
    background:rgba(0,0,0,.3);
    border-left:2px solid rgba(0,212,255,.2);
    padding:2px 8px; margin:2px 0;
    border-radius:0 4px 4px 0;
    text-align:left;
}

/* SLA status pills */
.sla-ok   { color:#00ff88; font-weight:700; }
.sla-warn { color:#ffd700; font-weight:700; }
.sla-fail { color:#ff2d78; font-weight:700; }

/* Scheduler card */
.sched-card {
    background: rgba(4,8,18,.85);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
}

/* Dict table */
.dict-row {
    display:grid; grid-template-columns: 200px 120px 1fr;
    gap: 0; border-bottom: 1px solid rgba(0,212,255,.06);
    padding: 7px 12px;
    font-family:'JetBrains Mono',monospace; font-size:.7rem;
    transition: background .2s;
}
.dict-row:hover { background: rgba(0,212,255,.03); }
.dict-col { padding: 0 6px; }
.dict-field { color: var(--cyan); }
.dict-type  { color: var(--orange); }
.dict-desc  { color: rgba(160,185,210,.8); }
.dict-header {
    display:grid; grid-template-columns: 200px 120px 1fr;
    gap: 0; padding: 8px 12px;
    font-family:'Orbitron',sans-serif; font-size:.58rem;
    letter-spacing:2px; text-transform:uppercase; color:var(--muted);
    border-bottom: 1px solid rgba(0,212,255,.18);
    margin-bottom: 2px;
}

/* Presentation mode */
body.present-mode section[data-testid="stSidebar"] { display:none !important; }
body.present-mode .main .block-container { max-width:100% !important; padding:1rem 1.5rem !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def load(path: Path):
    return pd.read_parquet(path) if path.exists() else None


def dados_existem() -> bool:
    return (GOLD_DIR / "air_quality_with_anomalies.parquet").exists()


LOG_FILE    = BASE_DIR / "logs" / "pipeline.log"
SCHED_FILE  = BASE_DIR / "logs" / "scheduler.json"

def rodar_pipeline():
    """Executa o pipeline com streaming de logs em tempo real."""
    LOG_FILE.parent.mkdir(exist_ok=True)
    LOG_FILE.write_text("", encoding="utf-8")

    log_box  = st.empty()
    status_p = st.empty()
    lines: list = []

    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
        cwd=str(BASE_DIR),
    )

    while True:
        line = proc.stdout.readline()
        if line == "" and proc.poll() is not None:
            break
        if line:
            lines.append(line.rstrip())
            shown = lines[-35:]
            log_box.markdown(
                '<div class="log-box">' +
                "<br>".join(shown) +
                "</div>",
                unsafe_allow_html=True,
            )

    rc = proc.wait()
    st.cache_data.clear()
    log_box.empty()
    if rc == 0:
        status_p.success("Pipeline concluído com sucesso!")
    else:
        status_p.error(f"Pipeline encerrado com código {rc}. Veja o log acima.")
        if lines:
            with st.expander("Log completo"):
                st.code("\n".join(lines))


def kpi_card(icon, label, value, sub, color=CYAN):
    return (
        f'<div class="kpi-card" style="--kc:{color}">'
        f'<div class="kpi-icon">{icon}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>'
    )


def cyber(fig, title="", h=320):
    """Aplica tema cyber dark a qualquer figura Plotly."""
    ax = dict(
        gridcolor="rgba(0,212,255,0.055)",
        linecolor="rgba(0,212,255,0.13)",
        tickfont=dict(family="JetBrains Mono", color="#3a5a7a", size=9),
        zerolinecolor="rgba(0,212,255,0.07)",
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(4,8,18,0.65)",
        font=dict(family="JetBrains Mono, monospace", color="#5a7a9a", size=10),
        title=dict(
            text=title,
            font=dict(family="Orbitron, sans-serif", color=CYAN, size=12),
            x=0.01, pad=dict(l=4, b=8),
        ),
        xaxis={**ax},
        yaxis={**ax},
        legend=dict(
            bgcolor="rgba(4,8,18,0.9)",
            bordercolor="rgba(0,212,255,0.18)",
            borderwidth=1,
            font=dict(family="JetBrains Mono", color="#7a9ab8", size=9),
        ),
        margin=dict(l=44, r=16, t=44, b=36),
        height=h,
    )
    return fig


PIPELINE_HTML = """
<div class="pl-wrap">
  <div class="pl-stage pl-bronze">
    <div class="pl-title c-bronze">⬡ Bronze</div>
    <div class="pl-item">IoT Tráfego (CET-SP)</div>
    <div class="pl-item">Qualidade do Ar (CETESB)</div>
    <div class="pl-item">GPS Ônibus (SPTrans)</div>
    <div class="pl-item">Ouvidoria Municipal</div>
    <div class="pl-item">Meteorologia (INMET)</div>
  </div>
  <div class="pl-arrow">▶</div>
  <div class="pl-stage pl-silver">
    <div class="pl-title c-silver">◆ Silver</div>
    <div class="pl-item">Timestamps → UTC</div>
    <div class="pl-item">IQAr calculado</div>
    <div class="pl-item">PII anonimizado (LGPD)</div>
    <div class="pl-item">Nulos imputados</div>
    <div class="pl-item">Enums padronizados</div>
  </div>
  <div class="pl-arrow">▶</div>
  <div class="pl-stage pl-gold">
    <div class="pl-title c-gold">◈ Gold</div>
    <div class="pl-item">Features normalizadas</div>
    <div class="pl-item">Lags 1h / 24h</div>
    <div class="pl-item">Geohash de risco</div>
    <div class="pl-item">One-hot encoding</div>
    <div class="pl-item">Labels para ML</div>
  </div>
  <div class="pl-arrow">▶</div>
  <div class="pl-stage pl-model">
    <div class="pl-title c-model">⚡ Modelos IA</div>
    <div class="pl-item">Isolation Forest</div>
    <div class="pl-item">XGBoost Demand</div>
    <div class="pl-item">DBSCAN Risk Map</div>
    <div class="pl-item">8 relatórios PNG</div>
  </div>
</div>
"""


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
<div class="sb-brand">
  <span class="sb-hex">⬡</span>
  <div class="sb-title">Metrópole SP</div>
  <div class="sb-sub">DATA PLATFORM v2.0</div>
</div>""", unsafe_allow_html=True)

    pagina = st.radio(
        "",
        [
            "Visão Geral",
            "Bronze — Dados Brutos",
            "Silver — Dados Limpos",
            "Gold — Features ML",
            "Modelos de IA",
            "🔬 Laboratório Jupyter",
            "Relatórios",
            "🗄️ Fontes de Dados",
            "🔗 Linhagem de Dados",
            "📊 Qualidade / SLA",
            "📅 Agendador",
            "📖 Dicionário de Dados",
        ],
        label_visibility="collapsed",
    )
    st.divider()

    if st.button("▶  RODAR PIPELINE", use_container_width=True, type="primary"):
        rodar_pipeline()
        st.rerun()

    if dados_existem():
        st.markdown(
            '<div class="status-live">'
            '<div class="dot-pulse"></div>PIPELINE ONLINE'
            '</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="status-offline">'
            '<div class="dot-offline"></div>SEM DADOS'
            '</div>',
            unsafe_allow_html=True)

    st.divider()

    # Modo apresentação
    if st.button("⛶  MODO APRESENTAÇÃO", use_container_width=True):
        st.session_state["present"] = not st.session_state.get("present", False)

    if st.session_state.get("present"):
        st.markdown(
            "<script>document.body.classList.add('present-mode')</script>",
            unsafe_allow_html=True)
        st.caption("Sidebar oculta. Clique novamente para sair.")
    else:
        st.markdown(
            "<script>document.body.classList.remove('present-mode')</script>",
            unsafe_allow_html=True)

    st.divider()
    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:.55rem;
            color:#1e3550;text-align:center;line-height:2;padding-bottom:8px">
  ENGENHARIA DE DADOS<br>
  ARQUITETURA MEDALLION<br>
  BRONZE · SILVER · GOLD<br>
  ── LGPD COMPLIANT ──
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
if not dados_existem() and pagina != "Visão Geral":
    st.warning("Nenhum dado encontrado. Clique em **RODAR PIPELINE** na barra lateral.")
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# PÁG 1 — VISÃO GERAL
# ════════════════════════════════════════════════════════════════════════════
if pagina == "Visão Geral":
    st.markdown('<div class="page-header"><div class="ph-tag">// Overview</div></div>',
                unsafe_allow_html=True)
    st.title("Metrópole SP — Data Platform")
    st.caption("Pipeline de Engenharia de Dados para Cidades Inteligentes  ·  Arquitetura Medallion")

    if not dados_existem():
        st.info("Nenhum dado processado ainda. Clique em **RODAR PIPELINE** na barra lateral.")
        st.stop()

    b_t = load(BRONZE_DIR / "iot_traffic_raw.parquet")
    b_a = load(BRONZE_DIR / "air_quality_raw.parquet")
    b_g = load(BRONZE_DIR / "gps_bus_raw.parquet")
    b_o = load(BRONZE_DIR / "ouvidoria_cdc_raw.parquet")
    b_w = load(BRONZE_DIR / "weather_inmet_raw.parquet")
    s_t = load(SILVER_DIR / "iot_traffic_clean.parquet")
    s_a = load(SILVER_DIR / "air_quality_clean.parquet")
    s_g = load(SILVER_DIR / "gps_bus_clean.parquet")
    s_o = load(SILVER_DIR / "ouvidoria_clean.parquet")
    g_a = load(GOLD_DIR   / "air_quality_with_anomalies.parquet")
    g_c = load(GOLD_DIR   / "risk_clusters_summary.parquet")
    g_b = load(GOLD_DIR   / "bus_demand_forecast.parquet")

    def n(df): return len(df) if df is not None else 0

    total_b = n(b_t)+n(b_a)+n(b_g)+n(b_o)+n(b_w)
    total_s = n(s_t)+n(s_a)+n(s_g)+n(s_o)
    total_g = n(g_a)+n(g_b)
    n_anom  = int(g_a["anomalia_pred"].sum()) if g_a is not None and "anomalia_pred" in g_a.columns else 0

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card("📥", "Bronze Layer",  f"{total_b:,}",  "registros brutos ingeridos", BRONZE_COL)
        + kpi_card("◆",  "Silver Layer",  f"{total_s:,}",  "registros limpos e validados", SILVER_COL)
        + kpi_card("◈",  "Gold Layer",    f"{total_g:,}",  "features prontas para ML", GOLD_C)
        + kpi_card("⚡", "Anomalias IA",  f"{n_anom}",     "Isolation Forest detectou", PINK)
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sec-div">// Arquitetura do Pipeline</div>', unsafe_allow_html=True)
    st.markdown(PIPELINE_HTML, unsafe_allow_html=True)

    st.markdown('<div class="sec-div">// Volume por Fonte e Camada</div>', unsafe_allow_html=True)
    fontes = ["IoT Tráfego", "Qualidade Ar", "GPS Ônibus", "Ouvidoria", "Meteorologia"]
    vol_b  = [n(b_t), n(b_a), n(b_g), n(b_o), n(b_w)]
    vol_s  = [n(s_t), n(s_a), n(s_g), n(s_o), 192]
    df_vol = pd.DataFrame({
        "Fonte":    fontes * 2,
        "Camada":   ["Bronze"]*5 + ["Silver"]*5,
        "Registros": vol_b + vol_s,
    })
    fig = px.bar(df_vol, x="Fonte", y="Registros", color="Camada", barmode="group",
                 color_discrete_map={"Bronze": BRONZE_COL, "Silver": SILVER_COL})
    fig.update_traces(marker_line_width=0, opacity=0.9)
    st.plotly_chart(cyber(fig, "Registros por Fonte"), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁG 2 — BRONZE
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "Bronze — Dados Brutos":
    st.markdown('<div class="page-header"><div class="ph-tag">// Camada Bronze · Raw Data</div></div>',
                unsafe_allow_html=True)
    st.title("Bronze — Dados Brutos")
    st.caption("Dados ingeridos SEM transformação. Preserva problemas reais das fontes originais.")

    fontes_map = {
        "IoT Sensores de Tráfego":  BRONZE_DIR / "iot_traffic_raw.parquet",
        "Qualidade do Ar (CETESB)": BRONZE_DIR / "air_quality_raw.parquet",
        "GPS de Ônibus (SPTrans)":  BRONZE_DIR / "gps_bus_raw.parquet",
        "Ouvidoria Municipal":      BRONZE_DIR / "ouvidoria_cdc_raw.parquet",
        "Meteorologia (INMET)":     BRONZE_DIR / "weather_inmet_raw.parquet",
    }
    problemas = {
        "IoT Sensores de Tráfego":  "timestamps sem timezone (BRT vs UTC) · contagem=-1 em manutenção · velocidade=null sem veículos",
        "Qualidade do Ar (CETESB)": "datas em DD/MM/YYYY · campos ausentes como '' · CAC001 mede CO em ppm em vez de µg/m³ · MP2.5 negativo",
        "GPS de Ônibus (SPTrans)":  "timestamp UNIX epoch sem fuso · enum lotação PT/EN inconsistente · (0,0) para veículos fora de serviço · motorista_id exposto (LGPD)",
        "Ouvidoria Municipal":      "CPF e telefone em texto livre (LGPD) · status PT/EN misturado · ~12% sem coordenadas · logradouros abreviados",
        "Meteorologia (INMET)":     "todos os campos chegam como string · ausentes representados por \"null\" em vez de NaN",
    }

    fonte = st.selectbox("Selecionar fonte de dados:", list(fontes_map.keys()))
    df = load(fontes_map[fonte])

    if df is not None:
        st.markdown(
            f'<p style="font-family:\'JetBrains Mono\',monospace;font-size:.72rem;'
            f'color:#6a4a2a;background:rgba(205,127,50,.06);border:1px solid rgba(205,127,50,.2);'
            f'border-left:3px solid #cd7f32;border-radius:0 6px 6px 0;padding:8px 12px;margin:8px 0 16px">'
            f'⚠  {problemas[fonte]}</p>',
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Registros",     f"{len(df):,}")
        c2.metric("Colunas",       f"{len(df.columns)}")
        c3.metric("Nulos totais",  f"{df.isna().sum().sum():,}")
        st.dataframe(df.head(60), use_container_width=True, height=360)
        ca, cb = st.columns(2)
        with ca:
            st.markdown('<div class="sec-div">// Tipos e Nulos</div>', unsafe_allow_html=True)
            tipos = pd.DataFrame({
                "Coluna": df.columns,
                "Tipo":   df.dtypes.astype(str).values,
                "Nulos":  df.isna().sum().values,
                "Nulos%": (df.isna().mean()*100).round(1).astype(str)+" %",
            })
            st.dataframe(tipos, use_container_width=True, height=300)
        with cb:
            st.markdown('<div class="sec-div">// Estatísticas</div>', unsafe_allow_html=True)
            st.dataframe(df.describe(include="all").T, use_container_width=True, height=300)


# ════════════════════════════════════════════════════════════════════════════
# PÁG 3 — SILVER
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "Silver — Dados Limpos":
    st.markdown('<div class="page-header"><div class="ph-tag">// Camada Silver · Clean Data</div></div>',
                unsafe_allow_html=True)
    st.title("Silver — Dados Limpos")

    tab_tr, tab_ar, tab_gps, tab_ouv = st.tabs([
        "🚗  Tráfego", "🌫️  Qualidade do Ar", "🚌  GPS Ônibus", "📋  Ouvidoria"
    ])

    with tab_tr:
        df = load(SILVER_DIR / "iot_traffic_clean.parquet")
        if df is not None:
            c1, c2, c3 = st.columns(3)
            c1.metric("Registros",   f"{len(df):,}")
            c2.metric("Sensores OK", f"{(df.qualidade=='OK').sum():,}" if "qualidade" in df.columns else "—")
            c3.metric("Manutenção",  f"{(df.qualidade=='SENSOR_MANUTENCAO').sum():,}" if "qualidade" in df.columns else "—")
            if "qualidade" in df.columns:
                vc = df["qualidade"].value_counts().reset_index()
                fig = px.pie(vc, names="qualidade", values="count",
                             color_discrete_sequence=NEON, hole=0.45)
                fig.update_traces(textfont_family="JetBrains Mono",
                                  textfont_size=10, textfont_color="white")
                st.plotly_chart(cyber(fig, "Status dos Sensores", 280), use_container_width=True)
            cols_show = ["sensor_id","timestamp_utc","via","sentido",
                         "contagem_veiculos","velocidade_kmh","qualidade"]
            st.dataframe(df[[c for c in cols_show if c in df.columns]].head(40),
                         use_container_width=True)

    with tab_ar:
        df = load(SILVER_DIR / "air_quality_clean.parquet")
        if df is not None:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Registros",   f"{len(df):,}")
            c2.metric("Estações",    f"{df.estacao_id.nunique()}" if "estacao_id" in df.columns else "—")
            c3.metric("IQAr Médio",  f"{df.iqar.mean():.1f}" if "iqar" in df.columns else "—")
            c4.metric("Alertas RUIM+", f"{(df.iqar>80).sum()}" if "iqar" in df.columns else "—")
            if "iqar" in df.columns and "timestamp_utc" in df.columns and "estacao_id" in df.columns:
                df["hora"] = pd.to_datetime(df["timestamp_utc"]).dt.floor("h")
                agg = df.groupby(["hora","estacao_id"])["iqar"].mean().reset_index()
                fig = px.line(agg, x="hora", y="iqar", color="estacao_id",
                              color_discrete_sequence=NEON)
                fig.update_traces(line_width=1.8)
                fig.add_hline(y=80, line_dash="dot", line_color=ORANGE, line_width=1,
                              annotation_text="Limite RUIM",
                              annotation_font=dict(color=ORANGE, family="JetBrains Mono", size=9))
                st.plotly_chart(cyber(fig, "IQAr por Estação", 320), use_container_width=True)
            ca, cb = st.columns(2)
            with ca:
                if "mp25" in df.columns:
                    fig2 = px.histogram(df, x="mp25", nbins=35,
                                        color_discrete_sequence=[PURPLE])
                    fig2.update_traces(marker_line_width=0, opacity=0.85)
                    fig2.add_vline(x=25, line_dash="dot", line_color=ORANGE, line_width=1,
                                   annotation_text="OMS",
                                   annotation_font=dict(color=ORANGE, family="JetBrains Mono", size=9))
                    st.plotly_chart(cyber(fig2, "Distribuição MP2.5", 260), use_container_width=True)
            with cb:
                if "iqar" in df.columns and "estacao_id" in df.columns:
                    fig3 = px.box(df, x="estacao_id", y="iqar", color="estacao_id",
                                  color_discrete_sequence=NEON)
                    fig3.update_traces(marker_size=3)
                    st.plotly_chart(cyber(fig3, "IQAr por Estação (boxplot)", 260),
                                    use_container_width=True)

    with tab_gps:
        df = load(SILVER_DIR / "gps_bus_clean.parquet")
        if df is not None:
            c1, c2, c3 = st.columns(3)
            c1.metric("Registros",    f"{len(df):,}")
            c2.metric("Ativos",       f"{df.ativo.sum():,}" if "ativo" in df.columns else "—")
            c3.metric("Fora Serviço", f"{(~df.ativo).sum():,}" if "ativo" in df.columns else "—")
            LOT_CLR = {"VAZIA":GREEN,"MEIA":"#8BC34A","CHEIA":GOLD_C,"LOTADA":PINK}
            ca, cb = st.columns(2)
            with ca:
                if "lotacao" in df.columns and "ativo" in df.columns:
                    vc = df[df.ativo]["lotacao"].value_counts().reset_index()
                    fig = px.bar(vc, x="lotacao", y="count", color="lotacao",
                                 color_discrete_map=LOT_CLR)
                    fig.update_traces(marker_line_width=0)
                    st.plotly_chart(cyber(fig, "Lotação dos Ônibus", 260), use_container_width=True)
            with cb:
                if all(c in df.columns for c in ["lat","lon","ativo","lotacao"]):
                    df_a = df[df.ativo & df.lat.notna() & df.lon.notna()]
                    fig2 = px.scatter(df_a, x="lon", y="lat", color="lotacao",
                                      color_discrete_map=LOT_CLR, opacity=0.65)
                    fig2.update_traces(marker=dict(size=5, line_width=0))
                    st.plotly_chart(cyber(fig2, "Localização dos Ônibus", 260),
                                    use_container_width=True)
            if "motorista_hash" in df.columns:
                st.info("**LGPD:** `motorista_id` substituído por `motorista_hash` (SHA-256 + salt)")
                st.dataframe(
                    df[["prefixo","linha","timestamp_utc","lotacao","ativo","motorista_hash"]].head(12),
                    use_container_width=True)

    with tab_ouv:
        df = load(SILVER_DIR / "ouvidoria_clean.parquet")
        if df is not None:
            c1, c2, c3 = st.columns(3)
            c1.metric("Ocorrências",   f"{len(df):,}")
            c2.metric("Bairros",       f"{df.bairro.nunique()}" if "bairro" in df.columns else "—")
            c3.metric("Geocodificadas",f"{int(df.coord_geocodificada.sum())}" if "coord_geocodificada" in df.columns else "—")
            ca, cb = st.columns(2)
            with ca:
                if "status" in df.columns:
                    vc = df["status"].value_counts().reset_index()
                    fig = px.pie(vc, names="status", values="count",
                                 color_discrete_sequence=[GREEN, GOLD_C, PINK], hole=0.45)
                    fig.update_traces(textfont_family="JetBrains Mono",
                                      textfont_size=10, textfont_color="white")
                    st.plotly_chart(cyber(fig, "Status das Ocorrências", 280),
                                    use_container_width=True)
            with cb:
                if "categoria" in df.columns:
                    vc2 = df["categoria"].value_counts().reset_index().head(8)
                    fig2 = px.bar(vc2, x="count", y="categoria", orientation="h",
                                  color="count",
                                  color_continuous_scale=[[0,PURPLE],[0.5,CYAN],[1,GREEN]])
                    fig2.update_layout(yaxis=dict(autorange="reversed"),
                                       coloraxis_showscale=False)
                    fig2.update_traces(marker_line_width=0)
                    st.plotly_chart(cyber(fig2, "Top Categorias", 280), use_container_width=True)
            if "lat" in df.columns and "lon" in df.columns:
                df_m = df.dropna(subset=["lat","lon"])
                fig3 = px.scatter(df_m, x="lon", y="lat", color="categoria",
                                  color_discrete_sequence=NEON, opacity=0.72,
                                  hover_data=[c for c in ["bairro","status","prioridade"]
                                              if c in df_m.columns])
                fig3.update_traces(marker=dict(size=7, line_width=0))
                st.plotly_chart(cyber(fig3, "Distribuição Geoespacial das Ocorrências", 360),
                                use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁG 4 — GOLD
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "Gold — Features ML":
    st.markdown('<div class="page-header"><div class="ph-tag">// Camada Gold · Feature Store</div></div>',
                unsafe_allow_html=True)
    st.title("Gold — Feature Store")

    tab1, tab2, tab3 = st.tabs(["🌫️  Anomalia de Ar", "🚌  Demanda Transporte", "📍  Mapa de Risco"])

    with tab1:
        df = load(GOLD_DIR / "air_quality_anomaly.parquet")
        if df is not None:
            st.info("Dataset para **Isolation Forest**: z-scores, StandardScaler, IQAr calculado por estação.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Registros", f"{len(df):,}")
            c2.metric("Features",  f"{len(df.columns)}")
            c3.metric("Anomalias (label)",
                      f"{int(df.label_anomalia.sum())}" if "label_anomalia" in df.columns else "—")
            tipos = pd.DataFrame({"Feature": df.columns, "Tipo": df.dtypes.astype(str).values})
            st.dataframe(tipos, use_container_width=True, height=300)

    with tab2:
        df = load(GOLD_DIR / "bus_demand_forecast.parquet")
        if df is not None:
            st.info("Dataset para **XGBoost**: lags 1h/24h, calendário, meteorologia, One-Hot linhas.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Registros", f"{len(df):,}")
            c2.metric("Features",  f"{len(df.columns)}")
            c3.metric("Target",    "lotacao_media (t+1h)")
            if "target" in df.columns and "hora_do_dia" in df.columns:
                fig = px.scatter(df, x="hora_do_dia", y="target",
                                 color="e_fim_semana" if "e_fim_semana" in df.columns else None,
                                 color_discrete_map={0: CYAN, 1: PURPLE},
                                 opacity=0.55)
                fig.update_traces(marker=dict(size=5, line_width=0))
                st.plotly_chart(cyber(fig, "Target (lotação) × Hora do Dia", 300),
                                use_container_width=True)

    with tab3:
        df    = load(GOLD_DIR / "occurrence_clusters.parquet")
        df_cl = load(GOLD_DIR / "risk_clusters_summary.parquet")
        if df is not None:
            st.info("Dataset para **DBSCAN**: coordenadas geo, categorias de risco, IQAr médio diário.")
            c1, c2 = st.columns(2)
            c1.metric("Ocorrências", f"{len(df):,}")
            c2.metric("Clusters",
                      f"{df_cl['cluster_id'].nunique()}" if df_cl is not None and "cluster_id" in df_cl.columns else "—")
            _CMAP = {"INFRAESTRUTURA":CYAN,"MEIO_AMBIENTE":GREEN,
                     "MOBILIDADE":ORANGE,"SEGURANCA":PINK,"OUTROS":"#607090"}
            if "lat" in df.columns and "lon" in df.columns and "categoria_l1" in df.columns:
                fig = px.scatter(df.dropna(subset=["lat","lon"]),
                                 x="lon", y="lat",
                                 color="categoria_l1",
                                 color_discrete_map=_CMAP,
                                 hover_data=[c for c in ["bairro","prioridade","cluster_id"] if c in df.columns],
                                 opacity=0.75)
                fig.update_traces(marker=dict(size=8, line_width=0))
                if df_cl is not None and "lon_centro" in df_cl.columns:
                    fig.add_scatter(
                        x=df_cl["lon_centro"], y=df_cl["lat_centro"],
                        mode="markers+text",
                        marker=dict(symbol="star", size=18, color=GOLD_C,
                                    line=dict(color="white", width=1)),
                        text=df_cl["cluster_id"].astype(str) if "cluster_id" in df_cl.columns else None,
                        textposition="top center",
                        textfont=dict(family="Orbitron", color=GOLD_C, size=9),
                        name="Centroide",
                    )
                st.plotly_chart(cyber(fig, "Clusters de Risco — DBSCAN", 380),
                                use_container_width=True)
            if df_cl is not None:
                st.markdown('<div class="sec-div">// Resumo dos Clusters</div>', unsafe_allow_html=True)
                st.dataframe(df_cl, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁG 5 — MODELOS
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "Modelos de IA":
    st.markdown('<div class="page-header"><div class="ph-tag">// AI / Machine Learning</div></div>',
                unsafe_allow_html=True)
    st.title("Modelos de Inteligência Artificial")

    tab_iso, tab_xgb, tab_db = st.tabs([
        "⚡  Isolation Forest", "📈  XGBoost Demand", "📍  DBSCAN Risk"
    ])

    def model_info(code_line, lines):
        inner = "".join(f'<div class="pl-item">{l}</div>' for l in lines)
        return (
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.75rem;'
            f'color:#5a7a9a;background:rgba(4,8,18,.6);border:1px solid var(--border);'
            f'border-radius:10px;padding:14px 16px;margin:0 0 16px;line-height:2">'
            f'<span style="color:{CYAN}">{code_line}</span><br>'
            f'{inner}</div>'
        )

    with tab_iso:
        st.markdown(model_info(
            "IsolationForest(n_estimators=150, contamination=0.05)",
            ["Treino: um modelo por estação de monitoramento",
             "Features: MP10 · MP2.5 · O3 · NO2 · CO · SO2 · temperatura · umidade · z-scores · hora"]
        ), unsafe_allow_html=True)
        df = load(GOLD_DIR / "air_quality_with_anomalies.parquet")
        if df is not None and "anomalia_pred" in df.columns:
            n_an = int(df["anomalia_pred"].sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("Total leituras",      f"{len(df):,}")
            c2.metric("Anomalias detectadas", f"{n_an}")
            c3.metric("Taxa de anomalia",    f"{n_an/len(df):.1%}")
            if "anomaly_score" in df.columns and "iqar" in df.columns:
                df["Status"] = df["anomalia_pred"].map({0:"Normal", 1:"Anomalia"})
                fig = px.scatter(
                    df.dropna(subset=["iqar","anomaly_score"]),
                    x="iqar", y="anomaly_score",
                    color="Status",
                    facet_col="estacao_id" if "estacao_id" in df.columns else None,
                    facet_col_wrap=4,
                    color_discrete_map={"Normal": CYAN, "Anomalia": PINK},
                    opacity=0.6,
                )
                fig.update_traces(marker=dict(size=5, line_width=0))
                fig.for_each_annotation(lambda a: a.update(
                    text=a.text.split("=")[-1],
                    font=dict(family="JetBrains Mono", color="#4a6a8a", size=9)
                ))
                st.plotly_chart(cyber(fig, "Anomaly Score vs IQAr por Estação", 420),
                                use_container_width=True)

    with tab_xgb:
        st.markdown(model_info(
            "XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.05)",
            ["Target: lotação média da linha na próxima hora",
             "Split temporal: 80% treino / 20% teste"]
        ), unsafe_allow_html=True)
        df_bus = load(GOLD_DIR / "bus_demand_forecast.parquet")
        if df_bus is not None and "target" in df_bus.columns:
            cut   = int(len(df_bus) * 0.80)
            df_te = df_bus.iloc[cut:].copy()
            df_te["idx"] = range(len(df_te))
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_te["idx"], y=df_te["target"],
                                     mode="lines", name="Real",
                                     line=dict(color=CYAN, width=1.8)))
            if "lag_1h" in df_te.columns:
                fig.add_trace(go.Scatter(x=df_te["idx"], y=df_te["lag_1h"],
                                         mode="lines", name="Lag 1h (baseline)",
                                         line=dict(color=ORANGE, width=1.2, dash="dot")))
            fig.add_trace(go.Scatter(x=df_te["idx"],
                                     y=df_te["target"].rolling(3, min_periods=1).mean(),
                                     mode="lines", name="Média móvel 3h",
                                     line=dict(color=GREEN, width=1.4, dash="dash")))
            st.plotly_chart(cyber(fig, "Lotação Real vs Baseline — Conjunto de Teste", 340),
                            use_container_width=True)
            linhas_cols = [c for c in df_bus.columns if c.startswith("linha_")]
            if linhas_cols:
                fi_df = pd.DataFrame({
                    "Linha":  [c.replace("linha_","Linha ") for c in linhas_cols],
                    "Volume": [float(df_bus[c].sum()) for c in linhas_cols],
                }).sort_values("Volume", ascending=True)
                fig2 = px.bar(fi_df, x="Volume", y="Linha", orientation="h",
                              color="Volume",
                              color_continuous_scale=[[0,PURPLE],[1,CYAN]])
                fig2.update_traces(marker_line_width=0)
                fig2.update_layout(coloraxis_showscale=False)
                st.plotly_chart(cyber(fig2, "Volume por Linha (Gold Dataset)", 300),
                                use_container_width=True)

    with tab_db:
        st.markdown(model_info(
            "DBSCAN(eps=0.008, min_samples=5, metric='euclidean')",
            ["Espaço de features: latitude × longitude",
             "Saída: clusters de concentração de ocorrências urbanas"]
        ), unsafe_allow_html=True)
        df    = load(GOLD_DIR / "occurrence_clusters.parquet")
        df_cl = load(GOLD_DIR / "risk_clusters_summary.parquet")
        if df is not None and "cluster_id" in df.columns:
            n_cl    = int(df[df.cluster_id >= 0]["cluster_id"].nunique())
            n_noise = int((df.cluster_id == -1).sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("Clusters detectados",  f"{n_cl}")
            c2.metric("Outliers (ruído)",      f"{n_noise}")
            c3.metric("Pontos clusterizados",  f"{int((df.cluster_id >= 0).sum()):,}")
            if df_cl is not None and "n_ocorrencias" in df_cl.columns:
                _CMAP2 = {"INFRAESTRUTURA":CYAN,"MEIO_AMBIENTE":GREEN,
                          "MOBILIDADE":ORANGE,"SEGURANCA":PINK,"OUTROS":"#607090"}
                fig = px.bar(df_cl,
                             x="cluster_id" if "cluster_id" in df_cl.columns else df_cl.index,
                             y="n_ocorrencias",
                             color="categoria_dom" if "categoria_dom" in df_cl.columns else None,
                             color_discrete_map=_CMAP2)
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(cyber(fig, "Ocorrências por Cluster", 300),
                                use_container_width=True)
                st.markdown('<div class="sec-div">// Tabela de Clusters</div>', unsafe_allow_html=True)
                st.dataframe(df_cl, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁG 6 — LABORATÓRIO JUPYTER
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "🔬 Laboratório Jupyter":
    import importlib, sys as _sys

    # Importa o runner de notebooks
    _nb_dir = str(BASE_DIR / "notebooks")
    if _nb_dir not in _sys.path:
        _sys.path.insert(0, _nb_dir)
    try:
        import runner as nb_runner
        importlib.reload(nb_runner)
        _runner_ok = True
    except ImportError:
        _runner_ok = False

    st.markdown('<div class="page-header"><div class="ph-tag">// Laboratório · Jupyter Integration</div></div>',
                unsafe_allow_html=True)
    st.title("Laboratório Jupyter")
    st.caption("Execute, visualize e sincronize os notebooks de análise por camada do pipeline.")

    # ── Auto-sync checker ─────────────────────────────────────────────────────
    if _runner_ok:
        if "auto_sync" not in st.session_state:
            st.session_state.auto_sync = False
        if "last_fp" not in st.session_state:
            st.session_state.last_fp = ""

        current_fp = nb_runner.data_fingerprint()
        data_changed = current_fp != st.session_state.last_fp and st.session_state.last_fp != ""

        if data_changed:
            st.markdown(
                '<div class="sync-alert">'
                '<div class="dot-offline" style="background:#ff6b00;box-shadow:0 0 6px #ff6b00"></div>'
                '⚡ Dados Gold atualizados — notebooks desatualizados. Clique em SINCRONIZAR.</div>',
                unsafe_allow_html=True)
            if st.session_state.auto_sync:
                with st.spinner("Auto-sync: executando notebooks..."):
                    nb_runner.execute_all()
                st.session_state.last_fp = current_fp
                st.rerun()
        elif st.session_state.last_fp != "":
            st.markdown(
                '<div class="sync-banner"><div class="dot-pulse"></div>'
                'Notebooks sincronizados com os dados Gold.</div>',
                unsafe_allow_html=True)

    # ── Controles ──────────────────────────────────────────────────────────────
    ca, cb, cc, cd = st.columns(4)
    with ca:
        if _runner_ok and st.button("⟳  SINCRONIZAR TUDO", use_container_width=True):
            ensure = nb_runner.ensure_notebooks()
            if not ensure:
                st.error("Falha ao criar notebooks.")
            else:
                prog = st.progress(0, "Executando notebooks...")
                results = {}
                for i, name in enumerate(["bronze", "silver", "gold"]):
                    prog.progress((i + 1) / 3, f"Executando {name}...")
                    results[name] = nb_runner.execute_notebook(name)
                st.session_state.last_fp = nb_runner.data_fingerprint()
                st.rerun()
    with cb:
        auto_val = st.toggle("Auto-Sync", value=st.session_state.get("auto_sync", False))
        st.session_state.auto_sync = auto_val
    with cc:
        _jup_running = _runner_ok and nb_runner.jupyter_running(8888)
        _jup_label   = "🟢  JUPYTER LAB ATIVO" if _jup_running else "🔬  INICIAR JUPYTER LAB"
        if st.button(_jup_label, use_container_width=True):
            if _runner_ok and not _jup_running:
                nb_runner.ensure_notebooks()
                with st.spinner("Iniciando Jupyter Lab..."):
                    nb_runner.start_jupyter_lab(8888)
                    import time as _t
                    for _ in range(20):          # até 20s
                        if nb_runner.jupyter_running(8888):
                            break
                        _t.sleep(1)
                st.session_state["jupyter_started"] = True
                st.rerun()

    # Banner com link (aparece quando Jupyter está rodando)
    _jup_up = _runner_ok and nb_runner.jupyter_running(8888)
    if _jup_up or st.session_state.get("jupyter_started"):
        st.markdown(
            '<div class="sync-banner">'
            '<div class="dot-pulse"></div>'
            '&nbsp;<b>Jupyter Lab ativo</b> — clique para abrir em nova aba &nbsp;→&nbsp; '
            '<a href="http://localhost:8888" target="_blank" '
            'style="color:#00d4ff;font-weight:700;text-decoration:underline;font-size:1.05em">'
            '🔬 localhost:8888 ↗</a></div>',
            unsafe_allow_html=True)
        if not _jup_up:
            st.warning("Jupyter Lab pode ainda estar iniciando. Aguarde alguns segundos e clique no link.")
    with cd:
        if _runner_ok and not (BASE_DIR / "notebooks" / "bronze_analysis.ipynb").exists():
            if st.button("⬡  GERAR NOTEBOOKS", use_container_width=True):
                nb_runner.ensure_notebooks()
                st.success("Notebooks criados!")
                st.rerun()

    st.divider()

    # ── Cards de status ────────────────────────────────────────────────────────
    status = nb_runner.load_status() if _runner_ok else {}
    LAYERS = [
        ("bronze", "📥 BRONZE", BRONZE_COL,
         "bronze_analysis.ipynb", "Exploração e diagnóstico de qualidade dos dados brutos."),
        ("silver", "◆ SILVER",  SILVER_COL,
         "silver_analysis.ipynb", "Validação das transformações e análise da camada limpa."),
        ("gold",   "◈ GOLD",    GOLD_C,
         "gold_analysis.ipynb",   "Feature engineering, correlações e desempenho dos modelos IA."),
    ]

    c1, c2, c3 = st.columns(3)
    for col, (key, label, color, fname, desc) in zip([c1, c2, c3], LAYERS):
        nb_path = BASE_DIR / "notebooks" / fname
        nb_st = status.get(key, {})
        st_text  = nb_st.get("status", "pending")
        st_class = {"ok": "nb-ok", "error": "nb-err", "pending": "nb-pend"}.get(st_text, "nb-pend")
        st_icon  = {"ok": "✅", "error": "❌", "pending": "⏳"}.get(st_text, "⏳")
        last_run = nb_st.get("last_run", "—")[:19].replace("T", " ") if nb_st.get("last_run") else "—"
        duration = nb_st.get("duration", "—")
        cells    = nb_st.get("cells", "—")

        with col:
            st.markdown(
                f'<div class="nb-card" style="--nc:{color}">'
                f'<div class="nb-title">{label}</div>'
                f'<div class="nb-stat">Arquivo: <span style="color:#d0e4ff">{fname}</span></div>'
                f'<div class="nb-stat">Status: <span class="{st_class}">{st_icon} {st_text.upper()}</span></div>'
                f'<div class="nb-stat">Última execução: {last_run}</div>'
                f'<div class="nb-stat">Duração: {duration}s &nbsp;|&nbsp; Células: {cells}</div>'
                f'<div class="nb-stat" style="margin-top:8px;color:#3a5a7a">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if _runner_ok and st.button(f"▶ Executar {label.split()[1]}", key=f"run_{key}",
                                         use_container_width=True):
                nb_runner.ensure_notebooks()
                with st.spinner(f"Executando {fname}..."):
                    res = nb_runner.execute_notebook(key)
                st.session_state.last_fp = nb_runner.data_fingerprint()
                if res["status"] == "ok":
                    st.success(f"Concluído em {res.get('duration',0)}s")
                else:
                    st.error(res.get("message", "Erro desconhecido")[:400])
                st.rerun()

    st.divider()

    # ── Visualizador de notebooks ──────────────────────────────────────────────
    st.markdown('<div class="sec-div">// Conteúdo dos Notebooks (última execução)</div>',
                unsafe_allow_html=True)

    tab_b, tab_s, tab_g = st.tabs(
        ["📥  Bronze Analysis", "◆  Silver Analysis", "◈  Gold Analysis"]
    )

    def render_notebook_cells(tab_key: str):
        """Renderiza as células de um notebook no Streamlit."""
        if not _runner_ok:
            st.warning("runner.py não disponível.")
            return
        cells = nb_runner.notebook_cells(tab_key)
        if not cells:
            st.info(f"Notebook '{tab_key}' ainda não foi executado ou não existe. "
                    "Clique em **SINCRONIZAR TUDO** para gerar e executar.")
            return

        import base64
        for i, cell in enumerate(cells):
            if cell.cell_type == "markdown":
                st.markdown(
                    f'<div class="nb-cell-md">{cell.source}</div>',
                    unsafe_allow_html=True)
            elif cell.cell_type == "code":
                if cell.source.strip():
                    st.markdown(
                        f'<div class="nb-cell-code">{cell.source}</div>',
                        unsafe_allow_html=True)
                for out in cell.get("outputs", []):
                    otype = out.get("output_type", "")
                    if otype == "stream":
                        txt = out.get("text", "")
                        if isinstance(txt, list):
                            txt = "".join(txt)
                        if txt.strip():
                            st.markdown(
                                f'<div class="nb-output">{txt[:3000]}</div>',
                                unsafe_allow_html=True)
                    elif otype in ("execute_result", "display_data"):
                        data = out.get("data", {})
                        if "image/png" in data:
                            img_b64 = data["image/png"]
                            if isinstance(img_b64, list):
                                img_b64 = "".join(img_b64)
                            img_bytes = base64.b64decode(img_b64)
                            st.image(img_bytes, use_container_width=True)
                        elif "text/html" in data:
                            html = data["text/html"]
                            if isinstance(html, list):
                                html = "".join(html)
                            st.components.v1.html(
                                f'<div style="background:#0d1526;color:#d0e4ff;padding:8px;'
                                f'font-family:JetBrains Mono,monospace;font-size:.78rem">{html}</div>',
                                height=250, scrolling=True)
                        elif "text/plain" in data:
                            txt = data["text/plain"]
                            if isinstance(txt, list):
                                txt = "".join(txt)
                            if txt.strip():
                                st.markdown(
                                    f'<div class="nb-output">{txt[:2000]}</div>',
                                    unsafe_allow_html=True)
                    elif otype == "error":
                        ename = out.get("ename", "Error")
                        evalue = out.get("evalue", "")
                        st.markdown(
                            f'<div class="nb-output-err">❌ {ename}: {evalue[:400]}</div>',
                            unsafe_allow_html=True)

    with tab_b: render_notebook_cells("bronze")
    with tab_s: render_notebook_cells("silver")
    with tab_g: render_notebook_cells("gold")


# ════════════════════════════════════════════════════════════════════════════
# PÁG 7 — RELATÓRIOS PERSONALIZÁVEIS
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "Relatórios":
    st.markdown('<div class="page-header"><div class="ph-tag">// Reports · Customizable</div></div>',
                unsafe_allow_html=True)
    st.title("Central de Relatórios")
    st.caption("Configure, filtre e exporte os relatórios do pipeline.")

    pngs = sorted(REPORTS_DIR.glob("*.png"))
    s_ar  = load(SILVER_DIR / "air_quality_clean.parquet")
    s_gps = load(SILVER_DIR / "gps_bus_clean.parquet")
    g_anom = load(GOLD_DIR  / "air_quality_with_anomalies.parquet")

    TITULOS = {
        "01_pipeline_volumes.png":    "Volume de Dados por Camada",
        "02_quality_heatmap.png":     "Heatmap de Qualidade — Silver",
        "03_iqar_timeseries.png":     "Série Temporal IQAr",
        "04_anomalias_ar.png":        "Anomalias — Isolation Forest",
        "05_demanda_transporte.png":  "Previsão de Demanda — XGBoost",
        "06_lotacao_onibus.png":      "Lotação dos Ônibus",
        "07_mapa_risco_clusters.png": "Mapa de Risco — DBSCAN",
        "08_ocorrencias_bairro.png":  "Ocorrências por Bairro",
    }

    # ── Painel de configuração ─────────────────────────────────────────────────
    with st.expander("⚙  CONFIGURAÇÕES DOS RELATÓRIOS", expanded=True):
        st.markdown('<div class="filter-title">// Personalizar Exibição</div>',
                    unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            opcoes_graficos = list(TITULOS.values())
            graficos_sel = st.multiselect(
                "Gráficos a exibir:",
                opcoes_graficos,
                default=opcoes_graficos,
            )
        with c2:
            layout_cols = st.selectbox("Layout de colunas:", [1, 2, 3], index=1)
        with c3:
            mostrar_estatisticas = st.toggle("Mostrar estatísticas", value=True)

        c4, c5 = st.columns(2)
        with c4:
            estacoes_disp = sorted(s_ar["estacao_id"].unique().tolist()) if s_ar is not None else []
            estacoes_sel = st.multiselect(
                "Estações de ar (filtro interativo):",
                estacoes_disp,
                default=estacoes_disp,
            )
        with c5:
            linhas_disp = sorted(s_gps["linha"].unique().tolist()) if s_gps is not None else []
            linhas_sel = st.multiselect(
                "Linhas de ônibus (filtro interativo):",
                linhas_disp,
                default=linhas_disp,
            )

        c6, c7 = st.columns(2)
        with c6:
            chart_type = st.selectbox("Tipo de gráfico (séries temporais):",
                                       ["Linha", "Área", "Barras"])
        with c7:
            paleta = st.selectbox("Paleta de cores:",
                                   ["Neon (padrão)", "Viridis", "Plasma", "Sunset", "Monocromático"])

    PALETAS = {
        "Neon (padrão)":  NEON,
        "Viridis":        ["#440154","#3b528b","#21918c","#5ec962","#fde725"],
        "Plasma":         ["#0d0887","#7201a8","#bd3786","#ed7953","#fdca26"],
        "Sunset":         ["#f7c59f","#eb6a5b","#bc2b4b","#7a1b54","#351543"],
        "Monocromático":  ["#00d4ff","#00aacc","#0088aa","#006688","#004466"],
    }
    cor_paleta = PALETAS.get(paleta, NEON)

    st.divider()

    # ── Gráficos interativos (filtrados) ──────────────────────────────────────
    if s_ar is not None and estacoes_sel:
        ar_f = s_ar[s_ar["estacao_id"].isin(estacoes_sel)]
        if len(ar_f) > 0:
            if "Série Temporal IQAr" in graficos_sel:
                st.markdown('<div class="sec-div">// IQAr — Série Temporal Interativa</div>',
                            unsafe_allow_html=True)
                ar_f2 = ar_f.copy()
                ar_f2["hora"] = pd.to_datetime(ar_f2["timestamp_utc"]).dt.floor("h")
                agg_f = ar_f2.groupby(["hora","estacao_id"])["iqar"].mean().reset_index()

                if chart_type == "Linha":
                    fig = px.line(agg_f, x="hora", y="iqar", color="estacao_id",
                                  color_discrete_sequence=cor_paleta)
                    fig.update_traces(line_width=1.8)
                elif chart_type == "Área":
                    fig = px.area(agg_f, x="hora", y="iqar", color="estacao_id",
                                  color_discrete_sequence=cor_paleta)
                else:
                    fig = px.bar(agg_f, x="hora", y="iqar", color="estacao_id",
                                 color_discrete_sequence=cor_paleta, barmode="group")

                fig.add_hline(y=80, line_dash="dot", line_color=ORANGE, line_width=1,
                              annotation_text="Limite RUIM",
                              annotation_font=dict(color=ORANGE, family="JetBrains Mono", size=9))
                st.plotly_chart(cyber(fig, "IQAr por Estação (filtrado)", 340),
                                use_container_width=True)

                if mostrar_estatisticas:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("IQAr Médio",  f"{ar_f['iqar'].mean():.1f}")
                    c2.metric("IQAr Máximo", f"{ar_f['iqar'].max():.1f}")
                    c3.metric("IQAr Mínimo", f"{ar_f['iqar'].min():.1f}")
                    c4.metric("Alertas",     f"{(ar_f['iqar'] > 80).sum()}")

            if "Anomalias — Isolation Forest" in graficos_sel and g_anom is not None:
                g_f = g_anom[g_anom["estacao_id"].isin(estacoes_sel)] if "estacao_id" in g_anom.columns else g_anom
                if len(g_f) > 0 and "anomalia_pred" in g_f.columns:
                    st.markdown('<div class="sec-div">// Anomalias Detectadas (filtrado)</div>',
                                unsafe_allow_html=True)
                    g_f2 = g_f.copy()
                    g_f2["Status"] = g_f2["anomalia_pred"].map({0:"Normal", 1:"Anomalia"})
                    fig2 = px.scatter(g_f2.dropna(subset=["iqar","anomaly_score"]),
                                      x="iqar", y="anomaly_score", color="Status",
                                      color_discrete_map={"Normal":cor_paleta[0], "Anomalia":PINK},
                                      opacity=0.6)
                    fig2.update_traces(marker=dict(size=5, line_width=0))
                    st.plotly_chart(cyber(fig2, "Anomaly Score vs IQAr", 300),
                                    use_container_width=True)

    if s_gps is not None and linhas_sel:
        gps_f = s_gps[s_gps["linha"].isin(linhas_sel) & s_gps["ativo"]]
        if len(gps_f) > 0 and "Lotação dos Ônibus" in graficos_sel:
            st.markdown('<div class="sec-div">// Lotação por Linha (filtrado)</div>',
                        unsafe_allow_html=True)
            agg_lot = gps_f.groupby(["linha","lotacao"]).size().reset_index(name="n")
            if chart_type == "Barras":
                fig3 = px.bar(agg_lot, x="linha", y="n", color="lotacao",
                              color_discrete_sequence=cor_paleta, barmode="group")
            else:
                fig3 = px.bar(agg_lot, x="linha", y="n", color="lotacao",
                              color_discrete_sequence=cor_paleta, barmode="stack")
            fig3.update_traces(marker_line_width=0)
            st.plotly_chart(cyber(fig3, "Lotação por Linha de Ônibus", 300),
                            use_container_width=True)

    st.divider()

    # ── Gráficos PNG estáticos ─────────────────────────────────────────────────
    st.markdown('<div class="sec-div">// Relatórios PNG — Pipeline (Estáticos)</div>',
                unsafe_allow_html=True)

    if not pngs:
        st.warning("Nenhum relatório encontrado. Execute o pipeline primeiro.")
    else:
        pngs_filtradas = [p for p in pngs if TITULOS.get(p.name, p.name) in graficos_sel]
        if not pngs_filtradas:
            st.info("Nenhum gráfico selecionado nos filtros acima.")
        else:
            cols = st.columns(layout_cols)
            for i, png in enumerate(pngs_filtradas):
                with cols[i % layout_cols]:
                    title = TITULOS.get(png.name, png.name)
                    st.markdown(
                        f'<div class="img-card">'
                        f'<div class="img-title">// {title}</div>',
                        unsafe_allow_html=True)
                    st.image(str(png), use_container_width=True)

                    # Download button
                    with open(str(png), "rb") as f:
                        img_bytes = f.read()
                    st.download_button(
                        label=f"⬇ Download",
                        data=img_bytes,
                        file_name=png.name,
                        mime="image/png",
                        key=f"dl_{png.name}",
                        use_container_width=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

    # ── Exportar PDF ───────────────────────────────────────────────────────────
    st.divider()
    st.markdown('<div class="sec-div">// Exportar Relatório em PDF</div>',
                unsafe_allow_html=True)

    if pngs_filtradas if pngs else []:
        if st.button("⬇  EXPORTAR RELATÓRIO PDF", use_container_width=False):
            try:
                import io
                from matplotlib.backends.backend_pdf import PdfPages
                import matplotlib.pyplot as plt
                import matplotlib.image as mpimg

                pdf_buf = io.BytesIO()
                with PdfPages(pdf_buf) as pdf:
                    # Capa
                    fig_capa, ax = plt.subplots(figsize=(11.7, 8.3))
                    fig_capa.patch.set_facecolor("#070b14")
                    ax.set_facecolor("#070b14")
                    ax.axis("off")
                    ax.text(0.5, 0.65, "Metrópole SP — Data Platform",
                            ha="center", va="center", fontsize=22, color="#00d4ff",
                            fontweight="bold", transform=ax.transAxes)
                    ax.text(0.5, 0.52, "Relatório de Engenharia de Dados",
                            ha="center", va="center", fontsize=14, color="#b8d4f0",
                            transform=ax.transAxes)
                    import datetime as _dt
                    ax.text(0.5, 0.40, f"Gerado em {_dt.datetime.now().strftime('%d/%m/%Y %H:%M')}",
                            ha="center", va="center", fontsize=10, color="#4a6a8a",
                            transform=ax.transAxes)
                    ax.text(0.5, 0.30, "Arquitetura Medallion  ·  Bronze → Silver → Gold",
                            ha="center", va="center", fontsize=11, color="#4a6a8a",
                            transform=ax.transAxes)
                    pdf.savefig(fig_capa, bbox_inches="tight")
                    plt.close(fig_capa)

                    for png in pngs_filtradas:
                        title = TITULOS.get(png.name, png.name)
                        img = mpimg.imread(str(png))
                        fig_img, ax2 = plt.subplots(figsize=(11.7, 8.3))
                        fig_img.patch.set_facecolor("#070b14")
                        ax2.set_facecolor("#070b14")
                        ax2.imshow(img)
                        ax2.axis("off")
                        ax2.set_title(title, color="#00d4ff", fontsize=12, pad=10)
                        pdf.savefig(fig_img, bbox_inches="tight", facecolor="#070b14")
                        plt.close(fig_img)

                pdf_buf.seek(0)
                st.download_button(
                    label="📄  Baixar PDF agora",
                    data=pdf_buf.read(),
                    file_name="metropole_sp_relatorio.pdf",
                    mime="application/pdf",
                    use_container_width=False,
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
    else:
        st.info("Execute o pipeline para gerar relatórios antes de exportar o PDF.")

# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# PÁG 8 — LINHAGEM DE DADOS
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "🔗 Linhagem de Dados":
    st.markdown('<div class="page-header"><div class="ph-tag">// Data Lineage</div></div>',
                unsafe_allow_html=True)
    st.title("Linhagem de Dados")
    st.caption("Rastreabilidade completa: da fonte bruta ao modelo de IA.")

    st.markdown('<div class="sec-div">// Fluxo de Dados — Sankey Interativo</div>',
                unsafe_allow_html=True)

    labels = [
        "IoT Tráfego", "Qualidade do Ar", "GPS Ônibus", "Ouvidoria", "Meteorologia",
        "Bronze: IoT", "Bronze: Ar", "Bronze: GPS", "Bronze: Ouvidoria", "Bronze: Clima",
        "Silver: Tráfego", "Silver: Ar", "Silver: GPS", "Silver: Ouvidoria", "Silver: Clima",
        "Gold: Ar/Anomalias", "Gold: Demanda Bus", "Gold: Risco Geo",
        "Isolation Forest", "XGBoost Demand", "DBSCAN Risk",
    ]
    source = [0,1,2,3,4, 5,6,7,8,9, 10,11,12,13,14, 11,14, 12,14, 13,11, 15,16,17]
    target = [5,6,7,8,9, 10,11,12,13,14, 15,15,16,17,16, 15,15, 16,16, 17,17, 18,19,20]
    value  = [5,5,5,5,5, 5,5,5,5,5, 4,3,4,3,2, 2,1, 2,2, 2,1, 3,4,3]
    node_colors = (["#cd7f32"]*5 + ["rgba(205,127,50,.6)"]*5 +
                   ["rgba(184,184,200,.7)"]*5 + ["rgba(255,215,0,.8)"]*3 +
                   ["rgba(123,47,255,.9)"]*3)

    fig_sank = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(pad=18, thickness=20,
                  line=dict(color="rgba(0,212,255,.2)", width=0.5),
                  label=labels, color=node_colors,
                  hovertemplate="<b>%{label}</b><extra></extra>"),
        link=dict(source=source, target=target, value=value,
                  color=["rgba(0,212,255,0.12)"]*len(source),
                  hovertemplate="<b>%{source.label}</b> → <b>%{target.label}</b><extra></extra>"),
    ))
    fig_sank.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono", color="#7a9ab8", size=10),
        height=520, margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_sank, use_container_width=True)

    st.markdown('<div class="sec-div">// Tabela de Linhagem — Origem → Destino</div>',
                unsafe_allow_html=True)
    lineage_rows = [
        ("IoT Tráfego (CET-SP)",    "iot_traffic_raw.parquet",   "iot_traffic_clean.parquet",  "—",                           "via Gold Ar"),
        ("Qualidade do Ar (CETESB)","air_quality_raw.parquet",   "air_quality_clean.parquet",  "air_quality_anomaly.parquet", "Isolation Forest"),
        ("GPS Ônibus (SPTrans)",    "gps_bus_raw.parquet",       "gps_bus_clean.parquet",      "bus_demand_forecast.parquet", "XGBoost Demand"),
        ("Ouvidoria Municipal",     "ouvidoria_cdc_raw.parquet", "ouvidoria_clean.parquet",    "occurrence_heatmap.parquet",  "DBSCAN Risk"),
        ("Meteorologia (INMET)",    "weather_inmet_raw.parquet", "weather_clean.parquet",      "bus_demand_forecast.parquet", "XGBoost (feature)"),
    ]
    tbl = ('<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;'
           'font-family:JetBrains Mono,monospace;font-size:.7rem"><thead><tr '
           'style="border-bottom:1px solid rgba(0,212,255,.3)">'
           + "".join(f'<th style="padding:8px 12px;text-align:left;color:#00d4ff;'
                     f'font-family:Orbitron,sans-serif;font-size:.6rem;letter-spacing:1.5px;'
                     f'text-transform:uppercase">{h}</th>'
                     for h in ["Fonte", "Bronze", "Silver", "Gold", "Modelo"])
           + "</tr></thead><tbody>")
    for i, (src, bro, sil, gol, mod) in enumerate(lineage_rows):
        bg = "rgba(0,212,255,.02)" if i % 2 == 0 else "transparent"
        tbl += (f'<tr style="background:{bg};border-bottom:1px solid rgba(0,212,255,.05)">'
                f'<td style="padding:7px 12px;color:#d0e4ff">{src}</td>'
                f'<td style="padding:7px 12px;color:#cd7f32">{bro}</td>'
                f'<td style="padding:7px 12px;color:#b8b8c8">{sil}</td>'
                f'<td style="padding:7px 12px;color:#ffd700">{gol}</td>'
                f'<td style="padding:7px 12px;color:#9b6fff">{mod}</td></tr>')
    tbl += "</tbody></table></div>"
    st.markdown(tbl, unsafe_allow_html=True)

    st.markdown('<div class="sec-div">// Transformações por Camada & Alinhamento com IA</div>',
                unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["Bronze → Silver", "Silver → Gold", "Gold → Modelos", "🎯 Alinhamento Pipeline → IA"])

    with t1:
        for fonte, ops in {
            "IoT Tráfego":     ["Timestamp → UTC", "Velocidade m/s → km/h", "Nulos imputados com mediana"],
            "Qualidade do Ar": ["IQAr calculado (PM2.5, O3, NO2)", "Estações <50% dados removidas"],
            "GPS Ônibus":      ["motorista_id → SHA-256 (LGPD)", "Coordenadas validadas", "Lotação → enum"],
            "Ouvidoria":       ["PII removido (regex)", "CEP padronizado", "Geocoding simulado"],
            "Meteorologia":    ["Precipitação negativa → 0", "Temperatura Kelvin → Celsius"],
        }.items():
            st.markdown(f"**{fonte}**")
            for op in ops: st.markdown(f"&nbsp;&nbsp;`→` {op}")

    with t2:
        for camada, ops in {
            "Gold Ar":   ["Join Meteorologia por hora+estação", "Lags 1h e 24h", "IQAr normalizado"],
            "Gold Bus":  ["Agrupamento por linha+hora", "Join temperatura/precipitação", "One-hot dia_semana"],
            "Gold Risk": ["Geohash H3 nível 7", "Contagem ocorrências/célula", "Score risco composto"],
        }.items():
            st.markdown(f"**{camada}**")
            for op in ops: st.markdown(f"&nbsp;&nbsp;`→` {op}")

    with t3:
        for modelo, info in {
            "Isolation Forest": ["Input: Gold Ar (20+ features)", "Output: anomalia_pred + anomaly_score"],
            "XGBoost Demand":   ["Input: Gold Bus (hora, linha, clima)", "MAE e R² calculados"],
            "DBSCAN Risk":      ["Input: Gold Risk (lat, lon)", "Output: cluster_id por ponto"],
        }.items():
            st.markdown(f"**{modelo}**")
            for item in info: st.markdown(f"&nbsp;&nbsp;`→` {item}")

    with t4:
        st.markdown("### Por que cada transformação existe — rastreabilidade até os requisitos dos algoritmos")
        st.markdown("---")

        # ── Isolation Forest ──────────────────────────────────────────────────
        st.markdown(f'<div class="nb-card" style="--nc:{CYAN};margin-bottom:16px">'
                    f'<div class="nb-title">Isolation Forest — Anomalias de Qualidade do Ar</div>'
                    f'</div>', unsafe_allow_html=True)

        req_iso = [
            ("Sem valores nulos nas features",
             "Silver: nulos em pm25/no2 imputados com mediana da estação",
             "Isolation Forest falha com NaN — sklearn levanta ValueError"),
            ("Escala numérica comparável entre features",
             "Gold: IQAr normalizado [0,1] via MinMaxScaler; poluentes z-score",
             "IF usa distância euclidiana — features em escalas diferentes distorcem o score"),
            ("Contexto temporal capturado",
             "Gold: lags 1h e 24h de PM2.5 e NO2 como features adicionais",
             "Anomalias de ar têm padrão temporal; sem lag o modelo não captura picos sazonais"),
            ("Variáveis externas (confounders)",
             "Gold: join com temperatura e umidade (Meteorologia)",
             "Alta temperatura e baixa umidade são causas naturais de IQAr elevado — sem elas geram falsos positivos"),
            ("Ausência de categorias — input 100% numérico",
             "Silver→Gold: lotacao e tipo_via convertidos para one-hot ou excluídos do Gold Ar",
             "IF aceita apenas float64; strings causam TypeError"),
        ]

        for req, impl, why in req_iso:
            st.markdown(
                f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;'
                f'padding:10px 14px;border-bottom:1px solid rgba(0,212,255,.08);'
                f'font-family:JetBrains Mono,monospace;font-size:.7rem;margin-bottom:4px">'
                f'<div><span style="color:#4a6a8a;font-size:.6rem;letter-spacing:1px">REQUISITO DO ALGORITMO</span><br>'
                f'<span style="color:#d0e4ff">{req}</span></div>'
                f'<div><span style="color:#4a6a8a;font-size:.6rem;letter-spacing:1px">IMPLEMENTADO NO PIPELINE</span><br>'
                f'<span style="color:#00d4ff">{impl}</span></div>'
                f'<div><span style="color:#4a6a8a;font-size:.6rem;letter-spacing:1px">CONSEQUÊNCIA SE IGNORADO</span><br>'
                f'<span style="color:#ff6b00">{why}</span></div>'
                f'</div>',
                unsafe_allow_html=True)

        st.markdown("---")

        # ── XGBoost ───────────────────────────────────────────────────────────
        st.markdown(f'<div class="nb-card" style="--nc:{GREEN};margin-bottom:16px">'
                    f'<div class="nb-title">XGBoost — Previsão de Demanda de Transporte</div>'
                    f'</div>', unsafe_allow_html=True)

        req_xgb = [
            ("Variáveis categóricas codificadas numericamente",
             "Gold: `dia_semana` one-hot (seg=0…dom=6); `linha` label-encoded",
             "XGBoost 2.x aceita categorias nativas, mas o pipeline usa encoding explícito para auditabilidade"),
            ("Feature de sazonalidade intradiária",
             "Gold: coluna `hora` [0–23] extraída do timestamp_utc",
             "Demanda tem pico às 7h e 18h — sem hora o modelo prevê média flat"),
            ("Features climáticas exógenas",
             "Gold: join por (data+hora) com temperatura e precipitação do INMET",
             "Chuva reduz demanda ~15%; sem join o modelo subestima variância R²"),
            ("Sem nulos no target",
             "Silver: linhas com `ativo=False` removidas; contagem mínima 1",
             "XGBoost ignora linhas com target NaN, reduzindo o dataset de treino silenciosamente"),
            ("Particionamento por dia_semana",
             "Gold particionado por `dia_semana` (Hive-style)",
             "Permite treinar modelos dia-específicos sem carregar todo o dataset em memória"),
        ]

        for req, impl, why in req_xgb:
            st.markdown(
                f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;'
                f'padding:10px 14px;border-bottom:1px solid rgba(0,255,136,.08);'
                f'font-family:JetBrains Mono,monospace;font-size:.7rem;margin-bottom:4px">'
                f'<div><span style="color:#4a6a8a;font-size:.6rem;letter-spacing:1px">REQUISITO DO ALGORITMO</span><br>'
                f'<span style="color:#d0e4ff">{req}</span></div>'
                f'<div><span style="color:#4a6a8a;font-size:.6rem;letter-spacing:1px">IMPLEMENTADO NO PIPELINE</span><br>'
                f'<span style="color:#00ff88">{impl}</span></div>'
                f'<div><span style="color:#4a6a8a;font-size:.6rem;letter-spacing:1px">CONSEQUÊNCIA SE IGNORADO</span><br>'
                f'<span style="color:#ff6b00">{why}</span></div>'
                f'</div>',
                unsafe_allow_html=True)

        st.markdown("---")

        # ── DBSCAN ────────────────────────────────────────────────────────────
        st.markdown(f'<div class="nb-card" style="--nc:{PURPLE};margin-bottom:16px">'
                    f'<div class="nb-title">DBSCAN — Mapa de Risco Geoespacial</div>'
                    f'</div>', unsafe_allow_html=True)

        req_dbs = [
            ("Coordenadas geográficas válidas e na mesma projeção",
             "Silver: lat/lon validadas [-90,90]×[-180,180]; datum WGS84",
             "DBSCAN com eps em km requer coordenadas reais — pontos (0,0) formam cluster falso no oceano"),
            ("Escala física consistente para o parâmetro eps",
             "Gold: eps=0.5 calibrado para ~500m em coordenadas decimais de SP",
             "eps em graus ≠ km; 0.5° ≈ 55 km em SP — clusters cobririam a cidade inteira"),
            ("Feature de intensidade para score de risco",
             "Gold: `risk_score = contagem_ocorrencias * peso_tipo + iqar_bairro * 0.3`",
             "Sem score, DBSCAN agrupa por densidade geográfica apenas, ignorando severidade"),
            ("Ausência de outliers de geocodificação",
             "Silver: coordenadas com erro >50km do centroide do bairro removidas",
             "Um único ponto em outra cidade cria cluster isolado, distorcendo o mapa de risco"),
            ("Particionamento Bronze por regiao",
             "Bronze GPS particionado por `regiao` — alimenta Gold Risk por área",
             "Sem partição, consulta de risco de uma região carrega GPS de toda SP desnecessariamente"),
        ]

        for req, impl, why in req_dbs:
            st.markdown(
                f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;'
                f'padding:10px 14px;border-bottom:1px solid rgba(123,47,255,.08);'
                f'font-family:JetBrains Mono,monospace;font-size:.7rem;margin-bottom:4px">'
                f'<div><span style="color:#4a6a8a;font-size:.6rem;letter-spacing:1px">REQUISITO DO ALGORITMO</span><br>'
                f'<span style="color:#d0e4ff">{req}</span></div>'
                f'<div><span style="color:#4a6a8a;font-size:.6rem;letter-spacing:1px">IMPLEMENTADO NO PIPELINE</span><br>'
                f'<span style="color:#9b6fff">{impl}</span></div>'
                f'<div><span style="color:#4a6a8a;font-size:.6rem;letter-spacing:1px">CONSEQUÊNCIA SE IGNORADO</span><br>'
                f'<span style="color:#ff6b00">{why}</span></div>'
                f'</div>',
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁG 9 — QUALIDADE / SLA
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "📊 Qualidade / SLA":
    st.markdown('<div class="page-header"><div class="ph-tag">// Data Quality · SLA</div></div>',
                unsafe_allow_html=True)
    st.title("Qualidade de Dados & SLA")
    st.caption("Métricas de qualidade por camada com indicadores de conformidade.")

    SLA_THRESHOLD = 0.90

    def quality_metrics(df, nome, cor):
        if df is None:
            return None
        total = len(df)
        nulos = int(df.isnull().sum().sum())
        pct   = nulos / max(total * len(df.columns), 1)
        dups  = int(df.duplicated().sum())
        score = max(0.0, 1.0 - pct * 3 - dups / max(total, 1))
        return {"nome": nome, "cor": cor, "total": total, "colunas": len(df.columns),
                "nulos": nulos, "pct_nulos": pct, "duplicatas": dups, "score": round(score, 4)}

    def render_layer(sources, title):
        st.markdown(f'<div class="sec-div">// {title}</div>', unsafe_allow_html=True)
        cols = st.columns(len(sources))
        scores = []
        for col, (df, nome, cor) in zip(cols, sources):
            m = quality_metrics(df, nome, cor)
            if m is None:
                with col:
                    st.markdown(f'<div class="nb-card" style="--nc:{ORANGE}"><div class="nb-title">'
                                f'{nome}</div><div class="nb-stat nb-pend">Sem dados</div></div>',
                                unsafe_allow_html=True)
                continue
            scores.append(m["score"])
            ok  = m["score"] >= SLA_THRESHOLD
            cls = "sla-ok" if ok else ("sla-warn" if m["score"] >= 0.75 else "sla-fail")
            lbl = "PASS" if ok else ("WARN" if m["score"] >= 0.75 else "FAIL")
            with col:
                st.markdown(
                    f'<div class="nb-card" style="--nc:{cor}">'
                    f'<div class="nb-title">{nome}</div>'
                    f'<div class="nb-stat">Registros: <b style="color:#d0e4ff">{m["total"]:,}</b></div>'
                    f'<div class="nb-stat">Colunas: <b style="color:#d0e4ff">{m["colunas"]}</b></div>'
                    f'<div class="nb-stat">Nulos: <b style="color:{"#ff6b00" if m["nulos"] else "#00ff88"}">{m["nulos"]:,}</b> ({m["pct_nulos"]:.1%})</div>'
                    f'<div class="nb-stat">Dups: <b style="color:{"#ff6b00" if m["duplicatas"] else "#00ff88"}">{m["duplicatas"]:,}</b></div>'
                    f'<div class="nb-stat" style="margin-top:10px">Score: <b style="font-size:1.1em;color:{cor}">{m["score"]:.1%}</b></div>'
                    f'<div class="nb-stat">SLA 90%: <span class="{cls}">▌ {lbl}</span></div>'
                    f'</div>', unsafe_allow_html=True)
        return scores

    b_sc = render_layer([
        (load(BRONZE_DIR / "iot_traffic_raw.parquet"),    "IoT Tráfego",     BRONZE_COL),
        (load(BRONZE_DIR / "air_quality_raw.parquet"),    "Qualidade do Ar", BRONZE_COL),
        (load(BRONZE_DIR / "gps_bus_raw.parquet"),        "GPS Ônibus",      BRONZE_COL),
        (load(BRONZE_DIR / "ouvidoria_cdc_raw.parquet"),  "Ouvidoria",       BRONZE_COL),
        (load(BRONZE_DIR / "weather_inmet_raw.parquet"),  "Meteorologia",    BRONZE_COL),
    ], "Camada Bronze — Dados Brutos")

    s_sc = render_layer([
        (load(SILVER_DIR / "iot_traffic_clean.parquet"),  "IoT Tráfego",     SILVER_COL),
        (load(SILVER_DIR / "air_quality_clean.parquet"),  "Qualidade do Ar", SILVER_COL),
        (load(SILVER_DIR / "gps_bus_clean.parquet"),      "GPS Ônibus",      SILVER_COL),
        (load(SILVER_DIR / "ouvidoria_clean.parquet"),    "Ouvidoria",       SILVER_COL),
        (load(SILVER_DIR / "weather_clean.parquet"),      "Meteorologia",    SILVER_COL),
    ], "Camada Silver — Dados Limpos")

    g_sc = render_layer([
        (load(GOLD_DIR / "air_quality_with_anomalies.parquet"), "Air Anomalias", GOLD_C),
        (load(GOLD_DIR / "bus_demand_forecast.parquet"),        "Bus Demand",    GOLD_C),
        (load(GOLD_DIR / "occurrence_clusters.parquet"),        "Risco Geo",     GOLD_C),
    ], "Camada Gold — Features ML")

    st.markdown('<div class="sec-div">// Score Geral por Camada</div>', unsafe_allow_html=True)
    all_names  = (["IoT Tráfego","Qualidade do Ar","GPS Ônibus","Ouvidoria","Meteorologia"] * 2
                  + ["Air Anomalias","Bus Demand","Risco Geo"])
    all_scores = b_sc + s_sc + g_sc
    all_layers = ["Bronze"]*5 + ["Silver"]*5 + ["Gold"]*3

    if all_scores:
        df_q = pd.DataFrame({
            "Fonte": all_names[:len(all_scores)],
            "Score": all_scores,
            "Camada": all_layers[:len(all_scores)],
        })
        fig_q = px.bar(df_q, x="Fonte", y="Score", color="Camada",
                       color_discrete_map={"Bronze": BRONZE_COL, "Silver": SILVER_COL, "Gold": GOLD_C},
                       text="Score")
        fig_q.update_traces(texttemplate="%{text:.1%}", textposition="outside", marker_line_width=0)
        fig_q.add_hline(y=SLA_THRESHOLD, line_dash="dot", line_color=GREEN, line_width=1.5,
                        annotation_text="SLA 90%",
                        annotation_font=dict(color=GREEN, family="JetBrains Mono", size=9))
        fig_q.update_layout(yaxis_range=[0, 1.12], yaxis_tickformat=".0%")
        st.plotly_chart(cyber(fig_q, "Score de Qualidade por Dataset", 360),
                        use_container_width=True)

    # Heatmap de nulos Silver
    st.markdown('<div class="sec-div">// Heatmap de Nulos — Camada Silver</div>',
                unsafe_allow_html=True)
    import numpy as _np
    silver_dfs = {
        "IoT Tráfego":     load(SILVER_DIR / "iot_traffic_clean.parquet"),
        "Qualidade do Ar": load(SILVER_DIR / "air_quality_clean.parquet"),
        "GPS Ônibus":      load(SILVER_DIR / "gps_bus_clean.parquet"),
        "Ouvidoria":       load(SILVER_DIR / "ouvidoria_clean.parquet"),
        "Meteorologia":    load(SILVER_DIR / "weather_clean.parquet"),
    }
    silver_dfs = {k: v for k, v in silver_dfs.items() if v is not None}
    if silver_dfs:
        n_cols = 8
        col_labels = list(list(silver_dfs.values())[0].columns[:n_cols])
        rows = []
        for df in silver_dfs.values():
            row = [df[c].isnull().mean() if c in df.columns else float("nan")
                   for c in col_labels]
            rows.append(row)
        heat = _np.array(rows, dtype=float)
        fig_heat = go.Figure(go.Heatmap(
            z=heat, x=col_labels, y=list(silver_dfs.keys()),
            colorscale=[[0,"#0d1526"],[0.5,"#ff6b00"],[1,"#ff2d78"]],
            text=[[f"{v:.1%}" if not _np.isnan(v) else "" for v in row] for row in heat],
            texttemplate="%{text}",
            textfont=dict(family="JetBrains Mono", size=8),
            zmin=0, zmax=0.2,
        ))
        st.plotly_chart(cyber(fig_heat, "% Nulos por Coluna (Silver)", 280),
                        use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁG 10 — AGENDADOR
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "📅 Agendador":
    import json as _json
    from datetime import datetime as _dt, timedelta as _td

    st.markdown('<div class="page-header"><div class="ph-tag">// Pipeline Scheduler</div></div>',
                unsafe_allow_html=True)
    st.title("Agendador de Pipeline")
    st.caption("Configure execuções automáticas e visualize o histórico.")

    _LOG_DIR  = BASE_DIR / "logs"
    _LOG_DIR.mkdir(exist_ok=True)
    SCHED_CFG  = _LOG_DIR / "scheduler.json"
    SCHED_HIST = _LOG_DIR / "scheduler_history.json"

    def _load_cfg():
        if SCHED_CFG.exists():
            try: return _json.loads(SCHED_CFG.read_text(encoding="utf-8"))
            except Exception: pass
        return {"enabled": False, "interval_min": 60, "next_run": None}

    def _save_cfg(c):
        SCHED_CFG.write_text(_json.dumps(c, indent=2), encoding="utf-8")

    def _load_hist():
        if SCHED_HIST.exists():
            try: return _json.loads(SCHED_HIST.read_text(encoding="utf-8"))
            except Exception: pass
        return []

    def _add_hist(entry):
        h = _load_hist(); h.insert(0, entry)
        SCHED_HIST.write_text(_json.dumps(h[:50], indent=2), encoding="utf-8")

    cfg = _load_cfg()

    # Configuração
    st.markdown('<div class="sec-div">// Configuração do Agendador</div>', unsafe_allow_html=True)
    ca, cb, cc = st.columns([1, 1, 2])
    with ca:
        enabled = st.toggle("Habilitar", value=cfg.get("enabled", False))
    with cb:
        opts = [15, 30, 60, 120, 360, 720, 1440]
        cur  = cfg.get("interval_min", 60)
        idx  = opts.index(cur) if cur in opts else 2
        interval = st.selectbox("Intervalo", opts, index=idx,
                                format_func=lambda x: f"{x}min" if x < 60 else f"{x//60}h")
    with cc:
        if enabled and cfg.get("next_run"):
            try:
                nxt = _dt.fromisoformat(cfg["next_run"])
                delta = nxt - _dt.now()
                if delta.total_seconds() > 0:
                    mins = int(delta.total_seconds() // 60)
                    secs = int(delta.total_seconds() % 60)
                    st.info(f"Proxima execucao em {mins}min {secs}s  ({nxt.strftime('%H:%M:%S')})")
                else:
                    st.warning("Prazo passou — sera executado ao salvar.")
            except Exception: pass

    if st.button("SALVAR CONFIGURACAO", use_container_width=False):
        nxt = (_dt.now() + _td(minutes=interval)).isoformat() if enabled else None
        _save_cfg({"enabled": enabled, "interval_min": interval, "next_run": nxt})
        st.success(f"Salvo! {'Proxima: ' + nxt[:19] if nxt else 'Desabilitado'}")
        st.rerun()

    # Verificar se passou do prazo
    cfg = _load_cfg()
    if cfg.get("enabled") and cfg.get("next_run"):
        try:
            nxt = _dt.fromisoformat(cfg["next_run"])
            if _dt.now() >= nxt:
                st.info("Executando pipeline agendado...")
                t0_s = _dt.now()
                r = subprocess.run([sys.executable, "main.py"],
                                   capture_output=True, text=True, cwd=str(BASE_DIR))
                elapsed_s = round((_dt.now() - t0_s).total_seconds(), 1)
                _add_hist({"timestamp": t0_s.isoformat(),
                           "status": "ok" if r.returncode == 0 else "error",
                           "elapsed": elapsed_s, "trigger": "scheduled"})
                nxt2 = (_dt.now() + _td(minutes=cfg["interval_min"])).isoformat()
                _save_cfg({**cfg, "next_run": nxt2})
                st.cache_data.clear()
                st.success(f"Pipeline agendado concluido em {elapsed_s}s") if r.returncode == 0 \
                    else st.error(f"Pipeline falhou ({r.returncode})")
                st.rerun()
        except Exception: pass

    # Executar agora
    st.markdown('<div class="sec-div">// Executar Manualmente</div>', unsafe_allow_html=True)
    if st.button("EXECUTAR PIPELINE AGORA", use_container_width=False, type="primary"):
        t0_m = _dt.now()
        _add_hist({"timestamp": t0_m.isoformat(), "status": "running", "trigger": "manual"})
        rodar_pipeline()
        elapsed_m = round((_dt.now() - t0_m).total_seconds(), 1)
        h2 = _load_hist()
        if h2: h2[0].update({"status": "ok", "elapsed": elapsed_m})
        SCHED_HIST.write_text(_json.dumps(h2[:50], indent=2), encoding="utf-8")
        st.cache_data.clear(); st.rerun()

    # Histórico
    st.markdown('<div class="sec-div">// Historico de Execucoes</div>', unsafe_allow_html=True)
    hist = _load_hist()
    if not hist:
        st.info("Nenhuma execucao registrada.")
    else:
        df_h = pd.DataFrame(hist)
        df_h["timestamp"] = pd.to_datetime(df_h["timestamp"]).dt.strftime("%d/%m/%Y %H:%M:%S")
        df_h["icon"] = df_h["status"].map({"ok": "OK", "error": "ERRO", "running": "..."})
        df_h["dur"]  = df_h.get("elapsed", pd.Series(dtype=float)).apply(
            lambda x: f"{x:.1f}s" if pd.notna(x) else "—")

        rows_h = ""
        for i, row in df_h.head(20).iterrows():
            st_v  = row.get("status", "?")
            color = "#00ff88" if st_v == "ok" else ("#ff2d78" if st_v == "error" else "#ff6b00")
            bg    = "rgba(0,212,255,.02)" if i % 2 == 0 else "transparent"
            rows_h += (f'<tr style="background:{bg};border-bottom:1px solid rgba(0,212,255,.05)">'
                       f'<td style="padding:6px 12px;color:#2a3a5a">{i+1}</td>'
                       f'<td style="padding:6px 12px;color:#d0e4ff">{row.get("timestamp","—")}</td>'
                       f'<td style="padding:6px 12px;color:{color}">{row.get("icon","?")} {st_v.upper()}</td>'
                       f'<td style="padding:6px 12px;color:#7a9ab8">{row.get("dur","—")}</td>'
                       f'<td style="padding:6px 12px;color:#4a6a8a">{row.get("trigger","—")}</td></tr>')

        st.markdown(
            '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;'
            'font-family:JetBrains Mono,monospace;font-size:.72rem"><thead><tr '
            'style="border-bottom:1px solid rgba(0,212,255,.3)">'
            + "".join(f'<th style="padding:8px 12px;color:#00d4ff;font-family:Orbitron,sans-serif;'
                      f'font-size:.58rem;letter-spacing:1.5px;text-transform:uppercase;text-align:left">{h}</th>'
                      for h in ["#", "Timestamp", "Status", "Duração", "Trigger"])
            + f"</tr></thead><tbody>{rows_h}</tbody></table></div>",
            unsafe_allow_html=True)

        if "elapsed" in df_h.columns:
            df_ok = df_h[df_h["status"] == "ok"].copy()
            df_ok["elapsed"] = pd.to_numeric(df_ok.get("elapsed", pd.Series()), errors="coerce")
            if len(df_ok) > 1 and df_ok["elapsed"].notna().any():
                fig_d = px.bar(df_ok.head(15), x="timestamp", y="elapsed",
                               color_discrete_sequence=[CYAN])
                fig_d.update_traces(marker_line_width=0)
                st.plotly_chart(cyber(fig_d, "Duracao das Execucoes (s)", 260),
                                use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁG 11 — DICIONÁRIO DE DADOS
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "📖 Dicionário de Dados":
    st.markdown('<div class="page-header"><div class="ph-tag">// Data Dictionary</div></div>',
                unsafe_allow_html=True)
    st.title("Dicionário de Dados")
    st.caption("Schemas completos de todas as tabelas — Bronze, Silver e Gold.")

    SCHEMAS = {
        "Bronze": {
            "iot_traffic_raw": [
                ("sensor_id",        "string",  "Identificador único do sensor IoT"),
                ("timestamp",        "datetime","Timestamp local do sensor"),
                ("velocidade_ms",    "float",   "Velocidade em m/s"),
                ("ocupacao_pct",     "float",   "Ocupação da via em %"),
                ("contagem_veiculos","int",      "Contagem de veículos na janela"),
                ("tipo_via",         "string",  "Classificação: arterial/coletora/local"),
                ("regiao",           "string",  "Região geográfica de SP"),
            ],
            "air_quality_raw": [
                ("estacao_id",   "string",  "ID da estação CETESB"),
                ("timestamp_utc","datetime","Timestamp UTC"),
                ("pm25",         "float",   "PM2.5 (µg/m³)"),
                ("pm10",         "float",   "PM10 (µg/m³)"),
                ("o3",           "float",   "Ozônio (µg/m³)"),
                ("no2",          "float",   "NO₂ (µg/m³)"),
                ("co",           "float",   "CO (ppm)"),
                ("so2",          "float",   "SO₂ (µg/m³)"),
            ],
            "gps_bus_raw": [
                ("veiculo_id",  "string",  "ID do veículo"),
                ("motorista_id","string",  "ID do motorista (PII — hash em Silver)"),
                ("linha",       "string",  "Código da linha (ex: 702A-10)"),
                ("latitude",    "float",   "Latitude WGS84"),
                ("longitude",   "float",   "Longitude WGS84"),
                ("timestamp",   "datetime","Timestamp local"),
                ("lotacao",     "string",  "Lotação declarada"),
                ("ativo",       "bool",    "Veículo em operação"),
            ],
        },
        "Silver": {
            "iot_traffic_clean": [
                ("sensor_id",        "string",  "ID do sensor (inalterado)"),
                ("timestamp_utc",    "datetime","Timestamp UTC"),
                ("velocidade_kmh",   "float",   "Velocidade em km/h"),
                ("ocupacao_pct",     "float",   "Ocupação validada [0,100]"),
                ("contagem_veiculos","int",      "Contagem (nulos → mediana)"),
                ("tipo_via",         "category","Via como categoria"),
                ("regiao",           "category","Região como categoria"),
            ],
            "air_quality_clean": [
                ("estacao_id",    "string",  "ID da estação"),
                ("timestamp_utc", "datetime","Timestamp UTC validado"),
                ("pm25",          "float",   "PM2.5 validado"),
                ("iqar",          "float",   "Índice de Qualidade do Ar [0–200+]"),
                ("iqar_categoria","string",  "Boa / Moderada / Ruim / Muito Ruim"),
            ],
            "gps_bus_clean": [
                ("veiculo_id",       "string",  "ID do veículo"),
                ("motorista_id_hash","string",  "SHA-256 do motorista_id (LGPD)"),
                ("linha",            "string",  "Código da linha"),
                ("latitude",         "float",   "Lat validada [-90, 90]"),
                ("longitude",        "float",   "Lon validada [-180, 180]"),
                ("timestamp_utc",    "datetime","Timestamp UTC"),
                ("lotacao",          "category","Baixa / Média / Alta / Cheia"),
                ("ativo",            "bool",    "Em operação"),
            ],
        },
        "Gold": {
            "air_quality_with_anomalies": [
                ("estacao_id",   "string",  "ID da estação"),
                ("timestamp_utc","datetime","Timestamp UTC"),
                ("iqar",         "float",   "IQAr calculado"),
                ("iqar_norm",    "float",   "IQAr normalizado [0, 1]"),
                ("pm25_lag1h",   "float",   "PM2.5 na hora anterior"),
                ("pm25_lag24h",  "float",   "PM2.5 24h atrás"),
                ("temperatura",  "float",   "Temperatura (join Meteorologia)"),
                ("anomalia_pred","int",      "Isolation Forest: 0=Normal, 1=Anomalia"),
                ("anomaly_score","float",   "Score contínuo de anomalia"),
            ],
            "bus_demand_forecast": [
                ("linha",           "string","Código da linha"),
                ("hora",            "int",   "Hora do dia [0-23]"),
                ("dia_semana",      "int",   "Dia [0=Seg, 6=Dom]"),
                ("temperatura",     "float", "Temperatura (feature)"),
                ("precipitacao",    "float", "Precipitação (feature)"),
                ("demanda",         "int",   "Contagem real de ônibus (target)"),
                ("demanda_prevista","float", "Previsão XGBoost"),
            ],
            "occurrence_clusters": [
                ("latitude",      "float", "Latitude da ocorrência"),
                ("longitude",     "float", "Longitude da ocorrência"),
                ("tipo_ocorrencia","string","Tipo da reclamação"),
                ("iqar_bairro",   "float", "IQAr médio do bairro"),
                ("cluster_id",    "int",   "Cluster DBSCAN (-1 = ruído)"),
                ("risk_score",    "float", "Score de risco composto"),
            ],
        },
    }

    parquet_map = {
        "iot_traffic_raw":            BRONZE_DIR / "iot_traffic_raw.parquet",
        "air_quality_raw":            BRONZE_DIR / "air_quality_raw.parquet",
        "gps_bus_raw":                BRONZE_DIR / "gps_bus_raw.parquet",
        "iot_traffic_clean":          SILVER_DIR / "iot_traffic_clean.parquet",
        "air_quality_clean":          SILVER_DIR / "air_quality_clean.parquet",
        "gps_bus_clean":              SILVER_DIR / "gps_bus_clean.parquet",
        "air_quality_with_anomalies": GOLD_DIR   / "air_quality_with_anomalies.parquet",
        "bus_demand_forecast":        GOLD_DIR   / "bus_demand_forecast.parquet",
        "occurrence_clusters":        GOLD_DIR   / "occurrence_clusters.parquet",
    }

    cor_map = {"Bronze": BRONZE_COL, "Silver": SILVER_COL, "Gold": GOLD_C}

    for camada, tabelas in SCHEMAS.items():
        cor = cor_map[camada]
        st.markdown(
            f'<div style="font-family:Orbitron,sans-serif;font-size:.8rem;font-weight:700;'
            f'color:{cor};letter-spacing:3px;text-transform:uppercase;'
            f'border-left:3px solid {cor};padding-left:12px;margin:24px 0 12px">'
            f'Camada {camada}</div>', unsafe_allow_html=True)

        for tabela, fields in tabelas.items():
            with st.expander(f"  {tabela}  ({len(fields)} campos)"):
                p = parquet_map.get(tabela)
                if p and p.exists():
                    df_r = load(p)
                    if df_r is not None:
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Registros", f"{len(df_r):,}")
                        c2.metric("Colunas",   str(df_r.shape[1]))
                        c3.metric("Nulos",     f"{df_r.isnull().sum().sum():,}")
                        c4.metric("Tamanho",   f"{p.stat().st_size/1024:.1f} KB")
                        st.dataframe(df_r.head(5), use_container_width=True, hide_index=True)

                hdr = ('<div style="display:grid;grid-template-columns:200px 120px 1fr;'
                       'padding:8px 12px;font-family:Orbitron,sans-serif;font-size:.58rem;'
                       'letter-spacing:2px;text-transform:uppercase;color:#4a6a8a;'
                       'border-bottom:1px solid rgba(0,212,255,.18);margin-bottom:2px">'
                       '<span>Campo</span><span>Tipo</span><span>Descrição</span></div>')
                rows_d = "".join(
                    f'<div style="display:grid;grid-template-columns:200px 120px 1fr;'
                    f'padding:6px 12px;border-bottom:1px solid rgba(0,212,255,.05);'
                    f'font-family:JetBrains Mono,monospace;font-size:.7rem">'
                    f'<span style="color:#00d4ff">{f}</span>'
                    f'<span style="color:#ff6b00">{t}</span>'
                    f'<span style="color:rgba(160,185,210,.8)">{d}</span></div>'
                    for f, t, d in fields)
                st.markdown(
                    f'<div style="background:rgba(4,8,18,.7);border:1px solid rgba(0,212,255,.1);'
                    f'border-radius:10px;padding:8px 4px;margin-top:8px">'
                    + hdr + rows_d + "</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁG — FONTES DE DADOS
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "🗄️ Fontes de Dados":
    st.markdown('<div class="page-header"><div class="ph-tag">// Data Sources · Catalog</div></div>',
                unsafe_allow_html=True)
    st.title("Catálogo de Fontes de Dados")
    st.caption("Descrição detalhada de cada fonte: características, formato, frequência, volume e desafios de ingestão.")

    # ── Visão consolidada ──────────────────────────────────────────────────────
    st.markdown('<div class="sec-div">// Visão Consolidada das 5 Fontes</div>',
                unsafe_allow_html=True)

    FONTES_OVERVIEW = [
        {
            "icon": "🚦", "nome": "IoT Tráfego (CET-SP)",
            "tipo": "Sensor / Streaming", "cor": BRONZE_COL,
            "freq": "A cada 5 min", "volume": "~288 leituras/sensor/dia",
            "formato": "JSON via MQTT", "latencia": "< 30s",
            "registros": "~10.000 / execução",
        },
        {
            "icon": "🌫️", "nome": "Qualidade do Ar (CETESB)",
            "tipo": "API REST / Batch", "cor": CYAN,
            "freq": "Horária", "volume": "~50 estações × 8 poluentes",
            "formato": "JSON/CSV via API", "latencia": "~15 min",
            "registros": "~5.000 / execução",
        },
        {
            "icon": "🚌", "nome": "GPS Ônibus (SPTrans)",
            "tipo": "Streaming em tempo real", "cor": GREEN,
            "freq": "A cada 30s por veículo", "volume": "~14.000 ônibus ativos",
            "formato": "JSON via WebSocket/API", "latencia": "< 60s",
            "registros": "~20.000 / execução",
        },
        {
            "icon": "📋", "nome": "Ouvidoria Municipal",
            "tipo": "Batch / CDC", "cor": ORANGE,
            "freq": "Diária (batch noturno)", "volume": "~500–2000 reclamações/dia",
            "formato": "CSV exportado do CRM", "latencia": "~24h",
            "registros": "~3.000 / execução",
        },
        {
            "icon": "🌡️", "nome": "Meteorologia (INMET)",
            "tipo": "API REST / Batch", "cor": PURPLE,
            "freq": "Horária", "volume": "~120 estações no estado de SP",
            "formato": "CSV / JSON via API INMET", "latencia": "~1h",
            "registros": "~8.760 / execução",
        },
    ]

    cols = st.columns(5)
    for col, f in zip(cols, FONTES_OVERVIEW):
        with col:
            st.markdown(
                f'<div class="nb-card" style="--nc:{f["cor"]};min-height:200px">'
                f'<div style="font-size:1.8rem;text-align:center;margin-bottom:8px">{f["icon"]}</div>'
                f'<div class="nb-title" style="font-size:.6rem;text-align:center">{f["nome"]}</div>'
                f'<div class="nb-stat"><b style="color:{f["cor"]}">{f["tipo"]}</b></div>'
                f'<div class="nb-stat">Freq: {f["freq"]}</div>'
                f'<div class="nb-stat">Formato: {f["formato"]}</div>'
                f'<div class="nb-stat">Latência: {f["latencia"]}</div>'
                f'<div class="nb-stat">Registros: {f["registros"]}</div>'
                f'</div>',
                unsafe_allow_html=True)

    # ── Detalhamento por fonte ─────────────────────────────────────────────────
    st.markdown('<div class="sec-div">// Detalhamento Técnico por Fonte</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚦 IoT Tráfego", "🌫️ Qualidade do Ar",
        "🚌 GPS Ônibus",  "📋 Ouvidoria", "🌡️ Meteorologia"
    ])

    with tab1:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### Fonte: Sensores IoT — CET-SP")
            st.markdown("""
**Órgão responsável:** Companhia de Engenharia de Tráfego (CET-SP)

**Descrição:** Rede de sensores magnéticos e de laço indutivo instalados nas principais vias arteriais de São Paulo.
Cada sensor reporta velocidade média, contagem de veículos e taxa de ocupação da via a cada 5 minutos.

**Protocolo de ingestão real:** MQTT Broker → Apache Kafka (tópico `cet.iot.traffic`) → consumer Python → Bronze

**Características do dado bruto:**
- Velocidade em **m/s** (precisa conversão para km/h)
- Timestamps em **horário local** sem timezone (precisa UTC)
- ~5% dos sensores reportam valores negativos ou zerados (sensor com defeito)
- Não há deduplição na fonte — o mesmo evento pode chegar 2×

**Problemas típicos de qualidade:**
| Problema | Frequência | Tratamento |
|----------|-----------|------------|
| Velocidade negativa | ~1.2% | Imputar com mediana do sensor |
| Timestamp sem TZ | 100% | Converter: `America/Sao_Paulo → UTC` |
| Sensor offline | ~3% por janela | Manter nulo; flag `sensor_ativo=False` |
| Duplicatas | ~0.8% | Deduplicar por `(sensor_id, timestamp)` |

**Evolução de schema conhecida:** Em 2023, o campo `contagem` foi renomeado para `contagem_veiculos`. O pipeline usa `rename()` defensivo.
""")
        with c2:
            # Mostrar amostra real se disponível
            df_b = load(BRONZE_DIR / "iot_traffic_raw.parquet")
            if df_b is not None:
                st.markdown("**Amostra real — Bronze:**")
                st.dataframe(df_b.head(6), use_container_width=True, hide_index=True)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Registros", f"{len(df_b):,}")
                c_b.metric("Colunas", str(df_b.shape[1]))
                c_c.metric("Nulos", f"{df_b.isnull().sum().sum():,}")
                # Distribuição de tipo_via
                if "tipo_via" in df_b.columns:
                    fig_tv = px.pie(df_b, names="tipo_via",
                                    color_discrete_sequence=NEON, hole=0.5)
                    st.plotly_chart(cyber(fig_tv, "Distribuição por Tipo de Via", 260),
                                    use_container_width=True)
            else:
                st.info("Execute o pipeline para ver os dados reais.")

            # Particionamento real
            part_dir = BRONZE_DIR / "iot_traffic_partitioned"
            if part_dir.exists():
                parts = list(part_dir.glob("*/"))
                st.markdown(f"**Particionamento físico** (`tipo_via=*`): **{len(parts)} partições**")
                for p in sorted(parts)[:5]:
                    files = list(p.glob("*.parquet"))
                    sz = sum(f.stat().st_size for f in files) / 1024
                    st.markdown(f"&nbsp;&nbsp;`{p.name}/` — {len(files)} arquivo(s), {sz:.1f} KB")

    with tab2:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### Fonte: Qualidade do Ar — CETESB")
            st.markdown("""
**Órgão responsável:** Companhia Ambiental do Estado de São Paulo (CETESB)

**Descrição:** Rede QUALAR com ~50 estações automáticas que monitoram poluentes atmosféricos 24/7.
Os dados são disponibilizados via API REST e portal web.

**Protocolo de ingestão real:** API REST QUALAR (`api.cetesb.sp.gov.br`) → autenticação OAuth2
→ JSON → parsing → Bronze

**Poluentes monitorados:**
| Poluente | Unidade | Limite CONAMA |
|----------|---------|---------------|
| PM2.5 | µg/m³ | 25 µg/m³ (24h) |
| PM10 | µg/m³ | 50 µg/m³ (24h) |
| O₃ | µg/m³ | 100 µg/m³ (8h) |
| NO₂ | µg/m³ | 200 µg/m³ (1h) |
| CO | ppm | 9 ppm (8h) |
| SO₂ | µg/m³ | 20 µg/m³ (24h) |

**Cálculo do IQAr (Silver):**
O Índice de Qualidade do Ar é calculado por interpolação linear dos sub-índices de cada poluente,
conforme metodologia CETESB/IBAMA. O pior sub-índice define a categoria final:
`Boa (0–40) → Moderada (41–80) → Ruim (81–120) → Muito Ruim (121–200) → Péssima (>200)`.

**Problemas típicos:**
- Estações com manutenção reportam `-999` (precisa converter para NaN)
- Dados atrasados até 15 min após o fechamento da hora
- ~3% de estações com falha de comunicação por janela
""")
        with c2:
            df_ar = load(BRONZE_DIR / "air_quality_raw.parquet")
            if df_ar is not None:
                st.markdown("**Amostra real — Bronze:**")
                st.dataframe(df_ar.head(6), use_container_width=True, hide_index=True)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Registros", f"{len(df_ar):,}")
                c_b.metric("Estações", str(df_ar["estacao_id"].nunique()) if "estacao_id" in df_ar.columns else "—")
                c_c.metric("Nulos", f"{df_ar.isnull().sum().sum():,}")
                if "pm25" in df_ar.columns:
                    fig_pm = px.histogram(df_ar.dropna(subset=["pm25"]), x="pm25",
                                          nbins=40, color_discrete_sequence=[CYAN])
                    fig_pm.update_traces(marker_line_width=0)
                    st.plotly_chart(cyber(fig_pm, "Distribuição PM2.5 (Bronze)", 240),
                                    use_container_width=True)
            else:
                st.info("Execute o pipeline para ver os dados reais.")

    with tab3:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### Fonte: GPS Ônibus — SPTrans")
            st.markdown("""
**Órgão responsável:** São Paulo Transporte S.A. (SPTrans)

**Descrição:** Sistema AVL (Automatic Vehicle Location) com rastreamento GPS de toda a frota de
ônibus municipal (~14.000 veículos). Cada veículo envia posição a cada 30 segundos.

**Protocolo de ingestão real:** WebSocket `ws://api.olhovivo.sptrans.com.br` (token JWT)
→ stream JSON → Kafka (`sptrans.gps.positions`) → consumer → Bronze

**Volume estimado em produção:**
- 14.000 ônibus × 2 leituras/min × 60 min × 18h de operação = **~30 milhões registros/dia**
- Por isso a **partição por `regiao`** é essencial para viabilizar queries

**Dados de PII e LGPD:**
O campo `motorista_id` é PII (identificador do motorista). O pipeline aplica SHA-256 na
camada Silver tornando o dado irreversível, conforme Art. 12 da LGPD.
As coordenadas GPS são mantidas pois referem-se ao veículo público, não à pessoa.

**Problemas típicos:**
| Problema | Frequência | Tratamento |
|----------|-----------|------------|
| Coordenada (0,0) | ~0.5% | Remover (GPS não fixado) |
| Lotação inconsistente | ~2% | Corrigir para `Desconhecida` |
| Sinal perdido > 5 min | ~1.8% | Flag `ativo=False` |
| Duplicata por retransmissão | ~1.2% | Dedup por `(veiculo_id, timestamp)` |
""")
        with c2:
            df_gps = load(BRONZE_DIR / "gps_bus_raw.parquet")
            if df_gps is not None:
                st.markdown("**Amostra real — Bronze:**")
                st.dataframe(df_gps.head(6), use_container_width=True, hide_index=True)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Registros", f"{len(df_gps):,}")
                c_b.metric("Linhas",    str(df_gps["linha"].nunique()) if "linha" in df_gps.columns else "—")
                c_c.metric("Nulos",     f"{df_gps.isnull().sum().sum():,}")
                if "lotacao" in df_gps.columns:
                    fig_lot = px.bar(df_gps["lotacao"].value_counts().reset_index(),
                                     x="lotacao", y="count",
                                     color_discrete_sequence=[GREEN])
                    fig_lot.update_traces(marker_line_width=0)
                    st.plotly_chart(cyber(fig_lot, "Distribuição de Lotação (Bronze)", 240),
                                    use_container_width=True)
            else:
                st.info("Execute o pipeline para ver os dados reais.")
            part_dir = BRONZE_DIR / "gps_bus_partitioned"
            if part_dir.exists():
                parts = list(part_dir.glob("*/"))
                st.markdown(f"**Partições físicas** (`regiao=*`): **{len(parts)} regiões**")
                for p in sorted(parts)[:6]:
                    files = list(p.glob("*.parquet"))
                    sz = sum(f.stat().st_size for f in files) / 1024
                    st.markdown(f"&nbsp;&nbsp;`{p.name}/` — {sz:.1f} KB")

    with tab4:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### Fonte: Ouvidoria Municipal — Prefeitura SP")
            st.markdown("""
**Órgão responsável:** Secretaria Municipal de Inovação e Tecnologia / 156 SP

**Descrição:** Sistema de atendimento 156 que registra reclamações, sugestões e
solicitações de serviços públicos. Cada registro inclui texto livre, endereço,
tipo de ocorrência e status de atendimento.

**Protocolo de ingestão real:** SFTP noturno (02h00) → CSV compactado (.gz)
→ decompressão → parsing → Bronze  *(batch diário — padrão CDC)*

**Dados sensíveis e LGPD:**
O campo `texto_reclamacao` pode conter CPF, nome, telefone e endereço completo.
O pipeline aplica remoção via regex no Silver antes de qualquer persistência:
- CPF: `[0-9]{3}\\.?[0-9]{3}\\.?[0-9]{3}-?[0-9]{2}`
- Telefone: `(\\+55)?[\\s-]?\\(?[0-9]{2}\\)?[\\s-]?[0-9]{4,5}-?[0-9]{4}`
- E-mail: `[\\w.-]+@[\\w.-]+\\.[\\w]+`

**Características do schema:**
- Texto livre de até 2.000 caracteres (variável, sem schema fixo)
- CEPs inconsistentes: com/sem traço, com/sem prefixo de estado
- Status com 12+ valores distintos → normalizado para 5 categorias no Silver

**Problemas típicos:**
| Problema | Frequência | Tratamento |
|----------|-----------|------------|
| PII em texto livre | ~8% | Remoção regex (Silver) |
| CEP inválido | ~3.5% | Manter como NaN |
| Sem coordenadas | ~15% | Geocoding reverso por bairro |
| Status não mapeado | ~2% | Categoria `Outros` |
""")
        with c2:
            df_ouv = load(BRONZE_DIR / "ouvidoria_cdc_raw.parquet")
            if df_ouv is not None:
                st.markdown("**Amostra real — Bronze:**")
                st.dataframe(df_ouv.head(6), use_container_width=True, hide_index=True)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Registros", f"{len(df_ouv):,}")
                c_b.metric("Colunas",   str(df_ouv.shape[1]))
                c_c.metric("Nulos",     f"{df_ouv.isnull().sum().sum():,}")
                if "tipo_ocorrencia" in df_ouv.columns:
                    top = df_ouv["tipo_ocorrencia"].value_counts().head(8).reset_index()
                    fig_tip = px.bar(top, x="count", y="tipo_ocorrencia",
                                     orientation="h", color_discrete_sequence=[ORANGE])
                    fig_tip.update_traces(marker_line_width=0)
                    st.plotly_chart(cyber(fig_tip, "Top Tipos de Ocorrência (Bronze)", 280),
                                    use_container_width=True)
            else:
                st.info("Execute o pipeline para ver os dados reais.")

    with tab5:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### Fonte: Meteorologia — INMET")
            st.markdown("""
**Órgão responsável:** Instituto Nacional de Meteorologia (INMET)

**Descrição:** Rede de ~500 estações automáticas no Brasil, com ~120 no estado de SP.
Dados horários de temperatura, precipitação, umidade, pressão, vento e radiação solar.

**Protocolo de ingestão real:** API REST INMET `apitempo.inmet.gov.br`
→ autenticação por token → JSON → Bronze  *(batch horário)*

**Relevância para o pipeline:**
Os dados meteorológicos são usados como **features exógenas** em dois modelos:
1. **XGBoost (demanda de transporte):** temperatura e chuva influenciam lotação de ônibus
2. **Gold Ar (qualidade do ar):** temperatura e vento correlacionam com dispersão de poluentes

**Características do dado:**
| Variável | Unidade | Range típico SP | Obs. |
|----------|---------|-----------------|------|
| Temperatura | °C | 10–35 | Kelvin na API → converter |
| Precipitação | mm/h | 0–80 | Valores negativos → 0 |
| Umidade relativa | % | 30–95 | Fora [0,100] → remover |
| Velocidade vento | m/s | 0–15 | — |
| Pressão atm. | hPa | 900–1020 | — |

**Problemas típicos:**
| Problema | Frequência | Tratamento |
|----------|-----------|------------|
| Temperatura em Kelvin | ~5% das estações | Converter: `K - 273.15` |
| Precipitação < 0 | ~0.9% | Forçar 0 |
| Umidade > 100% | ~0.3% | Remover (sensor com defeito) |
| Estação offline | ~2% / hora | Manter NaN |
""")
        with c2:
            df_wth = load(BRONZE_DIR / "weather_inmet_raw.parquet")
            if df_wth is not None:
                st.markdown("**Amostra real — Bronze:**")
                st.dataframe(df_wth.head(6), use_container_width=True, hide_index=True)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Registros", f"{len(df_wth):,}")
                c_b.metric("Colunas",   str(df_wth.shape[1]))
                c_c.metric("Nulos",     f"{df_wth.isnull().sum().sum():,}")
                if "temperatura" in df_wth.columns and "precipitacao" in df_wth.columns:
                    fig_sc = px.scatter(df_wth.sample(min(500, len(df_wth))),
                                        x="temperatura", y="precipitacao",
                                        opacity=0.5, color_discrete_sequence=[PURPLE])
                    fig_sc.update_traces(marker=dict(size=4, line_width=0))
                    st.plotly_chart(cyber(fig_sc, "Temperatura × Precipitação (Bronze)", 260),
                                    use_container_width=True)
            else:
                st.info("Execute o pipeline para ver os dados reais.")

    # ── Estratégia de particionamento ──────────────────────────────────────────
    st.markdown('<div class="sec-div">// Estratégia de Particionamento Parquet</div>',
                unsafe_allow_html=True)
    st.markdown("""
O particionamento Parquet usa o padrão **Hive-style** (`coluna=valor/`) suportado
nativamente por Spark, DuckDB, Athena e PyArrow. A lógica de escolha da coluna de
partição segue o padrão de **"filtre pelo que você mais consulta"**:
""")

    part_data = [
        ("Bronze", "iot_traffic_partitioned",    "tipo_via",       "Consultas por arterial/coletora/local"),
        ("Bronze", "gps_bus_partitioned",        "regiao",         "Análises por região geográfica de SP"),
        ("Gold",   "air_quality_partitioned",    "iqar_categoria", "Alertas filtram só categoria Ruim/Péssima"),
        ("Gold",   "bus_demand_partitioned",     "dia_semana",     "Modelos de demanda por dia da semana"),
    ]

    tbl_p = (
        '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;'
        'font-family:JetBrains Mono,monospace;font-size:.72rem"><thead><tr '
        'style="border-bottom:1px solid rgba(0,212,255,.3)">'
        + "".join(f'<th style="padding:8px 12px;color:#00d4ff;font-family:Orbitron,sans-serif;'
                  f'font-size:.58rem;letter-spacing:1.5px;text-transform:uppercase;text-align:left">{h}</th>'
                  for h in ["Camada", "Dataset", "Coluna de Partição", "Justificativa"])
        + "</tr></thead><tbody>"
    )
    for i, (camada, ds, col, just) in enumerate(part_data):
        cor = BRONZE_COL if camada == "Bronze" else GOLD_C
        bg  = "rgba(0,212,255,.02)" if i % 2 == 0 else "transparent"
        exists = (BASE_DIR / "data" / camada.lower() / ds).exists()
        status = f'<span style="color:#00ff88">OK</span>' if exists else f'<span style="color:#ff6b00">pendente</span>'
        tbl_p += (f'<tr style="background:{bg};border-bottom:1px solid rgba(0,212,255,.05)">'
                  f'<td style="padding:7px 12px;color:{cor}">{camada}</td>'
                  f'<td style="padding:7px 12px;color:#d0e4ff">{ds}/</td>'
                  f'<td style="padding:7px 12px;color:#9b6fff">{col}</td>'
                  f'<td style="padding:7px 12px;color:#7a9ab8">{just} {status}</td></tr>')
    tbl_p += "</tbody></table></div>"
    st.markdown(tbl_p, unsafe_allow_html=True)

    st.markdown("""
**Benefícios práticos do particionamento:**
- **Push-down de predicado:** `WHERE iqar_categoria = 'Ruim'` lê apenas 1 partição (~20× mais rápido)
- **Atualização incremental:** Sobrescreve apenas a partição do dia sem reescrever o dataset inteiro
- **Paralelismo:** Spark/Dask processa cada partição em um executor separado
- **Escalabilidade:** Permite armazenar anos de dados sem degradação de performance
""")
