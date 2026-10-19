#!/bin/bash

# Configura SSL (Let's Encrypt) e activa o bloco HTTPS do nginx.
#
# Ordem importante: o nginx sobe em HTTP puro (docker/nginx/conf.d/default.conf),
# o certbot valida o dominio via webroot nesse mesmo HTTP e so depois o bloco
# HTTPS e gerado. Assim o nginx nunca arranca a apontar para um certificado
# que ainda nao existe (era o erro "cannot load certificate ... No such file").

set -e

TEMPLATE="docker/nginx/ssl.conf.template"
TARGET="docker/nginx/conf.d/ssl.conf"

echo "==================================="
echo "Configuracao SSL com Let's Encrypt"
echo "==================================="

if [ -z "$1" ]; then
    echo "Uso: ./scripts/setup-ssl.sh seu-dominio.com [email] [--www]"
    echo ""
    echo "  --www   inclui tambem www.seu-dominio.com (requer registo DNS A/CNAME"
    echo "          para o www; sem ele o Let's Encrypt recusa o pedido)"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}
WITH_WWW=false
for arg in "$@"; do
    [ "$arg" = "--www" ] && WITH_WWW=true
done

if [ ! -f "$TEMPLATE" ]; then
    echo "Erro: $TEMPLATE nao encontrado."
    exit 1
fi

# O nginx tem de estar no ar em HTTP para responder ao desafio ACME.
echo "A garantir que o nginx esta a correr (HTTP)..."
docker compose up -d nginx >/dev/null

echo "Aguardando o nginx responder ao health check..."
for i in $(seq 1 30); do
    if docker compose exec -T nginx wget --quiet --tries=1 --spider http://localhost/health 2>/dev/null; then
        break
    fi
    sleep 2
done

echo "Dominio: $DOMAIN"
echo "Email:   $EMAIL"
echo ""

CERT_DOMAINS=(-d "$DOMAIN")
if [ "$WITH_WWW" = true ]; then
    CERT_DOMAINS+=(-d "www.$DOMAIN")
fi

echo "Obtendo certificado SSL via webroot..."
docker compose run --rm --entrypoint certbot certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    "${CERT_DOMAINS[@]}" \
    --email "$EMAIL" \
    --agree-tos \
    --non-interactive \
    --keep-until-expiring \
    --verbose

echo ""
echo "Gerando configuracao HTTPS a partir de $TEMPLATE..."
sed "s/\${DOMAIN}/${DOMAIN}/g" "$TEMPLATE" > "$TARGET"

# Se o www nao foi emitido, remove-o do server_name para o nginx nao aceitar
# SNI de um host sem certificado valido.
if [ "$WITH_WWW" = false ]; then
    sed -i "s/ www\.${DOMAIN}//g" "$TARGET"
fi

echo "Validando configuracao do nginx..."
docker compose exec -T nginx nginx -t

echo "Recarregando nginx..."
docker compose exec -T nginx nginx -s reload

echo "A garantir que o certbot renova automaticamente..."
docker compose up -d certbot >/dev/null

echo ""
echo "==================================="
echo "SSL configurado com sucesso!"
echo "==================================="
echo ""
echo "Seu site agora esta disponivel em:"
echo "  https://$DOMAIN"
if [ "$WITH_WWW" = true ]; then
    echo "  https://www.$DOMAIN"
fi
echo ""
echo "Os certificados serao renovados automaticamente pelo servico certbot."
echo "Depois de renovar, recarregue o nginx para usar o novo certificado:"
echo "  docker compose exec nginx nginx -s reload"
