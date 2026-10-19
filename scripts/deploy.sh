#!/bin/bash

# Script de deploy/atualizacao da aplicacao
# Execute este script no diretorio raiz do projeto

set -e

echo "==================================="
echo "PlacarCerto - Deploy"
echo "==================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ENV_FILE="backend/.env.production"
ROOT_ENV=".env"

# Verificar se o backend/.env.production existe
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Erro: $ENV_FILE nao encontrado!${NC}"
    echo "Copie o arquivo .env.production.example e configure:"
    echo "  cp backend/.env.production.example $ENV_FILE"
    exit 1
fi

# ---------------------------------------------------------------------------
# Swap: obrigatorio em droplets pequenos (512 MB - 1 GB).
# Sem swap, `npm run build` e `apt-get` sao mortos pelo OOM killer e o build
# parece "travar" durante varios minutos.
# ---------------------------------------------------------------------------
if [ "$(swapon --show --noheadings | wc -l)" -eq 0 ]; then
    if [ "$(id -u)" -eq 0 ] && [ -x "scripts/setup-swap.sh" ]; then
        echo -e "${YELLOW}Nenhum swap ativo - criando 2 GB de swap (necessario para o build)...${NC}"
        ./scripts/setup-swap.sh
    else
        echo -e "${YELLOW}AVISO: nenhum swap ativo. Em servidores com menos de 2 GB de RAM"
        echo -e "o build pode ser interrompido por falta de memoria.${NC}"
        echo "  Execute como root: ./scripts/setup-swap.sh"
        echo ""
    fi
fi

# ---------------------------------------------------------------------------
# Sincronizar as credenciais de banco para o .env da raiz.
#
# O Docker Compose le a interpolacao ${VAR} do .env da raiz, NAO do
# backend/.env.production (esse e apenas `env_file` dos containers). Sem esta
# sincronizacao o postgres recebia a senha por omissao e o Django a senha real,
# resultando em "password authentication failed for user postgres".
# ---------------------------------------------------------------------------
read_env_value() {
    grep -E "^[[:space:]]*$1[[:space:]]*=" "$2" 2>/dev/null | tail -n 1 \
        | sed -e 's/^[^=]*=//' -e 's/[[:space:]]*$//' \
        | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"
}

quote_env_value() {
    # Valores com $, # ou espacos sao envolvidos em aspas simples para o
    # Compose nao tentar interpreta-los.
    case "$1" in
        *\$*|*\#*|*" "*|*"'"*) printf "'%s'" "$1" ;;
        *) printf '%s' "$1" ;;
    esac
}

DB_NAME_VAL=$(read_env_value DB_NAME "$ENV_FILE")
DB_USER_VAL=$(read_env_value DB_USER "$ENV_FILE")
DB_PASSWORD_VAL=$(read_env_value DB_PASSWORD "$ENV_FILE")

DB_NAME_VAL=${DB_NAME_VAL:-betinsight_db}
DB_USER_VAL=${DB_USER_VAL:-postgres}

if [ -z "$DB_PASSWORD_VAL" ]; then
    echo -e "${RED}Erro: DB_PASSWORD nao definido em $ENV_FILE${NC}"
    exit 1
fi

# URL da API do frontend (runtime). Precedencia:
#   1. VITE_API_URL em frontend/.env.production
#   2. VITE_API_URL ja existente no .env da raiz
#   3. /api (relativo: o nginx faz proxy de /api/ para o backend)
FRONTEND_ENV="frontend/.env.production"
API_URL_VAL=""
if [ -f "$FRONTEND_ENV" ]; then
    API_URL_VAL=$(read_env_value VITE_API_URL "$FRONTEND_ENV")
fi
if [ -z "$API_URL_VAL" ] && [ -f "$ROOT_ENV" ]; then
    API_URL_VAL=$(read_env_value VITE_API_URL "$ROOT_ENV")
fi
API_URL_VAL=${API_URL_VAL:-/api}

echo -e "${YELLOW}Sincronizando credenciais de banco para $ROOT_ENV...${NC}"
umask 077
cat > "$ROOT_ENV" <<EOF
# Gerado automaticamente por scripts/deploy.sh - NAO EDITAR A MAO.
# Fonte de verdade: $ENV_FILE (campos DB_NAME, DB_USER, DB_PASSWORD).
# O Compose usa estes valores tanto no servico db como no backend/celery.
DB_NAME=$(quote_env_value "$DB_NAME_VAL")
DB_USER=$(quote_env_value "$DB_USER_VAL")
DB_PASSWORD=$(quote_env_value "$DB_PASSWORD_VAL")
# URL da API lida pelo frontend em runtime (/config.js). /api e relativo.
VITE_API_URL=$(quote_env_value "$API_URL_VAL")
EOF
chmod 600 "$ROOT_ENV"

