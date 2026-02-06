# 🚀 Solução Implementada - Bilhetes Automáticos

## ✅ Alterações Realizadas

### 1. **requirements.txt**
Adicionado `django-celery-beat==2.5.0` para scheduler persistente no banco de dados.

### 2. **config/settings.py**
Adicionado `django_celery_beat` ao `INSTALLED_APPS`.

### 3. **docker-compose.yml**
Adicionados 2 novos serviços:

```yaml
celery_worker:
  - Processa tasks em background
  - Comando: celery -A config worker --loglevel=info --pool=solo
  - Conectado ao Redis e PostgreSQL
  - Depende de: db, redis, backend

celery_beat:
  - Scheduler de tasks periódicas
  - Comando: celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
  - Usa DatabaseScheduler (persistente)
  - Depende de: db, redis, backend, celery_worker
```

### 4. **test_celery_setup.py**
Script de teste criado para validar configuração local.

---

## 📝 Próximos Passos (Deploy em Produção)

### Passo 1: Aplicar Migration do django-celery-beat

```bash
# Em produção, via Docker
docker-compose exec backend python manage.py migrate django_celery_beat

# Ou rebuild completo
docker-compose down
docker-compose build
docker-compose up -d
```

### Passo 2: Verificar Containers

```bash
docker-compose ps

# Deve mostrar 7 containers rodando:
# - placarcerto_db
# - placarcerto_redis
# - placarcerto_backend
# - placarcerto_celery_worker  ← NOVO
# - placarcerto_celery_beat    ← NOVO
# - placarcerto_frontend
# - placarcerto_nginx
```

### Passo 3: Verificar Logs

```bash
# Worker
docker logs -f placarcerto_celery_worker

# Deve mostrar:
# ✅ celery@worker ready
# ✅ Connected to redis://redis:6379/0

# Beat
docker logs -f placarcerto_celery_beat

# Deve mostrar:
# ✅ beat: Starting...
# ✅ Scheduler: DatabaseScheduler
# ✅ Schedule: <generate-daily-bets: crontab(hour=6, minute=0)>
```

### Passo 4: Testar API

```bash
# Após primeira execução às 06:00 UTC
curl https://seu-dominio.com/api/daily-bets/today/

# Deve retornar:
{
  "date": "2026-02-06",
  "multiple_tickets": [...],
  "value_bets": [...],
  "stats": {...}
}
```

---

## 🧪 Teste Local (Desenvolvimento)

### Terminal 1: Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### Terminal 2: Django
```bash
cd backend
python manage.py runserver
```

### Terminal 3: Celery Worker
```bash
cd backend
pip install django-celery-beat  # Se ainda não instalou
python manage.py migrate django_celery_beat
celery -A config worker --loglevel=info --pool=solo
```

### Terminal 4: Celery Beat (Opcional)
```bash
cd backend
celery -A config beat --loglevel=info
```

### Terminal 5: Teste
```bash
cd backend
python test_celery_setup.py
```

**Saída esperada:**
```
🎯 RESULTADO FINAL: 5/5 testes passaram
✅ Sistema configurado corretamente!
```

---

## 📊 Como Funciona Agora

### Fluxo Automático (Produção)

```
06:00 UTC (09:00 Maputo)
    ↓
Celery Beat dispara task 'generate_daily_bets'
    ↓
Redis recebe job
    ↓
Celery Worker processa
    ↓
DailyBetGenerator.generate_for_today()
    ↓
Analisa TODAS partidas do dia
    ↓
Gera automaticamente:
  • 3 bilhetes múltiplos (3x, 5x, 7x)
  • Top 10 value bets
    ↓
Salva no banco (DailyBet model)
    ↓
API /api/daily-bets/today/ retorna bilhetes
    ↓
Frontend exibe para usuários
```

### Validação de Resultados

```
A cada 1 hora
    ↓
Celery Beat dispara 'validate_daily_bets'
    ↓
Busca apostas pendentes dos últimos 7 dias
    ↓
Verifica se jogos finalizaram
    ↓
Atualiza status: pending → won/lost/partial
    ↓
Calcula ROI e estatísticas
```

---

## 🎯 Checklist Final

### Desenvolvimento (Local) ✅
- [x] Redis instalado/rodando
- [x] django-celery-beat instalado
- [x] Migration aplicada
- [x] Worker rodando
- [x] Beat rodando (opcional)
- [x] test_celery_setup.py passou

### Produção (Docker) ⏳
- [ ] docker-compose.yml atualizado com celery_worker e celery_beat
- [ ] Rebuild containers: `docker-compose build`
- [ ] Up containers: `docker-compose up -d`
- [ ] Migration aplicada: `docker-compose exec backend python manage.py migrate django_celery_beat`
- [ ] Verificar logs do worker e beat
- [ ] Aguardar execução às 06:00 UTC
- [ ] Testar API `/api/daily-bets/today/`

---

## 🔧 Troubleshooting

### Problema: Worker não conecta ao Redis
```bash
# Verificar se Redis está UP
docker-compose ps redis

# Verificar logs do Redis
docker logs placarcerto_redis

# Verificar variável de ambiente
docker-compose exec backend env | grep REDIS_URL
# Deve mostrar: REDIS_URL=redis://redis:6379/0
```

### Problema: Nenhum bilhete gerado
```bash
# Verificar se há partidas do dia
docker-compose exec backend python manage.py shell
>>> from apps.matches.models import Match
>>> from django.utils import timezone
>>> Match.objects.filter(match_date__gte=timezone.now()).count()

# Se 0, nenhum bilhete será gerado (normal)
```

### Problema: Task não aparece no schedule
```bash
# Verificar migration aplicada
docker-compose exec backend python manage.py showmigrations django_celery_beat

# Deve mostrar [X] em todas as migrations

# Verificar logs do beat
docker logs placarcerto_celery_beat | grep generate_daily_bets
```

---

## 📚 Referências

- [PROBLEMA_BILHETES_AUTOMATICOS.md](../PROBLEMA_BILHETES_AUTOMATICOS.md) - Diagnóstico detalhado
- [GUIA_BILHETES_AUTOMATICOS.md](../GUIA_BILHETES_AUTOMATICOS.md) - Documentação completa do sistema
- [Celery Documentation](https://docs.celeryq.dev/) - Documentação oficial
- [django-celery-beat](https://django-celery-beat.readthedocs.io/) - Scheduler persistente
