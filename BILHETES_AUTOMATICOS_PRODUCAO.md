# 🚀 **Sistema de Bilhetes Automáticos - PRODUÇÃO**

## 📊 **Comparação: Desenvolvimento vs Produção**

| Aspecto | Desenvolvimento (Windows) | Produção (Linux/Docker) |
|---------|---------------------------|-------------------------|
| **Como Rodar** | Duplo clique em `.bat` | Docker Compose automático |
| **Agendamento** | Task Scheduler Windows | Celery Beat + Redis |
| **Banco de Dados** | SQLite | PostgreSQL |
| **Cache/Broker** | Sem Redis | Redis |
| **Servidor Web** | Django runserver | Gunicorn + Nginx |
| **Escalabilidade** | Limitada | Alta (múltiplos workers) |
| **Confiabilidade** | Manual | Automático 24/7 |

---

## ✅ **Solução Criada para Produção**

Criei um setup **completo e pronto para deploy** com Docker:

### **📁 Arquivos Criados:**

1. ✅ `docker-compose.production.yml` - Orquestração completa
2. ✅ `.env.production.example` - Variáveis de ambiente
3. ✅ `nginx/nginx.conf` - Configuração do Nginx
4. ✅ `DEPLOY_PRODUCAO.md` - Guia completo de deploy

---

## 🎯 **Como Funciona em Produção**

### **Arquitetura:**

```
Internet → Nginx (80/443)
          ↓
       Django API (Gunicorn)
          ↓
    PostgreSQL + Redis
          ↓
  Celery Worker + Celery Beat
          ↓
  Bilhetes Gerados Automaticamente!
```

### **Componentes:**

1. **Django (Gunicorn)** - API REST
2. **PostgreSQL** - Banco de dados robusto
3. **Redis** - Message broker para Celery
4. **Celery Worker** - Processa tasks em background
5. **Celery Beat** - Agenda tasks (gera bilhetes às 06:00 UTC diariamente)
6. **Nginx** - Reverse proxy e SSL

---

## 🚀 **Deploy em 5 Passos**

### **1. Preparar Servidor**

```bash
# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### **2. Fazer Upload do Projeto**

```bash
# Via SCP
scp -r bet-insight/ user@servidor:/var/www/

# Ou via Git
cd /var/www
git clone <seu-repo> bet-insight
```

### **3. Configurar Variáveis**

```bash
cd /var/www/bet-insight
cp .env.production.example .env
nano .env
```

**Edite:**
- `SECRET_KEY` - Chave única e secreta
- `DB_PASSWORD` - Senha forte
- `ALLOWED_HOSTS` - Seu domínio
- `API_FOOTBALL_KEY` - Sua chave
- `GOOGLE_AI_KEY` - Sua chave

### **4. Iniciar Tudo**

```bash
# Build e start
docker-compose -f docker-compose.production.yml up -d

# Migrations
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# Criar admin
docker-compose -f docker-compose.production.yml exec web python manage.py createsuperuser
```

### **5. Verificar**

```bash
# Ver logs do Celery Beat (scheduler)
docker-compose -f docker-compose.production.yml logs -f celery_beat

# Ver logs do Celery Worker (executor)
docker-compose -f docker-compose.production.yml logs -f celery_worker

# Testar geração manual
docker-compose -f docker-compose.production.yml exec web python manage.py generate_daily_bets
```

---

## ⏰ **Agendamento Automático**

O **Celery Beat** roda automaticamente e executa:

### **Tasks Configuradas:**

1. **Gerar Bilhetes Diários**
   - ⏰ **Quando:** 06:00 UTC (09:00 Maputo) - TODOS OS DIAS
   - 🎯 **O que faz:** Analisa todas partidas e gera bilhetes
   - 📍 **Configurado em:** `backend/config/celery.py` linha 28

2. **Validar Resultados**
   - ⏰ **Quando:** A cada 1 hora
   - 🎯 **O que faz:** Atualiza status de apostas finalizadas
   - 📍 **Configurado em:** `backend/config/celery.py` linha 38

3. **Limpar Dados Antigos**
   - ⏰ **Quando:** Domingo 03:00 UTC (semanal)
   - 🎯 **O que faz:** Remove apostas antigas (>90 dias)
   - 📍 **Configurado em:** `backend/config/celery.py` linha 48

### **Como Funciona:**

```
06:00 UTC → Celery Beat dispara "generate_daily_bets"
         → Celery Worker recebe a task
         → Analisa todas partidas do dia
         → Gera bilhetes múltiplos (3x, 5x, 7x)
         → Gera value bets (top 10)
         → Salva no PostgreSQL
         → Usuários veem em /daily-bets