# Build sequencial + BuildKit: com 1 vCPU o build paralelo e mais lento
# (troca de contexto constante) e consome o dobro da memoria.
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export COMPOSE_PARALLEL_LIMIT=1
export BUILDKIT_PROGRESS=plain

# Pull das ultimas mudancas (se for um update)
if [ -d ".git" ]; then
    echo -e "${YELLOW}Atualizando codigo do repositorio...${NC}"
    git pull --ff-only origin main
fi

# Construir as imagens primeiro: se algo falhar, os containers antigos
# continuam a servir trafego (sem downtime no meio do build).
echo -e "${YELLOW}Construindo imagens (backend + frontend)...${NC}"
docker compose build backend frontend

echo -e "${YELLOW}Iniciando containers...${NC}"
docker compose up -d --no-build

echo -e "${YELLOW}Aguardando containers iniciarem...${NC}"
sleep 10

# ---------------------------------------------------------------------------
# Sincronizar o ssl.conf gerado com o template e recarregar o nginx.
#
# `docker/nginx/conf.d/ssl.conf` e gerado pelo setup-ssl.sh e nao e versionado.
# Quando o template muda (por exemplo, os blocos `upstream` e o servidor 443
# que rejeita o handshake no IP), um ssl.conf antigo fica desactualizado e o
# nginx -t falha com "host not found in upstream". Regeneramos a partir do
# dominio que ja consta no ficheiro, preservando a opcao www.
# ---------------------------------------------------------------------------
SSL_TEMPLATE="docker/nginx/ssl.conf.template"
SSL_GENERATED="docker/nginx/conf.d/ssl.conf"

if [ -f "$SSL_GENERATED" ] && [ -f "$SSL_TEMPLATE" ]; then
    SSL_DOMAIN=$(grep -oE '/etc/letsencrypt/live/[^/]+/fullchain\.pem' "$SSL_GENERATED" \
        | head -n 1 | cut -d/ -f5)
    if [ -n "$SSL_DOMAIN" ]; then
        SSL_WITH_WWW=false
        if grep -q "www\.${SSL_DOMAIN}" "$SSL_GENERATED"; then
            SSL_WITH_WWW=true
        fi
        echo -e "${YELLOW}Sincronizando $SSL_GENERATED com o template ($SSL_DOMAIN)...${NC}"
        sed "s/\${DOMAIN}/${SSL_DOMAIN}/g" "$SSL_TEMPLATE" > "$SSL_GENERATED.tmp"
        if [ "$SSL_WITH_WWW" = false ]; then
            sed -i "s/ www\.${SSL_DOMAIN}//g" "$SSL_GENERATED.tmp"
        fi
        mv "$SSL_GENERATED.tmp" "$SSL_GENERATED"
    fi
fi

echo -e "${YELLOW}Validando e recarregando o nginx...${NC}"
if docker compose exec -T nginx nginx -t; then
    docker compose exec -T nginx nginx -s reload
else
    echo -e "${RED}nginx -t falhou. O nginx anterior continua a servir o trafego;${NC}"
    echo -e "${RED}corrija os ficheiros em docker/nginx/conf.d/ antes de repetir.${NC}"
    exit 1
fi

echo -e "${GREEN}Verificando status dos containers...${NC}"
docker compose ps

echo ""
echo -e "${GREEN}Ultimas 20 linhas do log do backend:${NC}"
docker compose logs --tail=20 backend

echo ""
echo "==================================="
echo -e "${GREEN}Deploy concluido!${NC}"
echo "==================================="
echo ""
echo "Comandos uteis:"
echo "  Ver logs:           docker compose logs -f"
echo "  Parar aplicacao:    docker compose down"
echo "  Restart:            docker compose restart"
echo "  Shell no backend:   docker compose exec backend bash"
echo "  Migrations:         docker compose exec backend python manage.py migrate"
echo "  Criar superuser:    docker compose exec backend python manage.py createsuperuser"
echo "  Activar HTTPS:      ./scripts/setup-ssl.sh seu-dominio.com"
echo ""
