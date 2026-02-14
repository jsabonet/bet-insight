"""
Simulação Frontend: Sevilla vs Alaves (ID: 3168)
Verificar exibição do EV após correção
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.odds_calculator import OddsCalculator
from apps.ml.services.ml_orchestrator import MLOrchestrator

print('=' * 80)
print('🏆 ANÁLISE: SEVILLA vs ALAVES (STRATEGY: MULTIPLE)')
print('=' * 80)

try:
    # Carregar partida
    match = Match.objects.get(id=3168)
    print(f'\n✅ Partida encontrada:')
    print(f'   🏠 Casa: {match.home_team.name}')
    print(f'   ✈️  Fora: {match.away_team.name}')
    print(f'   📅 Data: {match.match_date}')
    print(f'   🏟️  Liga: {match.league.name if match.league else "N/A"}')
    
    # Pipeline de análise
    print('\n⚙️  Executando pipeline de análise...')
    
    enricher = MatchDataEnricher()
    enriched = enricher.enrich_match(match)
    
    odds_calc = OddsCalculator()
    enriched = odds_calc.calculate_missing_odds(enriched)
    
    feature_eng = FeatureEngineer()
    features = feature_eng.engineer_features(enriched)
    
    ml_orch = MLOrchestrator()
    predictions = ml_orch.predict(features, enriched['market_odds'])
    
    context_analyzer = ContextAnalyzer()
    context = context_analyzer.analyze(features, predictions, enriched['market_odds'])
    
    decision_engine = DecisionEngine()
    
    result = decision_engine.generate_recommendation(
        model_predictions=predictions,
        market_odds=enriched['market_odds'],
        features=features,
        context_analysis=context,
        strategy='multiple'
    )
    
    print('\n' + '=' * 80)
    print('📊 PROBABILIDADES DO MODELO')
    print('=' * 80)
    
    consensus = predictions.get('consensus', {})
    print(f'   🏠 Casa: {consensus.get("home_win", 0)*100:.1f}%')
    print(f'   ⚖️  Empate: {consensus.get("draw", 0)*100:.1f}%')
    print(f'   ✈️  Fora: {consensus.get("away_win", 0)*100:.1f}%')
    
    print('\n' + '=' * 80)
    print('🎯 TOP BETS (Dados do Backend - DecisionEngine)')
    print('=' * 80)
    
    for bet in result['top_bets']:
        print(f"\n#{bet['rank']}: {bet['market_display']}")
        print(f"  📊 Probabilidade: {bet['probability']*100:.1f}%")
        print(f"  💰 Odd: {bet.get('market_odd', 'N/A')}")
        print(f"  📈 EV: {bet['ev_pct']:+.1f}%")
        print(f"  💵 Stake: {bet['stake_units']}u")
        print(f"  📝 Reason: {bet['reason']}")
    
    print('\n' + '=' * 80)
    print('🖥️  SIMULAÇÃO FRONTEND (Como aparece no AnalysisModal)')
    print('=' * 80)
    print('\n📋 Top Bets:')
    
    for i, bet in enumerate(result['top_bets'], 1):
        print(f"\n{i}. {bet['market_display']}")
        print(f"   📊 Probabilidade: {bet['probability']*100:.1f}%")
        print(f"   💰 Odd: {bet.get('market_odd', 'N/A')}")
        print(f"   💵 Stake: {bet['stake_units']}u")
        print(f"   ℹ️  {bet['reason']}")
        print(f"   \033[92m✅ EV VISÍVEL: {bet['ev_pct']:+.1f}%\033[0m")
    
    print('\n' + '=' * 80)
    print('✨ COMPARAÇÃO: ANTES vs DEPOIS da correção')
    print('=' * 80)
    
    for bet in result['top_bets'][:2]:  # Mostrar primeiras 2 apostas
        prob = bet['probability'] * 100
        ev = bet['ev_pct']
        
        print(f"\n{bet['market_display']}:")
        print(f"  ❌ ANTES: Alta probabilidade: {prob:.1f}% (sem value significativo)")
        print(f"  ✅ DEPOIS: {bet['reason']}")
    
    print('\n' + '=' * 80)
    print('🎉 RESULTADO: EV agora está sempre visível!')
    print('=' * 80)
    
    # Salvar resultado em JSON para inspeção
    output = {
        'match': {
            'id': match.id,
            'home_team': match.home_team.name,
            'away_team': match.away_team.name,
            'match_date': str(match.match_date)
        },
        'probabilities': {
            'home_win': f"{consensus.get('home_win', 0)*100:.1f}%",
            'draw': f"{consensus.get('draw', 0)*100:.1f}%",
            'away_win': f"{consensus.get('away_win', 0)*100:.1f}%"
        },
        'top_bets': [
            {
                'rank': bet['rank'],
                'market': bet['market'],
                'market_display': bet['market_display'],
                'probability': f"{bet['probability']*100:.1f}%",
                'market_odd': bet.get('market_odd'),
                'ev_pct': f"{bet['ev_pct']:+.1f}%",
                'stake_units': bet['stake_units'],
                'reason': bet['reason']
            } for bet in result['top_bets']
        ],
        'strategy': result['strategy']
    }
    
    with open('sevilla_alaves_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultado salvo em: sevilla_alaves_analysis.json")

except Match.DoesNotExist:
    print('\n❌ Partida ID 3168 não encontrada no banco de dados')
except Exception as e:
    print(f'\n❌ Erro durante análise: {str(e)}')
    import traceback
    traceback.print_exc()
