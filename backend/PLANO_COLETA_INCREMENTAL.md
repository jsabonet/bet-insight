# 📊 Plano de Coleta Incremental - ML Dataset

## 🚨 Problema Identificado
- **Limite diário da API atingido** (plano free: 100 req/dia)
- Coletamos: **880/5000 partidas** (17.6%)
- Modelo treinado com 880: **52.3% acurácia** (XGBoost)

## ✅ Status Atual (25 Jan 2026)
```
Dataset: training_dataset.json
Total: 880 partidas
Distribuição: Casa 44.5% | Empate 25.2% | Fora 30.2%

Ligas coletadas:
- Premier League: 500 partidas (2023, 2024)
- La Liga: 380 partidas (2023)
- Outras ligas: 0 (limite atingido)
```

## 📈 Estratégia de Coleta

### Opção 1: Uso Imediato (RECOMENDADO)
- ✅ **880 partidas é suficiente** para ML inicial
- ✅ Modelo já treinado: 52.3% acurácia
- ✅ Podemos integrar agora e validar em produção
- 🔄 Continuar coleta incremental nos próximos dias

### Opção 2: Aguardar Reset Diário
- Aguardar reset do limite (00:00 UTC)
- Continuar coleta automática até 5000
- Retreinar modelo com dataset completo

### Opção 3: Upgrade Plano API
- Plano Pro: 3000 req/dia (~R$50/mês)
- Permite coleta completa em 1 dia
- Acesso a mais estatísticas

## 🔄 Coleta Incremental Automática

Para continuar coletando sem perder o progresso:

```bash
# Dia 1: Já temos 880 partidas
# Dia 2: Continuar (script detecta checkpoint)
python ml_training/collect_historical_data.py --target 5000

# O script irá:
# 1. Carregar checkpoint existente (880)
# 2. Continuar de onde parou
# 3. Adicionar novas partidas ao dataset
```

## 🎯 Recomendação

**USAR AGORA com 880 partidas:**
1. ✅ Modelo já treinado (52.3% > baseline 46%)
2. Integrar no orchestrator
3. Validar com partidas reais
4. Coletar incrementalmente nos próximos 5 dias
5. Retreinar quando atingir 2000+ partidas

**Vantagens:**
- Começamos a usar ML hoje
- Validação imediata em produção
- Melhoria contínua conforme coletamos mais dados
- Sem custos adicionais

## 📋 Próximos Passos

1. ✅ Integrar modelo no `ModelEnsembleML`
2. Testar em validação com partidas reais
3. Monitorar acurácia vs baseline
4. Continuar coleta (reset diário automático)
5. Retreinar modelo quando dataset > 2000 partidas
