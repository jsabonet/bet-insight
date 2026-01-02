# 🚀 Guia Completo de Deploy - PlacarCerto

Guia detalhado passo-a-passo para fazer deploy da aplicação PlacarCerto em um Droplet da Digital Ocean usando Docker.

## 📋 Pré-requisitos Necessários

Antes de começar, tenha em mãos:

- ✅ Conta ativa na Digital Ocean (https://cloud.digitalocean.com)
- ✅ Cartão de crédito/débito para Digital Ocean
- ✅ Domínio próprio (opcional, mas recomendado - ex: namecheap.com, godaddy.com)
- ✅ Chaves de API:
  - Football Data API: https://www.football-data.org/client/register
  - API-Football: https://www.api-football.com/
  - Google Gemini: https://ai.google.dev/
  - PaySuite (M-Pesa): Contato comercial PaySuite Moçambique
- ✅ Cliente SSH instalado (já vem no Windows 10+, Mac e Linux)


## 🚀 PARTE 1: Criar e Configurar Droplet na Digital Ocean

### Passo 1.1: Criar conta e acessar painel

```bash
# 1. Acesse: https://cloud.digitalocean.com
# 2. Clique em "Sign Up" se não tiver conta
# 3. Complete o cadastro e adicione método de pagamento
# 4. Você receberá $200 em créditos por 60 dias (promoção para novos usuários)
```

### Passo 1.2: Criar Droplet

1. **No painel da Digital Ocean, clique em "Create" → "Droplets"**

2. **Configure o Droplet:**

   **Região (Choose a datacenter region):**
   ```
   - Frankfurt, Germany (para Europa/África)
   - New York, USA (para Américas)
   - Escolha o mais próximo dos seus usuários
   ```

   **Imagem (Choose an image):**
   ```
   - Distributions → Ubuntu → 24.04 (LTS) x64 ⭐ RECOMENDADO
   - OU Ubuntu 22.04 (LTS) x64 (também funciona)
   ```

   **Tamanho (Choose a size):**
   ```
   Basic Plan (Recomendado para início)
   
   CPU Options: Regular
   
   Planos disponíveis:
   ┌─────────────────────────────────────────────────┐
   │ $6/mês  - 1GB RAM, 1 vCPU, 25GB SSD  (Mínimo)  │
   │ $12/mês - 2GB RAM, 1 vCPU, 50GB SSD  ⭐ IDEAL  │
   │ $18/mês - 2GB RAM, 2 vCPU, 60GB SSD  (Melhor)  │
   │ $24/mês - 4GB RAM, 2 vCPU, 80GB SSD  (Premium) │
   └─────────────────────────────────────────────────┘
   
   ⭐ Recomendação: Começar com $12/mês (2GB RAM)
   ```

   **Autenticação (Choose Authentication Method):**
   ```
   Opção 1 - SSH Key (MAIS SEGURO - Recomendado):
   - Clique em "New SSH Key"
   - No seu computador local, gere uma chave SSH:
   
   Windows (PowerShell):
   ssh-keygen -t ed25519 -C "seu-email@exemplo.com"
   # Pressione Enter 3 vezes (usa valores padrão)
   type C:\Users\SEU_USUARIO\.ssh\id_ed25519.pub
   # Copie o conteúdo que aparecer
   
   Mac/Linux (Terminal):
   ssh-keygen -t ed25519 -C "seu-email@exemplo.com"
   # Pressione Enter 3 vezes
   cat ~/.ssh/id_ed25519.pub
   # Copie o conteúdo que aparecer
   
   - Cole a chave pública no campo da Digital Ocean
   - Dê um nome: "Meu Computador"
   
   Opção 2 - Password (Mais simples):
   - Escolha uma senha forte (mínimo 8 caracteres)
   - Anote a senha em local seguro
   ```

   **Opções Adicionais (Additional options):**
   ```
   ☑ IPv6
   ☐ User data (deixe desmarcado)
   ☐ Monitoring (pode ativar depois)
   ```

   **Hostname & Tags:**
   ```
   Hostname: placarcerto-prod
   Tags: production, placarcerto
   ```

3. **Clique em "Create Droplet"**
   - Aguarde 1-2 minutos para criação
   - **ANOTE O IP PÚBLICO** que aparecerá (ex: 164.90.123.45)

### Passo 1.3: Primeiro acesso ao servidor

```bash
# Conectar via SSH (substitua SEU_IP pelo IP do droplet)

# Se usou SSH Key:
ssh root@SEU_IP

# Se usou Password:
ssh root@SEU_IP
# Digite a senha quando solicitado

# Primeira conexão pedirá para confirmar fingerprint
# Digite: yes

# Você verá algo como:
# Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-89-generic x86_64)
# root@placarcerto-prod:~#
```

### Passo 1.4: Atualizar sistema (primeiro comando no servidor)

```bash
# Atualizar lista de pacotes
apt-get update

# Atualizar pacotes instalados
apt-get upgrade -y

# Isso leva 2-5 minutos
```

## 🔧 PARTE 2: Instalar Docker e Dependências

### Passo 2.1: Instalar Docker

**Método 1 - Script oficial (tente primeiro):**

```bash
# Baixar script de instalação
curl -fsSL https://get.docker.com -o get-docker.sh

# Executar instalação
sh get-docker.sh

# Habilitar Docker para iniciar automaticamente
systemctl enable docker
systemctl start docker

# Verificar instalação
docker --version
# Deve mostrar: Docker version 24.x.x ou superior

# Testar Docker
docker run hello-world
# Deve mostrar: "Hello from Docker!" e mensagem de sucesso
```

**Se der erro 404 ou "Unit file docker.service does not exist", use o Método 2:**

**Método 2 - Instalação manual (se Método 1 falhar):**

```bash
# Remover resíduos de instalações anteriores
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Atualizar repositórios
apt-get update

# Instalar dependências
apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Adicionar chave GPG oficial do Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Adicionar repositório Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Atualizar índice de pacotes
apt-get update

# Instalar Docker Engine, CLI e Containerd
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Se ainda der erro no containerd.io, instale versão específica:
# apt-get install -y containerd.io=1.6.* docker-ce docker-ce-cli docker-buildx-plugin docker-compose-plugin

# Habilitar e iniciar Docker
systemctl enable docker
systemctl start docker

# Verificar status
systemctl status docker
# Pressione 'q' para sair

# Verificar versão
docker --version
# Deve mostrar: Docker version 24.x.x ou superior

# Testar instalação
docker run hello-world
# Deve mostrar:
# Hello from Docker!
# This message shows that your installation appears to be working correctly.
```

**Saída esperada do teste:**
```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
c1ec31eb5944: Pull complete
Digest: sha256:1234567890abcdef...
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

#### Nota específica para Ubuntu 24.04 (noble)

✅ **TESTADO E FUNCIONANDO** - Ubuntu 24.04 com Docker 29.1.3

Se aparecerem erros como:
- `404 Not Found` ao instalar `containerd.io`
- `Unit file docker.service does not exist`

**Use a Opção B abaixo (mais simples e estável):**

**Opção B — Pacote estável do Ubuntu (✅ RECOMENDADO para 24.04)**

```bash
# Usar pacotes mantidos pela Canonical
apt-get update
apt-get install -y docker.io docker-compose-plugin

# Habilitar e iniciar serviço
systemctl enable --now docker

# Verificar e testar
docker --version
# Resultado esperado: Docker version 29.1.3, build f52814d

docker run hello-world
# Deve mostrar: "Hello from Docker!"
```

**Opção A — Docker CE (alternativa, requer versão específica)**

```bash
# Garantir repositório Docker já adicionado (feito no Método 2)
apt-get update

# Instalar containerd.io em versão compatível (>= 1.7.27)
apt-get install -y containerd.io=1.7.29-1~ubuntu.24.04~noble

# Instalar Docker CE e plugins
apt-get install -y docker-ce docker-ce-cli docker-buildx-plugin docker-compose-plugin

# Habilitar e iniciar serviço
systemctl enable --now docker

# Verificar e testar
docker --version
docker run hello-world
```

Se a linha acima de `containerd.io` falhar, liste versões disponíveis e escolha a mais recente 1.7.x:

```bash
apt-cache madison containerd.io | head -10
# Exemplo de instalação alternativa:
apt-get install -y containerd.io=1.7.28-2~ubuntu.24.04~noble
```

**A Opção B é mais simples e comprovadamente estável para Ubuntu 24.04. A Opção A usa pacotes oficiais Docker Inc. com versões mais recentes mas pode ter problemas de disponibilidade de pacotes.**

### Passo 2.2: Instalar Docker Compose

**Nota:** Se instalou Docker usando a Opção B (docker.io), o plugin `docker-compose-plugin` já está instalado. Pule para verificação.

```bash
# Se usar Docker CE, baixar Docker Compose standalone (opcional)
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permissão de execução
chmod +x /usr/local/bin/docker-compose

# Verificar instalação (tente ambos os comandos)
docker compose version
# OU
docker-compose --version

# Deve mostrar: Docker Compose version v2.x.x
```

**Nota:** O comando moderno é `docker compose` (sem hífen). Ambos funcionam se o plugin estiver instalado.

### Passo 2.3: Instalar ferramentas úteis

```bash
# Git para clonar repositório
apt-get install -y git

# Ferramentas de sistema
apt-get install -y curl wget nano htop net-tools

# Editor de texto alternativo (vim)
apt-get install -y vim

# Verificar instalações
git --version
nano --version
```

### Passo 2.4: Configurar firewall

```bash
# Instalar UFW (já vem no Ubuntu)
apt-get install -y ufw

# Permitir SSH (IMPORTANTE - fazer ANTES de ativar firewall)
ufw allow 22/tcp

# Permitir HTTP e HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Ativar firewall
ufw --force enable

# Verificar status
ufw status
# Deve mostrar:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
```

### Passo 2.5: Criar usuário não-root (segurança)

```bash
# Criar usuário para a aplicação
useradd -m -s /bin/bash appuser

# Definir senha (escolha uma senha forte)
passwd appuser
# Digite a senha 2 vezes

# Adicionar ao grupo docker (para rodar comandos docker sem sudo)
usermod -aG docker appuser

# Adicionar ao grupo sudo (para comandos administrativos)
usermod -aG sudo appuser

# Verificar criação
id appuser
# Deve mostrar: uid=1000(appuser) gid=1000(appuser) groups=1000(appuser),27(sudo),999(docker)
```

## 📦 PARTE 3: Preparar e Fazer Upload da Aplicação

### Passo 3.1: Opção A - Clonar do Git (Recomendado)

```bash
# Mudar para usuário appuser
su - appuser

# Ir para diretório home
cd ~

# Clonar repositório
# Substitua jsabonet pelo seu usuário GitHub se for diferente
git clone https://github.com/jsabonet/bet-insight.git placarcerto

# OU se o repositório for privado, use token:
# git clone https://SEU_TOKEN@github.com/jsabonet/bet-insight.git placarcerto

# Entrar no diretório
cd placarcerto

# Verificar arquivos
ls -la
# Deve mostrar: backend/, frontend/, docker/, scripts/, etc.
```

### Passo 3.2: Opção B - Upload direto do computador local

```bash
# No seu computador LOCAL (não no servidor):

# Windows (PowerShell):
# Comprimir projeto
Compress-Archive -Path "D:\Projectos\Football\bet-insight\*" -DestinationPath "placarcerto.zip"

# Enviar para servidor
scp placarcerto.zip root@SEU_IP:/home/appuser/

# Conectar ao servidor e descomprimir
ssh root@SEU_IP
su - appuser
cd ~
apt-get install -y unzip
unzip placarcerto.zip -d placarcerto
cd placarcerto


# Mac/Linux (Terminal):
# Comprimir e enviar
cd /caminho/para/bet-insight
tar czf placarcerto.tar.gz *
scp placarcerto.tar.gz root@SEU_IP:/home/appuser/

# Conectar e descomprimir
ssh root@SEU_IP
su - appuser
cd ~
tar xzf placarcerto.tar.gz -C placarcerto
cd placarcerto
```

### Passo 3.3: Verificar estrutura de arquivos

```bash
# Verificar que todos os arquivos necessários existem
ls -la

# Deve conter:
# ✅ backend/
# ✅ frontend/
# ✅ docker/
# ✅ docker-compose.yml
# ✅ scripts/
# ✅ DEPLOY.md

# Dar permissão de execução aos scripts
chmod +x scripts/*.sh

# Verificar
ls -la scripts/
# Todos devem ter 'x' nas permissões
```

## ⚙️ PARTE 4: Configurar Variáveis de Ambiente

### Passo 4.1: Configurar Backend

```bash
# Copiar template
cp backend/.env.production.example backend/.env.production

# Editar arquivo
nano backend/.env.production
```

**Cole esta configuração e edite os valores:**

```env
# ==============================================
# CONFIGURAÇÃO DE PRODUÇÃO - BACKEND
# ==============================================

# Django Settings
DEBUG=False
SECRET_KEY=COLE-AQUI-A-CHAVE-SECRETA-GERADA-ABAIXO
ALLOWED_HOSTS=178.128.198.19,seu-dominio.com,www.seu-dominio.com

# Database (mantenha estes valores)
DB_NAME=betinsight_db
DB_USER=postgres
DB_PASSWORD=SenhaPostgres2026!Forte#Segura
DB_HOST=db
DB_PORT=5432

# Redis (mantenha este valor)
REDIS_URL=redis://redis:6379/0

# APIs Externas - SUBSTITUA COM SUAS CHAVES
FOOTBALL_DATA_API_KEY=sua-chave-football-data-aqui
FOOTBALL_DATA_URL=https://api.football-data.org/v4

API_FOOTBALL_KEY=sua-chave-api-football-aqui
API_FOOTBALL_HOST=v3.football.api-sports.io
API_FOOTBALL_URL=https://v3.football.api-sports.io

GOOGLE_GEMINI_API_KEY=sua-chave-gemini-aqui

# PaySuite (M-Pesa) - CONFIGURE COM SUAS CREDENCIAIS
PAYSUITE_API_KEY=sua-paysuite-api-key
PAYSUITE_API_SECRET=sua-paysuite-api-secret
PAYSUITE_BASE_URL=https://paysuite.tech/api/v1
PAYSUITE_ENVIRONMENT=production
PAYSUITE_WEBHOOK_URL=https://seu-dominio.com/api/subscriptions/payments/webhook/
PAYSUITE_MODE=token

# Email (opcional - configure depois se quiser)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=seu-email@gmail.com
# EMAIL_HOST_PASSWORD=sua-senha-de-app
# DEFAULT_FROM_EMAIL=PlacarCerto <noreply@seu-dominio.com>

# Firebase (opcional - configure depois)
FCM_SERVER_KEY=

# Limites
FREE_ANALYSIS_LIMIT=3
PREMIUM_ANALYSIS_LIMIT=100
```

**IMPORTANTE: Gerar SECRET_KEY segura**

```bash
# Abrir um novo terminal SSH no servidor
# Gerar SECRET_KEY
python3 -c 'import secrets; print(secrets.token_urlsafe(50))'

# Copie o resultado (será algo como):
# xK9mPqR3vYw2NzLp8cTfHj7SgQkVbDnWm4xZa6yEuI5oUrTiWlNdG

# Cole no campo SECRET_KEY do arquivo .env.production
```

**Salvar arquivo:**
- Pressione `Ctrl + X`
- Digite `Y`
- Pressione `Enter`

### Passo 4.2: Configurar Frontend

```bash
# Copiar template
cp frontend/.env.production.example frontend/.env.production

# Editar arquivo
nano frontend/.env.production
```

**Cole esta configuração:**

```env
# ==============================================
# CONFIGURAÇÃO DE PRODUÇÃO - FRONTEND
# ==============================================

# API Backend URL
# Use o IP do seu droplet:
VITE_API_URL=http://178.128.198.19

# Quando configurar domínio, mude para:
# VITE_API_URL=https://seu-dominio.com

# Ambiente
VITE_APP_ENV=production
```

**Salvar:**
- `Ctrl + X` → `Y` → `Enter`

### Passo 4.3: Verificar configurações

```bash
# Verificar que arquivos .env foram criados
ls -la backend/.env.production
ls -la frontend/.env.production

# Ambos devem existir

# Ver primeiras linhas (para confirmar)
head -n 5 backend/.env.production
# Deve mostrar DEBUG=False, SECRET_KEY=..., etc.
```

## 🏗️ PARTE 5: Fazer Deploy (Build e Start)

### Passo 5.1: Executar deploy inicial

```bash
# Verificar que está no diretório correto
pwd
# Deve mostrar: /home/appuser/placarcerto

# Executar script de deploy
./scripts/deploy.sh

# O script irá:
# 1. Baixar imagens Docker necessárias
# 2. Construir imagem do backend (5-10 minutos)
# 3. Construir imagem do frontend (3-5 minutos)
# 4. Criar containers PostgreSQL e Redis
# 5. Iniciar backend e frontend
# 6. Executar migrações do banco
# 7. Coletar arquivos estáticos

# Processo completo: 10-20 minutos dependendo da conexão
```

**Saída esperada do script:**
```
===================================
PlacarCerto - Deploy
===================================
Parando containers...
Construindo e iniciando containers...
[+] Building 234.5s (23/23) FINISHED
[+] Running 6/6
 ✔ Network placarcerto_app_network  Created
 ✔ Container placarcerto_db          Started
 ✔ Container placarcerto_redis       Started
 ✔ Container placarcerto_backend     Started
 ✔ Container placarcerto_frontend    Started
 ✔ Container placarcerto_nginx       Started
===================================
Deploy concluído!
===================================
```

### Passo 5.2: Verificar containers rodando

```bash
# Ver status dos containers
docker-compose ps

# Todos devem estar "Up" e "healthy":
# NAME                     STATUS
# placarcerto_db          Up (healthy)
# placarcerto_redis       Up (healthy)
# placarcerto_backend     Up (healthy)
# placarcerto_frontend    Up
# placarcerto_nginx       Up (healthy)
```

### Passo 5.3: Ver logs em tempo real

```bash
# Ver logs de todos os containers
docker compose logs -f

# Ver apenas logs do backend
docker compose logs -f backend

# Ver apenas logs do nginx
docker compose logs -f nginx

# Parar visualização: Ctrl + C
```

### Passo 5.4: Criar superusuário Django (admin)

```bash
# Executar comando dentro do container backend
docker compose exec backend python manage.py createsuperuser

# Preencher informações:
# Username: admin
# Email: seu-email@exemplo.com
# Password: ***** (escolha senha forte)
# Password (again): *****
# Superuser created successfully.
```

## 🌐 PARTE 6: Testar Aplicação

### Passo 6.1: Testes locais no servidor

```bash
# Teste 1: Health check
curl http://localhost/health
# Deve retornar: healthy

# Teste 2: API Backend
curl http://localhost/api/subscriptions/plans/
# Deve retornar JSON com planos

# Teste 3: Admin Django
curl -I http://localhost/admin/
# Deve retornar: HTTP/1.1 200 OK

# Teste 4: Frontend
curl -I http://localhost/
# Deve retornar: HTTP/1.1 200 OK
```

### Passo 6.2: Testar do seu computador

```bash
# No navegador, acesse:

# 1. Frontend
http://SEU_IP

# 2. Admin Django
http://SEU_IP/admin/
# Login com usuário criado no passo 5.4

# 3. API
http://SEU_IP/api/subscriptions/plans/
```

**Você deve ver:**
- ✅ Frontend PlacarCerto carregando
- ✅ Página de login funcionando
- ✅ Admin Django acessível
- ✅ API retornando dados JSON

## 🔐 PARTE 7: Configurar Domínio e SSL (Opcional mas Recomendado)

### Passo 7.1: Apontar domínio para servidor

**No painel do seu provedor de domínio (ex: Namecheap, GoDaddy):**

1. **Encontre a seção DNS Management**

2. **Adicione estes registros:**

```
Tipo    Host    Valor               TTL
A       @       SEU_IP_DO_DROPLET   3600
A       www     SEU_IP_DO_DROPLET   3600
```

Exemplo prático:
```
Tipo    Host    Valor           TTL
A       @       164.90.123.45   3600
A       www     164.90.123.45   3600
```

3. **Salvar mudanças**
   - Propagação DNS leva 5 minutos a 48 horas
   - Geralmente funciona em 10-30 minutos

### Passo 7.2: Verificar propagação DNS

```bash
# No seu computador local:

# Verificar registro A
nslookup seu-dominio.com

# Ou usar site:
# https://dnschecker.org

# Deve mostrar o IP do seu droplet
```

### Passo 7.3: Atualizar configuração backend

```bash
# No servidor, editar .env
nano backend/.env.production

# Atualizar linha ALLOWED_HOSTS:
ALLOWED_HOSTS=SEU_IP,seu-dominio.com,www.seu-dominio.com

# Atualizar PAYSUITE_WEBHOOK_URL:
PAYSUITE_WEBHOOK_URL=https://seu-dominio.com/api/subscriptions/payments/webhook/

# Salvar: Ctrl+X, Y, Enter

# Reiniciar backend
docker compose restart backend
```

### Passo 7.4: Atualizar configuração frontend

```bash
# Editar .env do frontend
nano frontend/.env.production

# Atualizar para usar domínio:
VITE_API_URL=https://seu-dominio.com

# Salvar: Ctrl+X, Y, Enter

# Rebuild frontend
docker compose up -d --build frontend
```

### Passo 7.5: Configurar SSL com Let's Encrypt

```bash
# Executar script de SSL
./scripts/setup-ssl.sh placarcerto.digital jsabonete09@gmail.com

# O script irá:
# 1. Parar nginx temporariamente
# 2. Obter certificado SSL gratuito
# 3. Configurar renovação automática
# 4. Atualizar configuração do nginx
# 5. Reiniciar nginx com HTTPS
```

**Saída esperada:**
```
===================================
Configuração SSL com Let's Encrypt
===================================
Domínio: seu-dominio.com
Email: seu-email@exemplo.com

Parando nginx...
Obtendo certificado SSL...
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/seu-dominio.com/fullchain.pem
Key is saved at: /etc/letsencrypt/live/seu-dominio.com/privkey.pem

Atualizando configuração do nginx...
Reiniciando nginx...
===================================
SSL configurado com sucesso!
===================================
```

### Passo 7.6: Testar HTTPS

```bash
# No navegador, acesse:
https://seu-dominio.com

# Deve ver:
# ✅ Cadeado verde (conexão segura)
# ✅ Site carregando normalmente
# ✅ HTTP redirecionando para HTTPS
```

## 📊 PARTE 8: Monitoramento e Manutenção

### Passo 8.1: Verificar saúde dos containers

```bash
# Ver containers rodando
docker-compose ps

# Ver uso de recursos
docker stats

# Ver logs em tempo real
docker-compose logs -f

# Ver apenas últimas 50 linhas
docker-compose logs --tail=50

# Ver logs de container específico
docker-compose logs -f backend
docker-compose logs -f nginx
```

### Passo 8.2: Comandos úteis de manutenção

```bash
# Reiniciar todos os serviços
docker-compose restart

# Reiniciar apenas um serviço
docker-compose restart backend
docker-compose restart frontend

# Parar todos os containers
docker-compose down

# Iniciar todos os containers
docker-compose up -d

# Ver uso de espaço em disco
df -h

# Limpar logs antigos do Docker
docker system prune -a --volumes
# CUIDADO: Isso remove tudo que não está em uso
```

### Passo 8.3: Backup do banco de dados

```bash
# Criar backup
docker-compose exec db pg_dump -U postgres betinsight_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Verificar backup criado
ls -lh backup_*.sql

# Fazer download do backup para seu computador (do seu PC):
scp appuser@SEU_IP:/home/appuser/placarcerto/backup_*.sql ./

# Restaurar backup (se necessário)
cat backup_20260102_143000.sql | docker-compose exec -T db psql -U postgres betinsight_db
```

### Passo 8.4: Atualizar aplicação

```bash
# Quando tiver novas mudanças:

# 1. Fazer pull das mudanças (se usar Git)
git pull origin main

# 2. Reconstruir e reiniciar
./scripts/deploy.sh

# 3. Ver logs
docker-compose logs -f

# 4. Testar no navegador
```

## 🐛 PARTE 9: Resolução de Problemas

### Problema 1: Container não inicia

```bash
# Ver logs do container
docker-compose logs backend

# Reiniciar container específico
docker-compose restart backend

# Reconstruir container
docker-compose up -d --build backend

# Ver eventos do Docker
docker events
```

### Problema 2: Erro 502 Bad Gateway

```bash
# Verificar se backend está rodando
docker-compose ps backend

# Testar conexão do nginx com backend
docker-compose exec nginx curl http://backend:8000/admin/

# Ver logs do nginx
docker-compose logs nginx

# Reiniciar nginx
docker-compose restart nginx
```

### Problema 3: Banco de dados não conecta

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps db

# Ver logs do banco
docker-compose logs db

# Testar conexão
docker-compose exec backend python manage.py dbshell
# Digite: \q para sair

# Reiniciar banco (CUIDADO: vai parar temporariamente)
docker-compose restart db
```

### Problema 4: Erro de migração

```bash
# Executar migrações manualmente
docker-compose exec backend python manage.py migrate

# Ver migrações pendentes
docker-compose exec backend python manage.py showmigrations

# Fazer fake migration (casos específicos)
docker-compose exec backend python manage.py migrate --fake
```

### Problema 5: Espaço em disco cheio

```bash
# Ver uso de espaço
df -h

# Limpar logs do Docker
docker system prune -a

# Limpar volumes não utilizados
docker volume prune

# Ver tamanho de imagens
docker images

# Remover imagens antigas
docker image prune -a
```

### Problema 6: Aplicação lenta

```bash
# Ver uso de recursos
htop
# Pressione F10 para sair

# Ver uso do Docker
docker stats

# Ver processos do PostgreSQL
docker-compose exec db ps aux

# Ver logs de erro
docker-compose logs | grep -i error
```

### Problema 7: SSL não funciona

```bash
# Verificar certificado
docker-compose exec nginx ls -la /etc/letsencrypt/live/

# Testar renovação manual
docker-compose run --rm certbot renew --dry-run

# Ver logs do certbot
docker-compose logs certbot

# Forçar renovação
docker-compose run --rm certbot renew --force-renewal
docker-compose restart nginx
```

## 📱 PARTE 10: Comandos Úteis Extras

### Comandos Docker Compose

```bash
# Ver versão
docker-compose --version

# Validar docker-compose.yml
docker-compose config

# Ver variáveis de ambiente
docker-compose config | grep environment -A 10

# Parar e remover tudo (CUIDADO)
docker-compose down -v

# Rebuild sem cache
docker-compose build --no-cache

# Ver redes Docker
docker network ls

# Ver volumes Docker
docker volume ls
```

### Comandos Django (dentro do backend)

```bash
# Shell Django
docker-compose exec backend python manage.py shell

# Criar nova migração
docker-compose exec backend python manage.py makemigrations

# Ver SQL de uma migração
docker-compose exec backend python manage.py sqlmigrate app_name migration_name

# Coletar estáticos
docker-compose exec backend python manage.py collectstatic --noinput

# Limpar sessões expiradas
docker-compose exec backend python manage.py clearsessions

# Ver configurações
docker-compose exec backend python manage.py diffsettings
```

### Comandos do Sistema

```bash
# Ver processos rodando
ps aux | grep python
ps aux | grep nginx

# Ver portas abertas
netstat -tulpn

# Ver espaço em disco
du -sh /home/appuser/placarcerto/*

# Ver logs do sistema
tail -f /var/log/syslog

# Ver memória RAM
free -h

# Ver uso de CPU
top
# Pressione 'q' para sair
```

## 🎓 PARTE 11: Checklist Final

Antes de considerar deploy completo, verifique:

### Funcionalidades

- [ ] Frontend carrega em https://seu-dominio.com
- [ ] Admin acessível em /admin/
- [ ] API retorna dados em /api/subscriptions/plans/
- [ ] Login/registro funcionando
- [ ] Análises de partidas funcionando
- [ ] Planos premium exibindo corretamente
- [ ] Pagamentos configurados (se aplicável)

### Segurança

- [ ] DEBUG=False no backend
- [ ] SECRET_KEY forte e única configurada
- [ ] ALLOWED_HOSTS configurado corretamente
- [ ] Firewall ativo (UFW)
- [ ] SSL/HTTPS funcionando
- [ ] Senha forte do PostgreSQL
- [ ] Superusuário Django criado

### Performance

- [ ] Arquivos estáticos sendo servidos
- [ ] Gzip compression ativo
- [ ] Cache Redis funcionando
- [ ] Containers com status "healthy"

### Backup e Manutenção

- [ ] Backup do banco configurado
- [ ] Logs sendo gerados
- [ ] Renovação SSL automática
- [ ] Documentação de acesso salva

## 💰 Custos Mensais Estimados

```
┌──────────────────────────────────────────┐
│ Item                    Custo (USD/mês)  │
├──────────────────────────────────────────┤
│ Droplet 2GB             $12.00           │
│ Domínio (.com)          ~$1.00           │
│ APIs (variável)         $0-50            │
├──────────────────────────────────────────┤
│ TOTAL                   ~$13-63/mês      │
└──────────────────────────────────────────┘

* Valores aproximados em USD
* Droplet pode ser escalado conforme necessidade
* APIs dependem do volume de requisições
```

## 📞 Suporte e Recursos

### Documentação Oficial

- Digital Ocean: https://docs.digitalocean.com
- Docker: https://docs.docker.com
- Django: https://docs.djangoproject.com
- React: https://react.dev

### Comunidade

- Digital Ocean Community: https://www.digitalocean.com/community
- Stack Overflow: https://stackoverflow.com
- Django Forum: https://forum.djangoproject.com

### Ferramentas de Monitoramento (Recomendadas)

- **UptimeRobot** (gratuito): https://uptimerobot.com
  - Monitorar se site está no ar
  - Receber alertas por email

- **Datadog** (trial gratuito): https://www.datadoghq.com
  - Monitoramento avançado
  - Métricas de performance

- **Sentry** (gratuito até 5k eventos/mês): https://sentry.io
  - Rastreamento de erros
  - Alertas em tempo real

## 🎉 Parabéns!

Se chegou até aqui e todos os passos foram executados com sucesso:

✅ Sua aplicação PlacarCerto está rodando em produção!
✅ Acessível via HTTPS com certificado SSL válido
✅ Banco de dados persistente e com backup
✅ Pronta para receber usuários e processar pagamentos

**Próximos passos sugeridos:**

1. Configurar monitoramento (UptimeRobot)
2. Configurar backups automáticos diários
3. Adicionar analytics (Google Analytics)
4. Testar fluxo completo de compra
5. Criar documentação para usuários finais
6. Configurar email transacional (SendGrid, Mailgun)
7. Implementar sistema de logs centralizado

---

**Desenvolvido com ❤️ para Moçambique**

Para suporte técnico ou dúvidas sobre este deploy, consulte:
- Arquivo README.md do projeto
- Issues no repositório Git
- Documentação da Digital Ocean

