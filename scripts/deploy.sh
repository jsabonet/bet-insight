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

# Verificar se o backend/.env.production existe
if [ ! -f "backend/.env.production" ]; then
    echo -e "${RED}Erro: backend/.env.production nao encontrado!${NC}"
    echo "Copie o arquivo .env.production.example e configure:"
    echo "  cp backend/.env.production.example backend/.env.production"
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

# Build sequencial + BuildKit: com 1 vCPU o build paralelo e mais lento
# (troca de contexto constante) e consome o dobro da memoria.
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export COMPOSE_PARALLEL_LIMIT=1
export BUILDKIT_PROGRESS=plain

# Pull das ultimas mudancas (se for um update)
if [ -d ".git" ]; then
    echo -e "${YELLOW}Atualizando codigo do repositorio...${NC}"
    git pull origin main || git pull origin master
fi

# Construir as imagens primeiro: se algo falhar, os containers antigos
# continuam a servir trafego (sem downtime no meio do build).
echo -e "${YELLOW}Construindo imagens (backend + frontend)...${NC}"
docker compose build backend frontend

echo -e "${YELLOW}Iniciando containers...${NC}"
docker compose up -d --no-build

echo -e "${YELLOW}Aguardando containers iniciarem...${NC}"
sleep 10

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
echo ""
