

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