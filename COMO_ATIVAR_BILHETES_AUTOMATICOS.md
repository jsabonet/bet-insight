# 🚀 Como Ativar o Sistema de Bilhetes Automáticos

## ⚠️ Problema Identificado

O sistema de Bilhetes Automáticos **NÃO estava rodando** porque:
- ❌ Celery Worker não estava iniciado
- ❌ Celery Beat não estava iniciado  
- ❌ Redis não está instalado no Windows (necessário para Celery)

## ✅ Solução Implementada (PRONTA!)

Criei **comandos Django** e **scripts .bat** prontos para usar! Basta clicar duplo e o sistema funciona.

### 📁 Arquivos Criados:
- ✅ `GERAR_BILHETES.bat` - Duplo clique para gerar bilhetes (uso diário)
- ✅ `VALIDAR_RESULTADOS.bat` - Duplo clique para validar resultados
- ✅ `run_daily_bets_scheduled.bat` - Para Task Scheduler (background)
- ✅ `run_validation_scheduled.bat` - Para Task Scheduler (background)

---

## 🎯 Uso Rápido (MAIS FÁCIL!)

### 1️⃣ Gerar Bilhetes de Hoje (Faça todos os dias pela manhã)

**Duplo clique em:**
```
D:\Projectos\Football\bet-insight\backend\GERAR_BILHETES.bat
```

O sistema vai:
- ✅ Analisar todas as partidas de hoje
- ✅ Gerar bilhetes múltiplos (3x, 5x, 7x)
- ✅ Gerar value bets (top 10)
- ✅ Salvar tudo no banco de dados

**Quando fazer:** Todos os dias entre **06:00 - 09:00** (antes dos jogos começarem)

### 2️⃣ Validar Resultados (Faça várias vezes ao dia)

**Duplo clique em:**
```
D:\Projectos\Football\bet-insight\backend\VALIDAR_RESULTADOS.bat
```

O sistema vai:
- ✅ Verificar apostas pendentes
- ✅ Atualizar resultados (ganhou/perdeu)
- ✅ Calcular ROI e estatísticas

**Quando fazer:** 
- 15:00 (após jogos da tarde)
- 18:00 (após mais jogos)
- 21:00 (após jogos da noite)
- 00:00 (validação final do dia)

### 3️⃣ Ver Resultados

**Frontend:**
```
http://localhost:3000/daily-bets
```

**Admin:**
```
http://localhost:8000/admin/analysis/dailybet/
```

**API:**
```bash
# PowerShell
Invoke-WebRequest http://localhost:8000/api/daily-bets/today/ | Select-Object -ExpandProperty Content
```

---

## ⚙️ Opção Avançada: Agendamento Automático

Quer que rode automaticamente sem você precisar clicar? Configure o **Task Scheduler do Windows**:

### Agendar Geração Diária (09:00)

1. Abra **Agendador de Tarefas** (Task Scheduler)
2. Clique em **"Criar Tarefa Básica"**
3. **Nome:** `PlacerCerto - Gerar Bilhetes Diários`
4. **Disparador:** Diariamente às **09:00**
5. **Ação:** Iniciar um programa
   - **Programa:** `D:\Projectos\Football\bet-insight\backend\run_daily_bets_scheduled.bat`
6. ✅ Concluir

### Agendar Validação (A cada 3 horas)

1. Abra **Agendador de Tarefas**
2. **Nome:** `PlacerCerto - Validar Resultados`
3. **Disparador:** Diariamente
4. **Ação:** `D:\Projectos\Football\bet-insight\backend\run_validation_scheduled.bat`
5. **Editar disparador:**
   - Marque: **"Repetir a cada: 3 horas"**
   - Duração: **Indefinidamente**
6. ✅ Concluir

### Ver Logs das Execuções Agendadas

```bash
# PowerShell
Get-Content D:\Projectos\Football\bet-insight\backend\logs\daily_bets_*.log -Tail 50
Get-Content D:\Projectos\Football\bet-insight\backend\logs\validation_*.log -Tail 50
```

---

## 🎯 Opção 1: Execução Manual (Linha de Comando)

### 1. Gerar Bilhetes de Hoje

```bash
cd D:\Projectos\Football\bet-insight\backend
python manage.py generate_daily_bets
```

**O que faz:**
- Analisa TODAS as partidas de hoje
- Gera bilhetes múltiplos (3x, 5x, 7x)
- Gera value bets (top 10 com maior EV)
- Salva no banco de dados

**Quando executar:**
- Todos os dias pela manhã (recomendado: 06:00 - 09:00)
- Ou quando quiser atualizar os bilhetes

### 2. Validar Resultados

```bash
cd D:\Projectos\Football\bet-insight\backend
python manage.py validate_daily_bets
```

**O que faz:**
- Verifica apostas pendentes dos últimos 7 dias
- Valida resultados automaticamente
- Atualiza status (ganhou/perdeu/parcial)

**Quando executar:**
- Várias vezes ao dia (ex: 15:00, 18:00, 21:00, 00:00)
- Após jogos importantes terminarem

---

## ⚙️ Opção 2: Agendamento Automático (Windows Task Scheduler)

### Passo 1: Criar Script de Geração

Crie o arquivo `D:\Projectos\Football\bet-insight\backend\run_daily_bets.bat`:

```batch
@echo off
cd /d D:\Projectos\Football\bet-insight\backend
call venv\Scripts\activate.bat
python manage.py generate_daily_bets >> logs\daily_bets_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log 2>&1
```

