# Backend Dockerfile - Django com Gunicorn
FROM python:3.11-slim

# Prevenir criação de .pyc e buffering de logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Não instalamos toolchain (gcc/python3-dev/libpq-dev/musl-dev): todas as
# dependências do requirements.txt têm wheels manylinux prontos
# (psycopg2-binary, numpy, pandas, scipy, scikit-learn, pillow, grpcio).
# curl é obrigatório para o healthcheck definido no docker-compose.yml.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY backend/ .

# Criar diretório para arquivos estáticos e media
RUN mkdir -p /app/staticfiles /app/media

# Coletar arquivos estáticos (será executado no entrypoint)
# RUN python manage.py collectstatic --noinput

# Criar usuário não-root para executar a aplicação
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8000

# Script de entrypoint
COPY --chown=appuser:appuser docker/backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
# 2 workers: o droplet tem 1 vCPU e pouca RAM. A regra (2*vCPU)+1 = 3 workers
# fazia cada worker Django (~70-90 MB) estourar a memória do servidor.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--max-requests", "1000", "--max-requests-jitter", "100", "--access-logfile", "-", "--error-logfile", "-"]
