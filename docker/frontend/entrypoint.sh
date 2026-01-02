#!/bin/sh
set -e

# Substituir variáveis de ambiente no bundle JavaScript (se necessário)
# Criar arquivo de configuração runtime
cat > /usr/share/nginx/html/config.js <<EOF
window.ENV = {
  API_URL: '${VITE_API_URL:-http://localhost:8000}'
};
EOF

echo "Frontend configurado com API_URL: ${VITE_API_URL:-http://localhost:8000}"

exec "$@"
