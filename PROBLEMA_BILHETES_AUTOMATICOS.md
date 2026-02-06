# 🚨 PROBLEMA: Bilhetes Automáticos Não Funcionam em Produção

## 📋 RESUMO DO PROBLEMA

**Status**: ❌ Sistema implementado mas NÃO EXECUTANDO em produção  
**Causa Raiz**: Falta configuração de Celery Worker e Celery Beat no Docker

---

## 🔍 ENTENDENDO O SISTEMA DE BILHETES AUTOMÁTICOS

### Como Foi Projetado

O sistema foi implementado seguindo este fluxo:

```
1. CELERY BEAT (scheduler)
   ↓ Executa às 06:00 UTC diariamente
   
2. CELERY WORKER (processador)
   ↓ Recebe task via Redis
   
3. Task: generate_daily_bets()
   ↓ Executa DailyBetGenerator
   
4. DailyBetGenerator
   ↓ Analisa TODAS partidas do dia
   ↓ Usa HybridAnalysisOrchestrator
   
5. Gera Automaticamente:
   ✅ 3 Bilhetes Múltiplos (3x, 5x, 7x)
   ✅ Top 10 Value Bets
   ✅ Salva no banco (DailyBet model)
   
6. API Pública serve os bilhetes:
   GET /api/daily-bets/today/
   GET /api/daily-bets/history/
```

### Componentes Implementados ✅

#### 1. **Modelo DailyBet** (`models.py`)
```python
class DailyBet(models.Model):
    date = models.DateField()  # Data do bilhete
    bet_type = models.CharField()  # 'multiple' ou 'value'
    selections = models.JSONField()  # Lista de apostas
    total_odd = models.DecimalField()
    combined_probability = models.FloatField()
    expected_value = models.FloatField()
    suggested_stake = models.FloatField()
    status = models.CharField()  # pending/won/lost/partial
    result = models.CharField()  # Resultado após validação
    is_validated = models.BooleanField(default=False)
```

#### 2. **Service DailyBetGenerator** (`daily_bet_generator.py`)
```python
class DailyBetGenerator:
    def generate_for_today(self):
        """Analisa partidas e gera bilhetes"""
        
        # 1. Busca partidas do dia
        matches = Match.objects.filter(
            match_date__gte=timezone.now(),
            match_date__lt=timezone.now() + timedelta(days=1),
            status__in=['not_started', 'scheduled']
        )
        
        # 2. Analisa cada partida com 2 estratégias
        for match in matches:
            result_value = orchestrator.run(match, strategy='value')
            result_multiple = orchestrator.run(match, strategy='multiple')
        
        # 3. Gera bilhetes múltiplos (3x, 5x, 7x)
        self._generate_multiple_tickets(analyses)
        
        # 4. Gera value bets (top 10)
        self._generate_value_bets(analyses)
```

**Filtros para Bilhetes Múltiplos:**
- Probabilidade individual: ≥ 50%
- Probabilidade combinada 3x: ≥ 15%
- Probabilidade combinada 5x: ≥ 8%
- Probabilidade combinada 7x: ≥ 4%
- Odd total: 2.0 - 20.0

**Filtros para Value Bets:**
- EV (Expected Value): ≥ +5%
- Probabilidade: ≥ 25%
- Limitar a 10 apostas por dia

#### 3. **Celery Tasks** (`tasks.py`)
```python
@shared_task(bind=True, name='analysis.generate_daily_bets')
def generate_daily_bets(self):
    """Task principal - gera bilhetes diários"""
    generator = DailyBetGenerator()
    results = generator.generate_for_today()
    return results

@shared_task(bind=True, name='analysis.validate_daily_bets')
def validate_daily_bets(self):
    """Valida resultados de apostas após jogos finalizarem"""
    # Atualiza status: pending → won/lost/partial
```

#### 4. **Celery Config** (`config/celery.py`)
```python
app.conf.beat_schedule = {
    # Gerar bilhetes diários - 06:00 UTC
    'generate-daily-bets': {
        'task': 'analysis.generate_daily_bets',
        'schedule': crontab(hour=6, minute=0),
    },
    
    # Validar apostas - A cada 1 hora
    'validate-daily-bets': {
        'task': 'analysis.validate_daily_bets',
        'schedule': crontab(minute=0),
    },
}
```

