"""
PLANO DE AÇÃO: Acurácia 55%+
================================

PROBLEMA ATUAL:
- Acurácia: 40.51% (32/79)
- Empates: 0/31 acertados (0%)
- Casa: 26/27 acertados (96.3%)
- Fora: 6/21 acertados (28.6%)

ESTRATÉGIAS IMPLEMENTADAS:

1. ✅ Boost de Empate em Jogos Equilibrados (15-30%)
   Localização: statistical_models.py linhas 663-674
   Impacto esperado: +5-10% acurácia

2. 🔄 PRÓXIMAS AÇÕES (Ordem de Impacto):

A) AUMENTAR BOOST DE EMPATE (Impacto: +8-12%)
   - Aumentar de 30% para 50% em jogos muito equilibrados
   - Expandir janela de 15pp para 20pp
   - Adicionar boost extra quando xG está equilibrado

B) CALIBRAÇÃO POR CONTEXTO (Impacto: +5-8%)
   - Empate mais provável quando:
     * Ambos times em posições próximas (diff < 3)
     * Ambos com defesas fortes (< 1.0 gols/jogo)
     * H2H recente tem > 40% empates
   
C) AJUSTAR PESOS DO ENSEMBLE (Impacto: +3-5%)
   - Testar: Poisson 40%, Logística 50%, Market 10%
   - Logística pode estar melhor calibrada para empates
   
D) THRESHOLD DE CONFIANÇA (Impacto: +5-7% mas -20% volume)
   - Só publicar se:
     * Probabilidade máxima >= 45%
     * Confiança >= 4/5
     * EV >= 0% (sem value negativo)

E) FEATURES ADICIONAIS PARA EMPATE (Impacto: +3-5%)
   - Ratio defesa/ataque de ambos times
   - Média de gols nos últimos 5 H2H
   - Fase da temporada (final tem mais empates)
   - Importância do jogo (rivalidade)

IMPLEMENTAÇÃO PRIORITÁRIA:
1. Aumentar boost (A) - Rápido, alto impacto
2. Calibração contexto (B) - Médio esforço, alto impacto  
3. Ajustar ensemble (C) - Rápido, médio impacto
4. Threshold (D) - Trade-off volume/acurácia
5. Features (E) - Alto esforço, médio impacto

TESTE INCREMENTAL:
- Implementar A → Validar → Meta: 48%
- Adicionar B → Validar → Meta: 52%
- Adicionar C → Validar → Meta: 55%+

MÉTRICAS DE SUCESSO:
✓ Acurácia geral >= 55%
✓ Empates >= 25% dos previstos (vs 0% atual)
✓ Acurácia de empates >= 35% (vs 0% atual)
✓ Manter coverage > 70% das partidas
"""
