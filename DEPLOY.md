# Deploy no Digital Ocean - PlacarCerto

Guia completo para fazer deploy da aplicação PlacarCerto em um Droplet da Digital Ocean usando Docker.

## 📋 Pré-requisitos

- Conta na Digital Ocean
- Domínio próprio (opcional, mas recomendado para SSL)
- Chaves API (Football Data, API-Football, Google Gemini, PaySuite)

## 🚀 Passo 1: Criar Droplet na Digital Ocean

1. **Acesse o painel da Digital Ocean**
   - Vá para https://cloud.digitalocean.com

2. **Crie um novo Droplet**
   - Clique em "Create" → "Droplets"
   - **Imagem**: Ubuntu 22.04 LTS
   - **Plano**: 
     - Básico: $12/mês (2GB RAM, 1 vCPU, 50GB SSD) - Recomendado para início
     - Premium: $18/mês (2GB RAM, 2 vCPU, 60GB SSD) - Melhor performance
   - **Datacenter**: Escolha o mais próximo dos seus usuários (ex: New York, Amsterdam)
   - **Autenticação**: SSH key (mais seguro) ou senha
   - **Hostname**: placarcerto-prod

3. **Aguarde a criação** (1-2 minutos)
   - Anote o IP público do servidor

## 🔧 Passo 2: Configuração Inicial do Servidor

### 2.1. Conectar via SSH

```bash
ssh root@SEU_IP_DO_DROPLET
```

### 2.2. Executar setup inicial

```bash
# Fazer upload do script de setup
# No seu computador local:
scp scripts/setup-server.sh root@SEU_IP:/root/

# No servidor:
chmod +x setup-server.sh
./setup-server.sh
```

Este script irá:
- ✅ Atualizar o sistema
- ✅ Instalar Docker e Docker Compose
- ✅ Criar usuário 'appuser'
- ✅ Configurar firewall
- ✅ Instalar ferramentas úteis

### 2.3. Mudar para usuário da aplicação

```bash
su - appuser
cd ~
```

## 📦 Passo 3: Deploy da Aplicação

### 3.1. Clonar repositório

```bash
# Se usar Git (recomendado)
git clone https://github.com/SEU-USUARIO/placarcerto.git
cd placarcerto

# OU fazer upload direto
# No seu computador:
# rsync -avz --exclude 'node_modules' --exclude 'venv' --exclude '__pycache__' \
#   /caminho/local/bet-insight/ appuser@SEU_IP:~/placarcerto/
```

### 3.2. Configurar variáveis de ambiente

```bash
# Backend
cp backend/.env.production.example backend/.env.production
nano backend/.env.production
```

**Configurações obrigatórias:**

```env
DEBUG=False
SECRET_KEY=GERE-UMA-CHAVE-SECRETA-ALEATORIA-FORTE
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,SEU_IP

DB_PASSWORD=SENHA-FORTE-POSTGRES

# APIs
FOOTBALL_DATA_API_KEY=sua-chave
API_FOOTBALL_KEY=sua-chave
GOOGLE_GEMINI_API_KEY=sua-chave

# PaySuite
PAYSUITE_API_KEY=sua-chave
PAYSUITE_API_SECRET=seu-secret
PAYSUITE_WEBHOOK_URL=https://seu-dominio.com/api/subscriptions/payments/webhook/
```

**Gerar SECRET_KEY segura:**
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

```bash
# Frontend (opcional - padrão já funciona)
cp frontend/.env.production.example frontend/.env.production
nano frontend/.env.production
```

### 3.3. Executar deploy

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
```

Este script irá:
- 🔨 Construir as imagens Docker
- 🚀 Iniciar todos os containers
- 📊 Executar migrações do banco
- 📁 Coletar arquivos estáticos

### 3.4. Criar superusuário Django

```bash
docker-compose exec backend python manage.py createsuperuser
```

## 🌐 Passo 4: Configurar Domínio (Opcional mas Recomendado)

### 4.1. Apontar domínio para o servidor

No painel do seu provedor de domínio, crie registros DNS:

```
Tipo    Nome    Valor               TTL
A       @       SEU_IP_DO_DROPLET   3600
A       www     SEU_IP_DO_DROPLET   3600
```

### 4.2. Aguardar propagação DNS (5-30 minutos)

Verificar:
```bash
nslookup seu-dominio.com
```

### 4.3. Configurar SSL com Let's Encrypt

```bash
./scripts/setup-ssl.sh seu-dominio.com seu-email@exemplo.com
```

Isso irá:
- 🔒 Obter certificado SSL gratuito
- 🔄 Configurar renovação automática
- ✅ Habilitar HTTPS

## ✅ Passo 5: Verificar Deploy

### 5.1. Verificar containers

```bash
docker-compose ps
```

Todos devem estar "Up" e "healthy":
- ✅ placarcerto_db
- ✅ placarcerto_redis
- ✅ placarcerto_backend
- ✅ placarcerto_frontend
- ✅ placarcerto_nginx

### 5.2. Verificar logs

```bash
# Todos os containers
docker-compose logs -f