#### 5. **API Endpoints** (`views.py`)
```python
class DailyBetViewSet(viewsets.ReadOnlyModelViewSet):
    @action(detail=False, methods=['get'])
    def today(self, request):
        """GET /api/daily-bets/today/"""
        # Retorna bilhetes e value bets de hoje
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """GET /api/daily-bets/history/?days=30"""
        # Retorna histórico com estatísticas
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """GET /api/daily-bets/stats/"""
        # ROI, win rate, etc.
```

---

## ❌ PORQUE NÃO FUNCIONA EM PRODUÇÃO

### Arquitetura Atual em Produção (docker-compose.yml)

```yaml
services:
  db:           # ✅ PostgreSQL
  redis:        # ✅ Redis
  backend:      # ✅ Django + Gunicorn
  frontend:     # ✅ React + Vite
  nginx:        # ✅ Reverse Proxy
```

**O QUE FALTA:**
```yaml
  celery_worker:   # ❌ NÃO EXISTE
  celery_beat:     # ❌ NÃO EXISTE
```

### Diagnóstico Completo

#### 1. ❌ Celery Worker NÃO está rodando

**O que é**: Processo que executa as tasks assíncronas

**Verificação**:
```bash
# Comando esperado em produção:
celery -A config worker --loglevel=info

# Status atual: NÃO RODANDO
```

**Consequência**:
- Task `generate_daily_bets` NUNCA é executada
- Task `validate_daily_bets` NUNCA é executada
- Redis recebe os jobs mas ninguém processa

#### 2. ❌ Celery Beat NÃO está rodando

**O que é**: Scheduler que dispara tasks no horário agendado

**Verificação**:
```bash
# Comando esperado em produção:
celery -A config beat --loglevel=info

# Status atual: NÃO RODANDO
```

**Consequência**:
- Tasks NÃO são agendadas automaticamente
- Mesmo às 06:00 UTC, nada acontece
- Sistema de geração diária INATIVO

#### 3. ✅ Redis está OK (mas sem uso)

**Verificação docker-compose.yml**:
```yaml
redis:
  image: redis:7-alpine
  restart: unless-stopped
  # ✅ CONFIGURADO CORRETAMENTE
```

**Django settings.py**:
```python
CELERY_BROKER_URL = 'redis://redis:6379/0'  # ✅ OK
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'  # ✅ OK
```

**Status**: Redis está rodando mas sem workers conectados

#### 4. ✅ Código está completo

**Arquivos implementados**:
- ✅ `apps/analysis/models.py` - Modelo DailyBet
- ✅ `apps/analysis/services/daily_bet_generator.py` - Lógica de geração
- ✅ `apps/analysis/tasks.py` - Celery tasks
- ✅ `apps/analysis/views.py` - API endpoints
- ✅ `apps/analysis/serializers.py` - Serializers
- ✅ `config/celery.py` - Configuração Celery
- ✅ Migration aplicada (0003_add_daily_bet_model)

**Status**: Todo código necessário existe e está correto

---

## 🔧 SOLUÇÃO: Adicionar Celery Worker e Beat ao Docker

### Opção 1: Adicionar ao docker-compose.yml (RECOMENDADO)

```yaml
services:
  # ... serviços existentes ...

  # Celery Worker - Processa tasks em background
  celery_worker:
    build:
      context: .
      dockerfile: ./backend/Dockerfile
    container_name: placarcerto_celery_worker
    restart: unless-stopped
    command: celery -A config worker --loglevel=info --pool=solo
    env_file:
      - ./backend/.env.production
    environment:
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    networks:
      - app_network
    depends_on:
      - db
      - redis
      - backend

  # Celery Beat - Scheduler de tasks periódicas
  celery_beat:
    build:
      context: .
      dockerfile: ./backend/Dockerfile
    container_name: placarcerto_celery_beat
    restart: unless-stopped
    command: celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file:
      - ./backend/.env.production
    environment:
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    networks:
      - app_network
    depends_on:
      - db
      - redis
      - backend
      - celery_worker
```

### Opção 2: Serviço Combinado (Worker + Beat)

