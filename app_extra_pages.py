

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