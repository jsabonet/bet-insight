# 🏆 GUIA DE RETREINO DO MODELO ML - LIGAS + COPAS

## 📋 Objetivo
Retreinar o modelo ML XGBoost com ~1680 partidas (880 ligas + 800 copas) para melhorar predições em competições de eliminatórias.

---

## 🚀 PASSO A PASSO

### **1️⃣ Coletar Dados de Copas (800 partidas)**

```bash
cd D:\Projectos\Football\bet-insight\backend
python collect_cup_data.py
```

**Tempo estimado:** 6-8 minutos (0.5s por request × 800 = 400s + overhead)

**Output esperado:**
```
✅ COLETA FINALIZADA
📊 Total coletado: 800 partidas de copas
💾 Dataset salvo em: ml_training/cup_training_dataset.json
```

**Competições coletadas:**
- FA Cup, League Cup (Inglaterra)
- Copa del Rey, Supercopa (Espanha)
- DFB-Pokal (Alemanha)
- Coppa Italia (Itália)
- Coupe de France (França)
- KNVB Beker (Holanda)
- Croky Cup (Bélgica)
- Taça de Portugal (Portugal)
- Champions League (fases eliminatórias)
- Europa League, Conference League

---

### **2️⃣ Retreinar Modelo com Dados Combinados**

```bash
python retrain_with_cups.py
```

**Tempo estimado:** 2-3 minutos

**Output esperado:**
```
✅ 880 partidas de LIGAS carregadas
✅ 800 partidas de COPAS carregadas

📊 DATASET COMBINADO:
   Total: 1680 partidas
   Ligas: 880 (52.4%)
   Copas: 800 (47.6%)

🎯 Acurácia no Test Set: XX.XX%
💾 Modelo salvo: ml_training/trained_models/xgboost_1x2_hybrid.pkl
```

---

### **3️⃣ Ativar Novo Modelo no Sistema**

**Opção A: Usar como modelo PADRÃO**

Edite `bet-insight/backend/apps/analysis/services/ml_integration.py`:

```python
class MLModel1X2:
    def __init__(self, model_path='ml_training/trained_models/xgboost_1x2_hybrid.pkl'):
        # Mudou de xgboost_1x2.pkl → xgboost_1x2_hybrid.pkl
```

**Opção B: Usar modelo HÍBRIDO apenas para copas**

Edite `analysis_orchestrator.py`:

```python
# Detectar tipo de competição
is_cup = competition.get('is_cup_competition', False)

# Usar modelo apropriado
if is_cup:
    ml_model_path = 'ml_training/trained_models/xgboost_1x2_hybrid.pkl'
else:
    ml_model_path = 'ml_training/trained_models/xgboost_1x2.pkl'

self.ensemble = ModelEnsembleML(ml_model_path=ml_model_path)
```

---

## 📊 VALIDAÇÃO

### Testar com partida de copa conhecida:

```bash
cd bet-insight/backend
python manage.py shell
```

```python
from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

# Buscar uma partida de copa
match = Match.objects.get(api_football_id=1508602)  # Anderlecht vs Antwerp

# Executar análise
orchestrator = HybridAnalysisOrchestrator()
result = orchestrator.run(match, strategy='value')

# Verificar predição
print(f"Predição: {result['prediction']}")
print(f"Probabilidades: H {result['home_probability']}% | D {result['draw_probability']}% | A {result['away_probability']}%")
print(f"xG: Casa {result['home_xg']} | Fora {result['away_xg']}")
```

---

## 🔍 ESTRUTURA DE ARQUIVOS

```
bet-insight/backend/
├── collect_cup_data.py              # Script de coleta (NOVO)
├── retrain_with_cups.py             # Script de retreino (NOVO)
├── retrain_hybrid_report.json       # Relatório de retreino (gerado)
│
└── ml_training/
    ├── cup_training_dataset.json    # Dataset de copas (gerado)
    ├── trained_models/
    │   ├── xgboost_1x2.pkl          # Modelo original (ligas)
    │   ├── xgboost_1x2_hybrid.pkl   # Modelo híbrido (NOVO)
    │   ├── feature_names.json       # Features do modelo original
    │   └── feature_names_hybrid.json # Features do modelo híbrido
```

---

## ⚠️ IMPORTANTE

### **Limitações da API (Free Tier)**
- **300 requests/dia**
- **Solução:** Script usa `time.sleep(0.5)` = ~0.3 req/min seguro
- **800 partidas** = ~400 segundos (6-7 minutos)

### **Se ultrapassar limite:**
```python
# Em collect_cup_data.py, ajuste o target:
collector.collect_cup_matches(
    target_matches=300,  # Reduzir para 300/dia
    output_file='cup_training_dataset_partial.json'
)
```

Execute em **3 dias** para coletar 800 partidas.

---

## 🎯 RESULTADOS ESPERADOS

### **Antes (Modelo Original - 880 partidas de ligas)**
- ✅ Ligas: ~52% acurácia
- ❌ Copas: ~40% acurácia (erro sistemático de xG)

### **Depois (Modelo Híbrido - 1680 partidas)**
- ✅ Ligas: ~52% acurácia (mantido)
- ✅ Copas: ~48-50% acurácia (MELHORIA)
- ✅ Over 2.5 em copas: Redução de erro de 46%

---

## 🐛 TROUBLESHOOTING

### **Erro: "429 Too Many Requests"**
```
⏰ Limite da API atingido. Aguarde 24h ou:
   - Reduza target_matches para 300
   - Execute em dias diferentes
```

### **Erro: "XGBoost não instalado"**
```bash
pip install xgboost
```

### **Erro: "cup_training_dataset.json não encontrado"**
```bash
# Execute primeiro a coleta:
python collect_cup_data.py
```

---

## 📈 MONITORAMENTO

Após retreino, monitore métricas:

```sql
-- Comparar acurácia antes/depois por tipo de competição
SELECT 
    league.name,
    COUNT(*) as total_matches,
    AVG(CASE WHEN prediction_correct THEN 1 ELSE 0 END) as accuracy
FROM matches
WHERE analyzed_at > '2026-02-06'  -- Após retreino
GROUP BY league.name
ORDER BY accuracy DESC;
```

---

## ✅ CHECKLIST

- [ ] Executar `collect_cup_data.py` (6-8 min)
- [ ] Verificar `cup_training_dataset.json` criado
- [ ] Executar `retrain_with_cups.py` (2-3 min)
- [ ] Verificar acurácia ≥ 50%
- [ ] Verificar `xgboost_1x2_hybrid.pkl` criado
- [ ] Atualizar `ml_integration.py` com novo modelo
- [ ] Testar com partida de copa conhecida
- [ ] Validar predições em produção
- [ ] Monitorar métricas por 1 semana

---

**Criado em:** 06/02/2026  
**Versão:** 1.0
