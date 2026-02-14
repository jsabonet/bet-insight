"""
Script de teste para partida 1388498
Valida análise de contexto e Decision Engine
"""
import sys
import os
import django

# Configurar Django
sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("="*80)
print("🧪 TESTE PARTIDA 1388498 - Contexto + Decision Engine")
print("="*80)

# Importar serviços
from apps.matches.services.football_api import FootballAPIService
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.odds_calculator import OddsCalculator
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Buscar dados da partida
print("\n1️⃣ Buscando dados da partida 1388498...")
api_service = FootballAPIService()
fixture_result = api_service.get_fixture_by_id(1388498)

if not fixture_result.get('success'):
    print(f"❌ Erro ao buscar partida: {fixture_result.get('error')}")
    sys.exit(1)

fixture = fixture_result['fixture']
print(f"✅ Partida encontrada: {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
print(f"   Liga: {fixture['league']['name']}")
print(f"   Data: {fixture['fixture']['date']}")

# 2. Construir match_data
match_data = {
    'home_team': {'name': fixture['teams']['home']['name']},
    'away_team': {'name': fixture['teams']['away']['name']},
    'league': fixture['league']['name'],
    'date': fixture['fixture']['date'],
    'status': fixture['fixture']['status']['short'],
    'api_id': 1388498,
    'fixture': fixture
}

# 3. Enriquecer dados
print("\n2️⃣ Enriquecendo dados...")
enricher = MatchDataEnricher()
match_data = enricher.enrich(match_data)

print(f"✅ Dados enriquecidos:")
print(f"   - Odds disponíveis: {'Sim' if match_data.get('odds') else 'Não'}")
print(f"   - Estatísticas: {'Sim' if match_data.get('home_stats') else 'Não'}")

# 4. Feature Engineering
print("\n3️⃣ Executando Feature Engineering...")
engineer = FeatureEngineer()
features = engineer.engineer_all_features(match_data)

print(f"✅ Features geradas: {list(features.keys())}")
print(f"   - Motivation: {features.get('motivation', {}).get('home_motivation', 'N/A')} (home), {features.get('motivation', {}).get('away_motivation', 'N/A')} (away)")
print(f"   - Strength diff: {features.get('strength', {}).get('strength_differential', 'N/A')}")

# 5. Context Analyzer
print("\n4️⃣ Analisando contexto...")
context_analyzer = ContextAnalyzer()
context_analysis = context_analyzer.analyze(features)

patterns = context_analysis.get('patterns', [])
print(f"✅ Padrões detectados: {len(patterns)}")

if patterns:
    for i, pattern in enumerate(patterns[:3], 1):
        print(f"   {i}. {pattern.get('name', 'Unknown')}")
        print(f"      Confiança: {pattern.get('confidence', 0):.0%}")
        fav = pattern.get('favorable_markets', [])
        print(f"      Mercados favorecidos: {', '.join(fav[:5])}")
        # Validação canônica
        for market in fav:
            if any(c.isupper() for c in market if c.isalpha()):
                print(f"      ❌ ERRO: Mercado com maiúsculas: '{market}'")

# 6. Preparar odds enriquecidas
print("\n5️⃣ Preparando odds do mercado...")
raw_odds = match_data.get('odds', {})

if raw_odds and raw_odds.get('home_win'):
    base_odds = {
        'home_win': raw_odds.get('home_win'),
        'draw': raw_odds.get('draw'),
        'away_win': raw_odds.get('away_win'),
        'over_2.5': raw_odds.get('over_25'),
        'under_2.5': raw_odds.get('under_25'),
        'over_1.5': raw_odds.get('over_15'),
        'under_1.5': raw_odds.get('under_15'),
        'over_3.5': raw_odds.get('over_35'),
        'under_3.5': raw_odds.get('under_35'),
        'btts_yes': raw_odds.get('btts_yes'),
    }
    odds_calc = OddsCalculator()
    market_odds = odds_calc.enrich_odds_dict(base_odds)
    print(f"✅ Odds enriquecidas: {len(market_odds)} mercados")
    print(f"   - Odds da API: {sum(1 for v in base_odds.values() if v)}")
    print(f"   - Odds calculadas (DC/DNB/Asian): {len(market_odds) - sum(1 for v in base_odds.values() if v)}")
    for market, odd_data in list(market_odds.items())[:3]:
        if isinstance(odd_data, dict):
            print(f"   - {market}: {odd_data.get('value')} (source: {odd_data.get('source')})")
        else:
            print(f"   ❌ ERRO: Odd não enriquecida: {market} = {odd_data}")
else:
    market_odds = None
    print("⚠️ Sem odds da API")

# 7. Modelos estatísticos
print("\n6️⃣ Executando modelos estatísticos...")
home_strength = match_data.get('home_stats', {}).get('goals_per_game_avg', 1.5)
away_strength = match_data.get('away_stats', {}).get('goals_per_game_avg', 1.3)
home_defense = match_data.get('home_stats', {}).get('conceded_per_game_avg', 1.3)
away_defense = match_data.get('away_stats', {}).get('conceded_per_game_avg', 1.3)
weather_impact = features.get('weather', {}).get('goal_impact', 0.0)

ensemble = ModelEnsemble()
model_predictions = ensemble.predict(
    features,
    home_strength,
    away_strength,
    weather_impact,
    league_id=match_data.get('fixture', {}).get('league', {}).get('id'),
    home_defense=home_defense,
    away_defense=away_defense
)

consensus = model_predictions.get('consensus', {})
print(f"✅ Consensus:")
print(f"   - Casa: {consensus.get('home_win', 0):.1%}")
print(f"   - Empate: {consensus.get('draw', 0):.1%}")
print(f"   - Fora: {consensus.get('away_win', 0):.1%}")

# 🔍 DEBUG: Verificar estrutura completa
print(f"\n🔍 DEBUG model_predictions keys: {list(model_predictions.keys())}")
print(f"🔍 DEBUG poisson keys: {list(model_predictions.get('poisson', {}).keys())}")
if 'probabilities' in model_predictions.get('poisson', {}):
    print(f"🔍 DEBUG poisson.probabilities keys: {list(model_predictions['poisson']['probabilities'].keys())}")
else:
    print(f"⚠️ poisson.probabilities NÃO EXISTE!")
    # Ver se as probs estão diretamente em poisson
    print(f"🔍 DEBUG poisson direto: {model_predictions.get('poisson', {})}")


# 8. Decision Engine
print("\n7️⃣ Executando Decision Engine...")
decision_engine = DecisionEngine()

try:
    decision_data = decision_engine.make_decision(
        model_predictions=model_predictions,
        features=features,
        market_odds=market_odds,
        strategy='multiple',  # 🎯 MÚLTIPLOS: Alta probabilidade para bilhetes
        context_analysis=context_analysis
    )

    print(f"✅ Decisão gerada com sucesso!")
    print(f"\n📊 Recomendação Principal:")
    rec = decision_data.get('recommendation', {})
    print(f"   - Mercado: {rec.get('market_display', rec.get('market'))}")
    print(f"   - Probabilidade: {rec.get('probability', 0):.1%}")
    print(f"   - Odd: {rec.get('odd', 'N/A')}")

    top_bets = decision_data.get('top_bets', [])
    print(f"\n🏆 Top 3 Apostas:")
    for bet in top_bets[:3]:
        print(f"\n   #{bet.get('rank', '?')}. {bet.get('market_display', bet.get('market'))}")
        print(f"      Probabilidade: {bet.get('probability', 0):.1%}")
        print(f"      Odd: {bet.get('market_odd', 'N/A')}")
        print(f"      EV: {bet.get('ev_pct', 0):+.1f}%")
        print(f"      Score: {bet.get('score', 0):.3f}")
        print(f"      Razão: {bet.get('reason', 'N/A')}")
        market = bet.get('market', '')
        if any(c.isupper() for c in market if c.isalpha()):
            print(f"      ❌ ERRO: Mercado com maiúsculas: '{market}'")
    
    # 🔍 DEBUG: Mostrar TODOS os candidatos considerados (não apenas top 3)
    print(f"\n📊 DEBUG: Probabilidades de TODOS os mercados:")
    print(f"   Over 2.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('over_2.5', 0):.1%}")
    print(f"   Under 2.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('under_2.5', 0):.1%}")
    print(f"   Over 1.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('over_1.5', 0):.1%}")
    print(f"   Under 1.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('under_1.5', 0):.1%}")
    print(f"   Over 3.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('over_3.5', 0):.1%}")
    print(f"   Under 3.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('under_3.5', 0):.1%}")
    print(f"   BTTS: {model_predictions.get('poisson', {}).get('probabilities', {}).get('btts', 0):.1%}")
    print(f"   Casa Over 0.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('home_over_0.5', 0):.1%}")
    print(f"   Casa Over 1.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('home_over_1.5', 0):.1%}")
    print(f"   Fora Over 0.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('away_over_0.5', 0):.1%}")
    print(f"   Fora Over 1.5: {model_predictions.get('poisson', {}).get('probabilities', {}).get('away_over_1.5', 0):.1%}")


    context_used = bool(context_analysis and context_analysis.get('patterns'))
    print(f"\n{'✅ CONTEXTO FOI CONSIDERADO' if context_used else '⚠️ CONTEXTO NÃO FOI USADO'} ({len(patterns)} padrões)")

    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO")
    print("="*80)
    sys.exit(0)

except Exception as e:
    print(f"\n❌ ERRO ao executar Decision Engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
