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

# Obter certificado (método webroot, nginx continua rodando)
echo "Obtendo certificado SSL via webroot..."
docker compose run --rm --entrypoint certbot certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive \
    --verbose

# Criar configuração HTTPS dedicada (ssl.conf)
echo "Gerando configuração HTTPS (ssl.conf)..."
cat > docker/nginx/conf.d/ssl.conf <<EOF
server {
    listen 443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Certbot challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /admin/ {
        limit_req zone=auth_limit burst=10 nodelay;
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Testar configuração e reiniciar nginx
echo "Validando configuração do nginx..."
docker compose exec nginx nginx -t || { echo "Configuração NGINX inválida"; exit 1; }
echo "Reiniciando nginx..."
docker compose up -d nginx

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
