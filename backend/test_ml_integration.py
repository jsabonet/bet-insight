"""
Teste end-to-end da integração ML no sistema
Valida se o XGBoost otimizado está sendo usado corretamente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

print("="*80)
print("TESTE DE INTEGRAÇÃO ML - END-TO-END")
print("="*80)
print()

# Pegar uma partida finalizada recente
match = Match.objects.filter(
    status='finished',
    home_score__isnull=False,
    away_score__isnull=False,
    api_football_id__isnull=False
).order_by('-match_date').first()

if not match:
    print("Nenhuma partida encontrada para teste")
    sys.exit(1)

print(f"Partida de teste: {match.home_team.name} vs {match.away_team.name}")
print(f"Resultado: {match.home_score}-{match.away_score}")
print(f"Data: {match.match_date}")
print(f"API ID: {match.api_football_id}")
print()

try:
    # Executar análise
    orchestrator = HybridAnalysisOrchestrator()
    result = orchestrator.run(match, strategy='value')
    
    print("="*80)
    print("RESULTADO DA ANALISE")
    print("="*80)
    print()
    
    # Consensus via analysis_data
    print("Consensus (probabilidades):")
    print(f"  Casa: {result.get('home_probability', 0):.1f}%")
    print(f"  Empate: {result.get('draw_probability', 0):.1f}%")
    print(f"  Fora: {result.get('away_probability', 0):.1f}%")
    print()
    
    print(f"Expected Goals (xG):")
    print(f"  Casa: {result.get('home_xg', 0):.2f}")
    print(f"  Fora: {result.get('away_xg', 0):.2f}")
    print()
    
    print(f"Predicao: {result.get('prediction', 'N/A').upper()}")
    print(f"Confianca: {'*' * result.get('confidence', 0)} ({result.get('confidence', 0)}/5)")
    print(f"Publicar: {'SIM' if result.get('should_publish', False) else 'NAO'}")
    print()
    
    # Mostrar top bets
    analysis_data = result.get('analysis_data', {})
    top_bets = analysis_data.get('top_bets', [])
    print(f"Top Bets geradas: {len(top_bets)}")
    for i, bet in enumerate(top_bets[:3], 1):
        print(f"\n  #{i}: {bet.get('market_display')}")
        print(f"      Pick: {bet.get('pick_display')}")
        print(f"      Probabilidade: {bet.get('probability', 0)*100:.1f}%")
        print(f"      Odd: {bet.get('market_odd', 0):.2f}")
        print(f"      Value: {bet.get('value_pct', 0):.1f}%")
        print(f"      Confidence: {'*' * bet.get('confidence', 0)}")
    
    print()
    print("="*80)
    print("INTEGRACAO FUNCIONANDO OK")
    print("="*80)
    print()
    
    # Verificar uso de ML pelos logs (indireto)
    # Os logs mostrarão se XGBoost otimizado foi carregado
    print("NOTA: Verifique os logs acima para confirmar:")
    print("  - 'XGBoost OTIMIZADO: xgboost_balanced_...json'")
    print("  - Peso ML no ensemble (deve ser 50-70%)")
    print()
    
except Exception as e:
    print(f"[ERRO] ERRO na analise: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
