# 🧪 TESTES DE API - BET INSIGHT MOZAMBIQUE

## 📋 Pré-requisitos
- Servidor Django rodando: `python manage.py runserver`
- Usuário de teste criado
- Banco populado com partidas

---

## 1️⃣ AUTENTICAÇÃO

### Registro de Usuário
```bash
curl -X POST http://localhost:8000/api/users/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "novo@betinsight.co.mz",
    "username": "novousuario",
    "password": "Test@123",
    "password2": "Test@123",
    "phone": "+258 84 123 4567"
  }'
```

### Login (Obter Token)
```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@123"
  }'
```

**Resposta esperada:**
```json
{
  "refresh": "eyJ...",
  "access": "eyJ..."
}
```

**💡 Copie o token "access" e use nas próximas requisições!**

---

## 2️⃣ PERFIL DO USUÁRIO

### Ver Perfil
```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Estatísticas do Usuário
```bash
curl -X GET http://localhost:8000/api/users/stats/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Atualizar Perfil
```bash
curl -X PATCH http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+258 85 999 8888",
    "push_enabled": true
  }'
```

---

## 3️⃣ LIGAS

### Listar Todas as Ligas
```bash
curl -X GET http://localhost:8000/api/leagues/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Buscar Liga por Nome
```bash
curl -X GET "http://localhost:8000/api/leagues/?search=Premier" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 4️⃣ TIMES

### Listar Todos os Times
```bash
curl -X GET http://localhost:8000/api/teams/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Buscar Time
```bash
curl -X GET "http://localhost:8000/api/teams/?search=Manchester" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 5️⃣ PARTIDAS

### Listar Todas as Partidas
```bash
curl -X GET http://localhost:8000/api/matches/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Partidas de Hoje
```bash
curl -X GET http://localhost:8000/api/matches/today/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Partidas Futuras (Próximos 7 dias)
```bash
curl -X GET http://localhost:8000/api/matches/upcoming/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Partidas ao Vivo
```bash
curl -X GET http://localhost:8000/api/matches/live/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Filtrar por Liga
```bash
curl -X GET "http://localhost:8000/api/matches/?league=1" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Detalhes de uma Partida
```bash
curl -X GET http://localhost:8000/api/matches/1/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 6️⃣ ANÁLISES (Principal Feature!)

### Solicitar Análise de uma Partida
```bash
curl -X POST http://localhost:8000/api/analyses/request_analysis/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": 1
  }'
```

**Resposta esperada:**
```json
{
  "message": "Análise gerada com sucesso!",
  "analysis": {
    "id": 1,
    "match": {...},
    "prediction": "home",
    "prediction_display": "Vitória Casa",
    "confidence": 4,
    "confidence_display": "⭐⭐⭐⭐",
    "home_probability": 48.5,
    "draw_probability": 25.2,
    "away_probability": 26.3,
    "home_xg": 2.1,
    "away_xg": 1.4,
    "reasoning": "Análise detalhada...",
    "key_factors": [
      "Forma recente favorece Manchester City",
      "Histórico direto equilibrado",
      "Fator casa pode ser decisivo"
    ]
  }
}
```

### Minhas Análises
```bash
curl -X GET http://localhost:8000/api/analyses/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Minhas Estatísticas de Análises
```bash
curl -X GET http://localhost:8000/api/analyses/my_stats/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Filtrar Análises por Confiança
```bash
curl -X GET "http://localhost:8000/api/analyses/?confidence=4" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Filtrar Análises por Predição
```bash
curl -X GET "http://localhost:8000/api/analyses/?prediction=home" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 7️⃣ ASSINATURAS

### Ver Assinatura Atual
```bash
curl -X GET http://localhost:8000/api/subscriptions/current/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Listar Minhas Assinaturas
```bash
curl -X GET http://localhost:8000/api/subscriptions/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Cancelar Assinatura
```bash
curl -X POST http://localhost:8000/api/subscriptions/1/cancel/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 8️⃣ PAGAMENTOS

### Criar Pagamento (M-Pesa)
```bash
curl -X POST http://localhost:8000/api/payments/create_payment/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "monthly",
    "phone_number": "+258 84 123 4567"
  }'
```

**Planos disponíveis:**
- `monthly` - 499 MZN/mês
- `quarterly` - 1299 MZN/3 meses
- `yearly` - 4499 MZN/ano

### Listar Meus Pagamentos
```bash
curl -X GET http://localhost:8000/api/payments/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🧪 TESTE COMPLETO - FLUXO DE USUÁRIO

### 1. Criar conta e fazer login
```bash
# Registro
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/users/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "fluxo@test.com",
    "username": "fluxotest",
    "password": "Test@123",
    "password2": "Test@123"
  }')

echo "Registro: $REGISTER_RESPONSE"

# Extrair token (no Windows PowerShell)
# $token = ($REGISTER_RESPONSE | ConvertFrom-Json).tokens.access

# Login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@123"
  }')

echo "Login: $LOGIN_RESPONSE"
```

### 2. Ver partidas disponíveis
```bash
curl -X GET http://localhost:8000/api/matches/upcoming/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Solicitar análise
```bash
curl -X POST http://localhost:8000/api/analyses/request_analysis/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"match_id": 1}'
```

### 4. Ver minhas análises
```bash
curl -X GET http://localhost:8000/api/analyses/ \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Ver estatísticas
```bash
curl -X GET http://localhost:8000/api/users/stats/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## ✅ VALIDAÇÕES

### Limite de Análises (Free User)
- Usuários free: 5 análises/dia
- Ao atingir limite, retorna erro 403

```bash
# Fazer 6 requisições de análise para testar limite
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/analyses/request_analysis/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"match_id\": $i}"
  echo "\n---"
done
```

### Análise Duplicada
- Não permite analisar mesma partida 2x
- Retorna análise existente

---

## 🔧 TROUBLESHOOTING

### Erro 401 Unauthorized
- Token expirado ou inválido
- Fazer login novamente

### Erro 403 Forbidden
- Limite de análises atingido
- Verificar: `GET /api/users/stats/`

### Erro 404 Not Found
- Match ID inválido
- Verificar: `GET /api/matches/`

### Erro 400 Bad Request
- Dados inválidos
- Verificar formato JSON e campos obrigatórios

---

## 📊 COMANDOS ÚTEIS

### Resetar contador de análises diárias
```python
python manage.py shell
>>> from apps.users.models import User
>>> User.objects.all().update(daily_analysis_count=0)
```

### Criar usuário premium manualmente
```python
python manage.py shell
>>> from apps.users.models import User
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> user = User.objects.get(email='test@betinsight.co.mz')
>>> user.is_premium = True
>>> user.premium_until = timezone.now() + timedelta(days=30)
>>> user.save()
```

### Limpar todas as análises
```python
python manage.py shell
>>> from apps.analysis.models import Analysis
>>> Analysis.objects.all().delete()
```

---

## 🎯 PRÓXIMOS PASSOS

- ✅ Backend REST API funcional
- ✅ Autenticação JWT
- ✅ CRUD completo de entidades
- ✅ Sistema de análise com IA (simulada)
- ⏳ Frontend React PWA
- ⏳ Integração real com Google Gemini
- ⏳ Integração real com M-Pesa
- ⏳ Deploy em produção
