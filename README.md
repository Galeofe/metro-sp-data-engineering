# Metrópole SP — Data Platform

> Pipeline de Engenharia de Dados para Cidades Inteligentes  
> Arquitetura Medallion · Bronze → Silver → Gold · ML · Dashboard Interativo

---

## Visão Geral

Este projeto implementa uma plataforma completa de **Engenharia de Dados** aplicada ao contexto de **Cidades Inteligentes** na Metrópole de São Paulo. O pipeline processa dados de cinco fontes heterogêneas, aplica transformações em camadas (Medallion Architecture), treina modelos de IA e expõe os resultados em um dashboard interativo com tema cyber/tech.

    Fontes Brutas → [BRONZE] → [SILVER] → [GOLD] → Modelos de IA → Dashboard

---

## Tecnologias

| Categoria | Tecnologia | Versão |
|-----------|-----------|--------|
| Linguagem | Python | 3.11+ |
| Pipeline | pandas, numpy, pyarrow | 2.x / 1.x / 13.x |
| ML | scikit-learn, XGBoost | 1.3+ / 2.x |
| Dashboard | Streamlit | 1.35+ |
| Visualização | Plotly, Matplotlib, Seaborn | 5.x / 3.x |
| Notebooks | JupyterLab, nbformat, nbclient | 4.x |
| Storage | Apache Parquet | via PyArrow |
| Containerização | Docker + Docker Compose | -- |

---

## Instalação

    pip install -r requirements.txt
    python main.py
    streamlit run app.py

Dashboard: http://localhost:8501

---

## Dashboard — 11 Páginas

| Página | Descrição |
|--------|-----------|
| Visão Geral | KPIs, diagrama de pipeline, volumes por camada |
| Bronze | Exploração dos dados brutos + perfil de qualidade |
| Silver | Dados limpos, comparação com Bronze |
| Gold | Features ML, correlações, distribuições |
| Modelos de IA | Isolation Forest, XGBoost e DBSCAN |
| Laboratório Jupyter | Notebooks integrados com auto-sync |
| Relatórios | Gráficos personalizáveis + exportação PDF |
| Linhagem de Dados | Sankey interativo + tabela de transformações |
| Qualidade / SLA | Score por dataset, heatmap de nulos, SLA 90% |
| Agendador | Execuções automáticas + histórico |
| Dicionário de Dados | Schema completo com amostras reais |

---

## Modelos de IA

- **Isolation Forest** — Anomalias na qualidade do ar (contamination=0.05)
- **XGBoost** — Previsão de demanda de transporte (MAE, R2)
- **DBSCAN** — Clusters geoespaciais de risco urbano

---

## Conformidade LGPD

- motorista_id → SHA-256 (Silver)
- Texto livre → PII removido via regex
- Coordenadas GPS validadas sem tracking individual

---

## Autor

Gabriel Felice — gabriel.felice@everflow.com.br  
Projeto de Avaliação — Engenharia de Dados — Junho 2026
