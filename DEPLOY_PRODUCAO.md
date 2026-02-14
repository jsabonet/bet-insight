# 🐳 Deploy com Docker em Produção

## 📋 Pré-requisitos

- Servidor Linux (Ubuntu 20.04+ recomendado)
- Docker e Docker Compose instalados
- Domínio configurado (DNS apontando para o servidor)

---

## 🚀 Deployment Completo

### **Passo 1: Preparar Servidor**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker --version
docker-compose --version
```

### **Passo 2: Clonar Projeto**

```bash
# Criar diretório
sudo mkdir -p /var/www
cd /var/www

# Clonar repositório (ou fazer upload via FTP/SCP)
git clone <seu-repositorio> bet-insight
cd bet-insight
```

### **Passo 3: Configurar Variáveis de Ambiente**

```bash
# Copiar exemplo
cp .env.production.example .env

# Editar com suas configurações
nano .env
```

**Variáveis importantes:**
- `SECRET_KEY` - Gere uma chave secreta única
- `DB_PASSWORD` - Senha segura para o banco
- `ALLOWED_HOSTS` - Seu domínio
- `API_FOOTBALL_KEY` - Sua chave da API
- `GOOGLE_AI_KEY` - Sua chave do Gemini

### **Passo 4: Build e Iniciar**

```bash
# Build das imagens
docker-compose -f docker-compose.production.yml build

# Iniciar todos os serviços
docker-compose -f docker-compose.production.yml up -d

# Ver logs
docker-compose -f docker-compose.production.yml logs -f
```

### **Passo 5: Configurar Banco de Dados**

```bash
# Executar migrations
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# Criar superuser
docker-compose -f docker-compose.production.yml exec web python manage.py createsuperuser

# Coletar static files
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
```

### **Passo 6: Verificar Celery**

```bash
# Ver status do Celery Worker
docker-compose -f docker-compose.production.yml logs celery_worker

# Ver status do Celery Beat
docker-compose -f docker-compose.production.yml logs celery_beat

# Testar geração de bilhetes manualmente
docker-compose -f docker-compose.production.yml exec web python manage.py generate_daily_bets
```

---

## 🔍 Monitoramento

### **Ver Logs**

```bash
# Todos os serviços
docker-compose -f docker-compose.production.yml logs -f

# Apenas Django
docker-compose -f docker-compose.production.yml logs -f web

# Apenas Celery Worker
docker-compose -f docker-compose.production.yml logs -f celery_worker

# Apenas Celery Beat
docker-compose -f docker-compose.production.yml logs -f celery_beat
```

### **Status dos Containers**

```bash
docker-compose -f docker-compose.production.yml ps
```

### **Executar Comandos**

```bash
# Django shell
docker-compose -f docker-compose.production.yml exec web python manage.py shell

# Verificar bilhetes gerados
docker-compose -f docker-compose.production.yml exec web python manage.py shell
>>> from apps.analysis.models import DailyBet
>>> DailyBet.objects.count()
>>> DailyBet.objects.filter(date='2026-02-07')
```

---

## 🔄 Atualizações

```bash
# Baixar últimas alterações
cd /var/www/bet-insight
git pull

# Rebuild e restart
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Executar migrations se necessário
docker-compose -f docker-compose.production.yml exec web python manage.py migrate
```

---

## 🛑 Parar/Reiniciar

```bash
# Parar todos os serviços
docker-compose -f docker-compose.production.yml stop

# Reiniciar
docker-compose -f docker-compose.production.yml restart

# Parar e remover containers
docker-compose -f docker-compose.production.yml down

# Parar e remover TUDO (incluindo volumes)
docker-compose -f docker-compose.production.yml down -v
```

---

## 📊 Verificar Funcionamento

1. **API Django:** http://seudominio.com/api/daily-bets/today/
2. **Admin:** http://seudominio.com/admin/
3. **Health Check:** http://seudominio.com/health/

---

## 🔐 SSL/HTTPS (Certbot + Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado
sudo certbot --nginx -d seudominio.com -d www.seudominio.com

# Renovação automática já está configurada
sudo certbot renew --dry-run
```

---

## 🎯 Resumo dos Serviços

| Serviço | Descrição | Porta | Status |
|---------|-----------|-------|--------|
| `web` | Django API | 8000 | Sempre ativo |
| `celery_worker` | Processa tasks | - | Sempre ativo |
| `celery_beat` | Agenda tasks | - | Sempre ativo |
| `redis` | Message broker | 6379 | Sempre ativo |
| `db` | PostgreSQL | 5432 | Sempre ativo |
| `nginx` | Reverse proxy | 80/443 | Sempre ativo |

---

## ✅ Checklist de Produção

- [ ] Variáveis de ambiente configuradas
- [ ] SECRET_KEY única gerada
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] Banco de dados criado
- [ ] Migrations executadas
- [ ] Superuser criado
- [ ] Static files coletados
- [ ] Celery Worker rodando
- [ ] Celery Beat rodando
- [ ] Redis funcionando
- [ ] Nginx configurado
- [ ] SSL/HTTPS ativo
- [ ] Backups configurados

---

## 🆘 Troubleshooting

### Celery não está executando tasks

```bash
# Verificar se Redis está respondendo
docker-compose exec redis redis-cli ping

# Verificar logs do Celery
docker-compose logs celery_worker
docker-compose logs celery_beat

# Restart Celery
docker-compose restart celery_worker celery_beat
```

### Bilhetes não estão sendo gerados

```bash
# Verificar schedule do Celery Beat
docker-compose exec web python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.all()

# Executar manualmente
docker-compose exec web python manage.py generate_daily_bets
```

### Erro de permissões

```bash
# Ajustar permissões
sudo chown -R 1000:1000 /var/www/bet-insight
```

🎉 **Pronto! Seu sistema está rodando em produção com Celery automático!**
