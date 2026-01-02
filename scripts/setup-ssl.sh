#!/bin/bash

# Script para configurar SSL com Let's Encrypt

set -e

echo "==================================="
echo "Configuração SSL com Let's Encrypt"
echo "==================================="

# Verificar se o domínio foi fornecido
if [ -z "$1" ]; then
    echo "Uso: ./setup-ssl.sh seu-dominio.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}

echo "Domínio: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Parar nginx temporariamente
echo "Parando nginx..."
docker-compose stop nginx

# Obter certificado
echo "Obtendo certificado SSL..."
docker-compose run --rm certbot certonly --standalone \
    --preferred-challenges http \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive

# Atualizar configuração do nginx
echo "Atualizando configuração do nginx..."
sed -i "s/seu-dominio.com/$DOMAIN/g" docker/nginx/conf.d/default.conf

# Descomentar linhas HTTPS na configuração
sed -i 's/# server {/server {/g' docker/nginx/conf.d/default.conf
sed -i 's/#     listen/    listen/g' docker/nginx/conf.d/default.conf
sed -i 's/#     server_name/    server_name/g' docker/nginx/conf.d/default.conf
sed -i 's/#     ssl_/    ssl_/g' docker/nginx/conf.d/default.conf
sed -i 's/#     location/    location/g' docker/nginx/conf.d/default.conf
sed -i 's/# }/}/g' docker/nginx/conf.d/default.conf

# Reiniciar nginx
echo "Reiniciando nginx..."
docker-compose up -d nginx

echo ""
echo "==================================="
echo "SSL configurado com sucesso!"
echo "==================================="
echo ""
echo "Seu site agora está disponível em:"
echo "  https://$DOMAIN"
echo "  https://www.$DOMAIN"
echo ""
echo "Os certificados serão renovados automaticamente."
echo ""
