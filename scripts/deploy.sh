#!/bin/bash

# Script de deploy/atualização da aplicação
# Execute este script no diretório raiz do projeto

set -e

echo "==================================="
echo "PlacarCerto - Deploy"
echo "==================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se os arquivos .env existem
if [ ! -f "backend/.env.production" ]; then
    echo -e "${RED}Erro: backend/.env.production não encontrado!${NC}"
    echo "Copie o arquivo .env.production.example e configure:"
    echo "  cp backend/.env.production.example backend/.env.production"
    exit 1
fi

# Pull das últimas mudanças (se for um update)
if [ -d ".git" ]; then
    echo -e "${YELLOW}Atualizando código do repositório...${NC}"
    git pull origin main || git pull origin master
fi

# Parar containers existentes
echo -e "${YELLOW}Parando containers...${NC}"
docker-compose down

# Rebuild e start
echo -e "${YELLOW}Construindo e iniciando containers...${NC}"
docker-compose up -d --build

# Aguardar containers iniciarem
echo -e "${YELLOW}Aguardando containers iniciarem...${NC}"
sleep 10

# Verificar status
echo -e "${GREEN}Verificando status dos containers...${NC}"
docker-compose ps

# Logs do backend
echo ""
echo -e "${GREEN}Últimas 20 linhas do log do backend:${NC}"
docker-compose logs --tail=20 backend

echo ""
echo "==================================="
echo -e "${GREEN}Deploy concluído!${NC}"
echo "==================================="
echo ""
echo "Comandos úteis:"
echo "  Ver logs:           docker-compose logs -f"
echo "  Parar aplicação:    docker-compose down"
echo "  Restart:            docker-compose restart"
echo "  Shell no backend:   docker-compose exec backend bash"
echo "  Migrations:         docker-compose exec backend python manage.py migrate"
echo "  Criar superuser:    docker-compose exec backend python manage.py createsuperuser"
echo ""