# Apenas backend
docker-compose logs -f backend

# Apenas nginx
docker-compose logs -f nginx
```

### 5.3. Testar aplicação

```bash
# Health check
curl http://SEU_IP/health

# API backend
curl http://SEU_IP/api/subscriptions/plans/

# Frontend
curl -I http://SEU_IP/
```

**Abra no navegador:**
- Frontend: `http://SEU_IP` ou `https://seu-dominio.com`
- Admin Django: `http://SEU_IP/admin/` ou `https://seu-dominio.com/admin/`

## 🔄 Atualizações e Manutenção

### Atualizar aplicação

```bash
cd ~/placarcerto
git pull origin main
./scripts/deploy.sh
```

### Ver logs em tempo real

```bash
docker-compose logs -f
```

### Reiniciar serviços

```bash
# Todos os serviços
docker-compose restart

# Apenas backend
docker-compose restart backend

# Apenas frontend
docker-compose restart frontend
```

### Parar aplicação

```bash
docker-compose down
```

### Backup do banco de dados

```bash
# Criar backup
docker-compose exec db pg_dump -U postgres betinsight_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup_20260102.sql | docker-compose exec -T db psql -U postgres betinsight_db
```

### Limpar Docker (liberar espaço)

```bash
# Remover imagens não utilizadas
docker system prune -a

# Remover volumes órfãos
docker volume prune
```

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs backend

# Verificar status
docker-compose ps
```

### Erro de conexão com banco

```bash
# Verificar se DB está rodando
docker-compose ps db

# Ver logs do banco
docker-compose logs db

# Testar conexão manualmente
docker-compose exec backend python manage.py dbshell
```

### Erro 502 Bad Gateway

```bash
# Verificar se backend está respondendo
docker-compose exec nginx curl http://backend:8000/admin/login/

# Ver logs do nginx
docker-compose logs nginx

# Reiniciar nginx
docker-compose restart nginx
```

### Arquivos estáticos não carregam

```bash
# Recoletar estáticos
docker-compose exec backend python manage.py collectstatic --noinput

# Verificar permissões
docker-compose exec backend ls -la /app/staticfiles
```

### Logs de debug

```bash
# Backend detalhado
docker-compose exec backend python manage.py check --deploy

# Variáveis de ambiente
docker-compose exec backend env | grep DB_

# Processos rodando
docker-compose exec backend ps aux
```

## 📊 Monitoramento

### Recursos do servidor

```bash
# CPU e memória
htop

# Espaço em disco
df -h

# Docker stats
docker stats
```

### Logs de acesso

```bash
# Nginx access log
docker-compose exec nginx tail -f /var/log/nginx/access.log

# Nginx error log
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

## 🔐 Segurança

### Firewall

```bash
# Verificar regras
sudo ufw status

# Permitir porta (se necessário)
sudo ufw allow 8080/tcp
```

### Atualizar sistema

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Renovação SSL automática

O certificado SSL renova automaticamente via Certbot. Para forçar renovação:

```bash
docker-compose run --rm certbot renew
docker-compose restart nginx
```

## 💰 Custos Estimados

| Item | Custo Mensal (USD) |
|------|-------------------|
| Droplet 2GB | $12-18 |
| Domínio | $10-15/ano |
| APIs (depende do uso) | $0-50 |
| **Total** | **~$15-70/mês** |

## 📞 Suporte

- Digital Ocean Docs: https://docs.digitalocean.com
- Docker Docs: https://docs.docker.com
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/

## 🎉 Deploy Completo!

Sua aplicação PlacarCerto agora está rodando em produção! 🚀

Acesse:
- 🌐 Frontend: https://seu-dominio.com
- ⚙️ Admin: https://seu-dominio.com/admin/
- 📡 API: https://seu-dominio.com/api/

---

**Dicas finais:**
- Configure monitoramento (ex: UptimeRobot, Datadog)
- Configure backups automáticos do banco
- Monitore os logs regularmente
- Mantenha o sistema atualizado