```

---

## 🔍 **Monitoramento**

### **Ver Bilhetes Gerados:**

```bash
# Via API
curl https://seudominio.com/api/daily-bets/today/

# Via Admin
https://seudominio.com/admin/analysis/dailybet/

# Via Shell
docker-compose exec web python manage.py shell
>>> from apps.analysis.models import DailyBet
>>> DailyBet.objects.filter(date='2026-02-07').count()
```

### **Ver Logs do Celery:**

```bash
# Logs em tempo real
docker-compose -f docker-compose.production.yml logs -f celery_beat
docker-compose -f docker-compose.production.yml logs -f celery_worker

# Últimas 100 linhas
docker-compose -f docker-compose.production.yml logs --tail=100 celery_beat
```

### **Verificar Status:**

```bash
# Status de todos containers
docker-compose -f docker-compose.production.yml ps

# Saúde do Redis
docker-compose -f docker-compose.production.yml exec redis redis-cli ping
# Resposta: PONG

# Processos do Celery
docker-compose -f docker-compose.production.yml exec celery_worker celery -A config inspect active
```

---

## 🛠️ **Comandos Úteis**

### **Executar Tarefa Manualmente:**

```bash
# Gerar bilhetes AGORA
docker-compose -f docker-compose.production.yml exec web python manage.py generate_daily_bets

# Validar resultados AGORA
docker-compose -f docker-compose.production.yml exec web python manage.py validate_daily_bets
```

### **Reiniciar Serviços:**

```bash
# Reiniciar apenas Celery
docker-compose -f docker-compose.production.yml restart celery_worker celery_beat

# Reiniciar tudo
docker-compose -f docker-compose.production.yml restart
```

### **Atualizar Código:**

```bash
# Pull do Git
cd /var/www/bet-insight
git pull

# Rebuild e restart
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Migrations (se necessário)
docker-compose -f docker-compose.production.yml exec web python manage.py migrate
```

---

## 🆘 **Troubleshooting**

### **"Nenhum bilhete sendo gerado"**

```bash
# 1. Verificar se Celery Beat está rodando
docker-compose logs celery_beat | grep "generate-daily-bets"

# 2. Verificar Redis
docker-compose exec redis redis-cli ping

# 3. Ver tasks agendadas
docker-compose exec web python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> for t in PeriodicTask.objects.all():
...     print(f"{t.name}: enabled={t.enabled}")

# 4. Executar manualmente para testar
docker-compose exec web python manage.py generate_daily_bets
```

### **"Celery não processa tasks"**

```bash
# Verificar se worker está ativo
docker-compose exec celery_worker celery -A config inspect active

# Ver fila de tasks
docker-compose exec celery_worker celery -A config inspect reserved

# Restart completo do Celery
docker-compose restart celery_worker celery_beat
```

### **"Erro de conexão com Redis"**

```bash
# Verificar se Redis está rodando
docker-compose ps redis

# Testar conexão
docker-compose exec web python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')  # Deve retornar 'value'
```

---

## 📊 **Comparação Final**

### **Desenvolvimento (Windows):**
```
Você → Duplo clique GERAR_BILHETES.bat
    → Python executa
    → Bilhetes gerados
    → Você precisa fazer isso MANUALMENTE todo dia
```

### **Produção (Docker):**
```
06:00 UTC → Celery Beat agenda task
         → Redis recebe mensagem
         → Celery Worker processa
         → Bilhetes gerados AUTOMATICAMENTE
         → Você não precisa fazer NADA! 🎉
```

---

## ✅ **Checklist de Produção**

- [ ] Docker e Docker Compose instalados
- [ ] Projeto clonado/uploadado no servidor
- [ ] `.env` configurado com chaves corretas
- [ ] `docker-compose up -d` executado
- [ ] Migrations aplicadas
- [ ] Superuser criado
- [ ] Celery Beat rodando (logs confirmam)
- [ ] Celery Worker rodando (logs confirmam)
- [ ] Redis funcionando (ping = PONG)
- [ ] Teste manual de geração funcionou
- [ ] Domínio configurado (DNS)
- [ ] SSL/HTTPS configurado (Certbot)
- [ ] Backups configurados

---

## 🎯 **Resumo**

**Desenvolvimento (Agora):**
- Scripts `.bat` para rodar manualmente
- Bom para testar e desenvolver

**Produção (Recomendado):**
- Docker Compose com Celery automático
- **Tudo roda sozinho 24/7**
- Escalável e confiável
- Deploy em ~15 minutos

📖 **Guia completo:** [DEPLOY_PRODUCAO.md](DEPLOY_PRODUCAO.md)

🎉 **Pronto para produção!**