```yaml
  # Celery Worker + Beat Combinado
  celery:
    build:
      context: .
      dockerfile: ./backend/Dockerfile
    container_name: placarcerto_celery
    restart: unless-stopped
    command: >
      sh -c "
        celery -A config worker --loglevel=info --pool=solo &
        celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
      "
    env_file:
      - ./backend/.env.production
    environment:
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    networks:
      - app_network
    depends_on:
      - db
      - redis
      - backend
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Passo 1: Instalar django-celery-beat (se usar DatabaseScheduler)

**requirements.txt**:
```txt
celery==5.3.4
redis==5.0.1
django-celery-beat==2.5.0  # ← ADICIONAR
```

### Passo 2: Adicionar ao INSTALLED_APPS

**config/settings.py**:
```python
INSTALLED_APPS = [
    # ...
    'django_celery_beat',  # ← ADICIONAR
]
```

### Passo 3: Aplicar migration do django-celery-beat

```bash
python manage.py migrate django_celery_beat
```

### Passo 4: Atualizar docker-compose.yml

Adicionar serviços `celery_worker` e `celery_beat` como mostrado acima.

### Passo 5: Rebuild e restart

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### Passo 6: Verificar logs

```bash
# Verificar worker
docker logs -f placarcerto_celery_worker

# Verificar beat
docker logs -f placarcerto_celery_beat

# Deve mostrar:
# ✅ "celery@worker ready"
# ✅ "beat: Starting..."
# ✅ "Scheduler: Sending due task analysis.generate_daily_bets"
```

---

## 🧪 TESTAR EM DESENVOLVIMENTO (Local)

### Terminal 1: Redis
```bash
# Windows: baixar Redis para Windows ou usar Docker
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
celery -A config worker --loglevel=info --pool=solo
```

### Terminal 4: Celery Beat
```bash
cd backend
celery -A config beat --loglevel=info
```

### Terminal 5: Testar geração manual
```bash
cd backend
python manage.py shell

>>> from apps.analysis.tasks import generate_daily_bets
>>> generate_daily_bets()
# Deve gerar bilhetes se houver partidas do dia
```

---

## 📊 VERIFICAR SE ESTÁ FUNCIONANDO

### 1. Logs do Celery Beat
```bash
docker logs placarcerto_celery_beat | grep generate_daily_bets

# Deve mostrar (diariamente às 06:00 UTC):
# Scheduler: Sending due task analysis.generate_daily_bets
```

### 2. Logs do Celery Worker
```bash
docker logs placarcerto_celery_worker | grep generate_daily_bets

# Deve mostrar:
# Received task: analysis.generate_daily_bets
# Task analysis.generate_daily_bets succeeded
```

### 3. API Response
```bash
curl http://localhost/api/daily-bets/today/

# Deve retornar:
{
  "date": "2026-02-06",
  "multiple_tickets": [...],  # ← Se houver bilhetes
  "value_bets": [...],         # ← Se houver value bets
  "stats": {...}
}
```

### 4. Admin Django
```
http://localhost/admin/analysis/dailybet/

# Deve listar:
# - Bilhetes múltiplos criados automaticamente
# - Value bets criadas automaticamente
# - Status: pending/won/lost
```

---

## 🎯 RESUMO EXECUTIVO

### O Problema
1. Sistema de Bilhetes Automáticos **COMPLETO NO CÓDIGO** ✅
2. Celery Worker **NÃO RODANDO EM PRODUÇÃO** ❌
3. Celery Beat **NÃO RODANDO EM PRODUÇÃO** ❌
4. Resultado: **NENHUM BILHETE GERADO AUTOMATICAMENTE** ❌

### A Solução
1. Adicionar `celery_worker` service ao docker-compose.yml
2. Adicionar `celery_beat` service ao docker-compose.yml
3. Instalar `django-celery-beat` (se usar DatabaseScheduler)
4. Rebuild containers
5. Verificar logs

### Impacto Esperado
- ✅ Bilhetes gerados automaticamente às 06:00 UTC (09:00 Maputo)
- ✅ Validação de resultados a cada 1 hora
- ✅ API `/api/daily-bets/today/` retorna bilhetes do dia
- ✅ Usuários veem bilhetes prontos para apostar

---

## 📚 REFERÊNCIAS

- [GUIA_BILHETES_AUTOMATICOS.md](GUIA_BILHETES_AUTOMATICOS.md) - Documentação completa do sistema
- [apps/analysis/services/daily_bet_generator.py](backend/apps/analysis/services/daily_bet_generator.py) - Lógica de geração
- [apps/analysis/tasks.py](backend/apps/analysis/tasks.py) - Celery tasks
- [config/celery.py](backend/config/celery.py) - Configuração Celery
- [Celery Documentation](https://docs.celeryq.dev/) - Documentação oficial
