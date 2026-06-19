# ── Imagem base ──────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Metadados
LABEL maintainer="Metrópole SP Data Platform"
LABEL description="Pipeline de Engenharia de Dados — Cidades Inteligentes"

# Evita prompts interativos durante o build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    # MinIO / S3 (configuráveis via docker-compose env)
    MINIO_ENDPOINT=minio:9000 \
    MINIO_ACCESS_KEY=metropolesp \
    MINIO_SECRET_KEY=metropolesp2026 \
    MINIO_BUCKET=data-lake

WORKDIR /app

# Dependências do sistema (necessárias para pyarrow / xgboost)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python primeiro (camada cacheada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte
COPY . .

# Cria diretórios de dados para o volume externo
RUN mkdir -p data/bronze data/silver data/gold reports

# Expõe porta do Streamlit
EXPOSE 8501

# Saúde: verifica se o Streamlit responde
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Comando padrão: inicia o dashboard
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]