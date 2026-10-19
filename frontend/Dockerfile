# Multi-stage build para React + Vite
FROM node:20-alpine AS builder

WORKDIR /app

# Limitar o heap do Node: em droplets de 512 MB-2 GB o V8 assume um limite
# alto e o build é morto pelo OOM killer. Silenciar o ruído do npm também
# reduz I/O num disco pequeno.
ENV NODE_OPTIONS=--max-old-space-size=512 \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_PROGRESS=false

# Copiar package files
COPY frontend/package*.json ./

# Instalar dependências (inclui devDependencies para build)
# Use --legacy-peer-deps para resolver conflito de react-helmet-async com React 19
RUN npm ci --legacy-peer-deps --no-audit --no-fund

# Copiar código fonte
COPY frontend/ .

# Build da aplicação para produção
RUN npm run build

# Stage 2: Nginx para servir arquivos estáticos
FROM nginx:alpine

# Copiar configuração customizada do nginx
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copiar build do React do stage anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar script de entrypoint para substituir variáveis de ambiente
COPY docker/frontend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
