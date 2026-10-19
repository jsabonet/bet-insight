#!/bin/sh
set -e

# Gera /config.js: o frontend le window.ENV.API_URL em runtime
# (frontend/src/services/api.js), por isso o URL da API pode ser mudado sem
# reconstruir a imagem: basta reiniciar o container.
# O default /api e relativo: o nginx faz proxy de /api/ para o backend.
API_URL="${VITE_API_URL:-/api}"

cat > /usr/share/nginx/html/config.js <<EOF
window.ENV = {
  API_URL: '$API_URL'
};
EOF

echo "Frontend configurado com API_URL: $API_URL"

exec "$@"
