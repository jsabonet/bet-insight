# Multi-stage build para React + Vite
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependências
RUN npm ci --only=production

# Copiar código fonte
COPY . .

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