### Passo 2: Criar Script de Validação

Crie o arquivo `D:\Projectos\Football\bet-insight\backend\run_validation.bat`:

```batch
@echo off
cd /d D:\Projectos\Football\bet-insight\backend
call venv\Scripts\activate.bat
python manage.py validate_daily_bets >> logs\validation_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log 2>&1
```

### Passo 3: Criar Pasta de Logs

```bash
mkdir D:\Projectos\Football\bet-insight\backend\logs
```

### Passo 4: Agendar no Task Scheduler

#### A) Gerar Bilhetes Diários (09:00 todos os dias)

1. Abra **Task Scheduler** (Agendador de Tarefas)
2. Clique em **"Create Basic Task"** (Criar Tarefa Básica)
3. Nome: `Gerar Bilhetes PlacerCerto`
4. Trigger: **Daily** (Diariamente) às **09:00**
5. Action: **Start a Program**
   - Program: `D:\Projectos\Football\bet-insight\backend\run_daily_bets.bat`
6. ✅ Finish

#### B) Validar Resultados (A cada 3 horas)

1. Abra **Task Scheduler**
2. Clique em **"Create Basic Task"**
3. Nome: `Validar Bilhetes PlacerCerto`
4. Trigger: **Daily** (Diariamente)
5. Action: **Start a Program**
   - Program: `D:\Projectos\Football\bet-insight\backend\run_validation.bat`
6. Após criar:
   - Clique com botão direito → **Properties**
   - Vá em **Triggers** → **Edit**
   - Marque: **"Repeat task every: 3 hours"**
   - Duration: **Indefinitely**
7. ✅ OK

---

## 🔥 Opção 3: Celery (Produção - Requer Redis)

### Windows (WSL ou Docker)

Se quiser usar Celery no Windows, você precisa de Redis via:

**A) WSL (Windows Subsystem for Linux)**

```bash
# Instalar WSL
wsl --install

# Dentro do WSL
sudo apt update
sudo apt install redis-server
redis-server --daemonize yes
```

**B) Docker**

```bash
docker run -d -p 6379:6379 redis:alpine
```

### Iniciar Celery

**Terminal 1: Worker**
```bash
cd D:\Projectos\Football\bet-insight\backend
celery -A config worker --pool=solo --loglevel=info
```

**Terminal 2: Beat (Scheduler)**
```bash
cd D:\Projectos\Football\bet-insight\backend
celery -A config beat --loglevel=info
```

---

## 📊 Verificar se Está Funcionando

### 1. Ver Bilhetes Gerados

**Via Admin:**
```
http://localhost:8000/admin/analysis/dailybet/
```

**Via API:**
```bash
# Bilhetes de hoje
curl http://localhost:8000/api/daily-bets/today/

# Estatísticas
curl http://localhost:8000/api/daily-bets/stats/
```

**Via Frontend:**
```
http://localhost:3000/daily-bets
```

### 2. Ver Logs

```bash
# Logs do Django (se rodou comando manual)
# Aparecem no terminal

# Logs agendados (Task Scheduler)
dir D:\Projectos\Football\bet-insight\backend\logs
type D:\Projectos\Football\bet-insight\backend\logs\daily_bets_*.log
```

---

## 🎯 Recomendação para Você

### Para Desenvolvimento/Teste: **Opção 1 (Manual)**

Rode agora mesmo para testar:

```bash
cd D:\Projectos\Football\bet-insight\backend
python manage.py generate_daily_bets
```

### Para Uso Diário: **Opção 2 (Task Scheduler)**

- Configure os .bat files
- Agende no Task Scheduler
- Funciona mesmo com PC desligado (se configurar para acordar)

### Para Produção: **Opção 3 (Celery)**

- Use servidor Linux/Cloud
- Redis sempre ativo
- Mais robusto e escalável

---

## 🐛 Troubleshooting

### "Nenhuma partida encontrada"

**Causa:** Não há jogos agendados para hoje no banco de dados

**Solução:** Verifique se há partidas no banco:
```bash
python manage.py shell
>>> from apps.matches.models import Match
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> Match.objects.filter(match_date__gte=timezone.now(), match_date__lt=timezone.now() + timedelta(days=1)).count()
```

### "Nenhum bilhete gerado"

**Causa:** Apostas não atendem critérios mínimos (probabilidade, EV, etc.)

**Solução:** Ajuste os filtros em `DailyBetGenerator`:
```python
# apps/analysis/services/daily_bet_generator.py
MIN_VALUE_EV = 5.0  # Reduza para 3.0
MIN_MULTIPLE_PROBABILITY = 0.50  # Reduza para 0.40
```

### Erro de importação

**Causa:** Virtual environment não ativado

**Solução:**
```bash
cd D:\Projectos\Football\bet-insight\backend
venv\Scripts\activate
python manage.py generate_daily_bets
```

---

## 📝 Resumo Rápido

```bash
# 1. Ativar ambiente virtual
cd D:\Projectos\Football\bet-insight\backend
venv\Scripts\activate

# 2. Gerar bilhetes AGORA
python manage.py generate_daily_bets

# 3. Validar resultados
python manage.py validate_daily_bets

# 4. Ver no admin
# http://localhost:8000/admin/analysis/dailybet/

# 5. Ver no frontend
# http://localhost:3000/daily-bets
```

**🎉 Pronto! O sistema vai gerar bilhetes automaticamente todos os dias!**
