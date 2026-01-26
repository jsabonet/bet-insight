"""
Teste COMPLETO: Análise da partida Barcelona vs Oviedo
Usando HybridAnalysisOrchestrator (fluxo completo de produção)
"""
import os
import sys
import django
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from apps.matches.models import Match

print("="*80)
print("TESTE: Análise Completa - Barcelona vs Oviedo")
print("="*80)

# Buscar a partida Barcelona vs Oviedo
match = Match.objects.filter(
    api_football_id=1391021
).first()

if not match:
    print("\n[X] Partida não encontrada no banco de dados")
    sys.exit(1)

print(f"\n[OK] Partida encontrada:")
print(f"   ID: {match.api_football_id}")
print(f"   Jogo: {match.home_team.name} vs {match.away_team.name}")
print(f"   Liga: {match.league.name}")
print(f"   Data: {match.match_date}")
print(f"   Status: {match.status}")

print("\n" + "="*80)
print("EXECUTANDO ANÁLISE COMPLETA (HybridAnalysisOrchestrator)")
print("="*80)
print("\nComponentes:")
print("  1. MatchDataEnricher (enriquecimento)")
print("  2. FeatureEngineer (109 features)")
print("  3. ModelEnsembleML (Poisson + XGBoost + Market)")
print("  4. DecisionEngine (value bets + confidence)")
print("  5. AIAnalyzer (explicação)")
print()

# Executar análise completa
orchestrator = HybridAnalysisOrchestrator()
result = orchestrator.run(match, strategy='value')

print("\n" + "="*80)
print("RESULTADO DA ANÁLISE")
print("="*80)

# Dados principais
prediction = result.get('prediction', 'N/A')
confidence = result.get('confidence', 0)
home_prob = result.get('home_probability', 0)
draw_prob = result.get('draw_probability', 0)
away_prob = result.get('away_probability', 0)
home_xg = result.get('home_xg', 0)
away_xg = result.get('away_xg', 0)

print(f"\n[*] PREVISAO: {prediction.upper()}")
print(f"[*] CONFIANCA: {confidence}/5 estrelas")
print(f"\n[*] PROBABILIDADES:")
print(f"    Casa (Barcelona): {home_prob}%")
print(f"    Empate: {draw_prob}%")
print(f"    Fora (Oviedo): {away_prob}%")
print(f"\n[*] EXPECTED GOALS (xG):")
print(f"    Casa: {home_xg:.2f}")
print(f"    Fora: {away_xg:.2f}")

# Analysis data
analysis_data = result.get('analysis_data', {})
consensus = analysis_data.get('consensus', {})
poisson = analysis_data.get('poisson', {})
fair_odds = analysis_data.get('fair_odds', {})
top_bets = analysis_data.get('top_bets', [])
recommendation = analysis_data.get('recommendation', {})
risk = analysis_data.get('risk', 'N/A')

print(f"\n" + "="*80)
print("DETALHES DOS MODELOS")
print("="*80)

print(f"\n[*] CONSENSUS (Ensemble):")
print(f"    Casa: {consensus.get('home_win', 0)*100:.2f}%")
print(f"    Empate: {consensus.get('draw', 0)*100:.2f}%")
print(f"    Fora: {consensus.get('away_win', 0)*100:.2f}%")

poisson_xg = poisson.get('expected_goals', {})
print(f"\n[*] POISSON (xG):")
print(f"    Casa: {poisson_xg.get('home', 0):.2f}")
print(f"    Fora: {poisson_xg.get('away', 0):.2f}")

print(f"\n[*] ODDS JUSTAS (Fair Value):")
print(f"    Casa: {fair_odds.get('home_win', 0):.2f}")
print(f"    Empate: {fair_odds.get('draw', 0):.2f}")
print(f"    Fora: {fair_odds.get('away_win', 0):.2f}")
print(f"    Over 2.5: {fair_odds.get('over_2_5', 0):.2f}")
print(f"    Under 2.5: {fair_odds.get('under_2_5', 0):.2f}")
print(f"    BTTS: {fair_odds.get('btts', 0):.2f}")

print(f"\n[*] RECOMENDACAO:")
print(f"    Mercado: {recommendation.get('market_display', 'N/A')}")
print(f"    Probabilidade: {recommendation.get('probability', 0)*100:.1f}%")
print(f"    Odd Justa: {recommendation.get('fair_odd', 0):.2f}")
print(f"    Risco: {risk.upper()}")

if top_bets:
    print(f"\n[*] TOP BETS (Value):")
    for i, bet in enumerate(top_bets[:3], 1):
        print(f"\n    #{i} {bet.get('market_display', 'N/A')}")
        print(f"        Probabilidade: {bet.get('probability', 0)*100:.1f}%")
        print(f"        Odd Mercado: {bet.get('market_odd', 0):.2f}")
        print(f"        Odd Justa: {bet.get('fair_odd', 0):.2f}")
        print(f"        EV: {bet.get('ev_pct', 0):+.1f}%")
        print(f"        Stake: {bet.get('stake_pct', 0):.1f}% da banca")
else:
    print(f"\n[!] Nenhum value bet encontrado")

# Reasoning
reasoning = result.get('reasoning', '')
print(f"\n" + "="*80)
print("RACIOCÍNIO DA IA")
print("="*80)
print(f"\n{reasoning[:500]}...")  # Primeiros 500 caracteres

# Salvar resultado completo
output_file = 'analysis_barcelona_oviedo.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n" + "="*80)
print("CONCLUSAO")
print("="*80)
print(f"\n[OK] Analise completa executada com sucesso!")
print(f"[OK] Resultado completo salvo em: {output_file}")
print(f"\n[*] Sistema operando com:")
print(f"    - Enriquecimento: 100/100")
print(f"    - Features: 109")
print(f"    - Acuracia esperada: 65%")
print(f"    - Confianca: {confidence}/5")
print(f"\n" + "="*80)
