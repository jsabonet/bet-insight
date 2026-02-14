"""
Script de teste para partida 1387895
Valida todas as correções do Sprint 5
"""
import sys
import os
import django

# Configurar Django
sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("="*80)
print("🧪 TESTE PARTIDA 1387895 - Validação Sprint 5")
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
print("\n1️⃣ Buscando dados da partida 1387895...")
api_service = FootballAPIService()
fixture_result = api_service.get_fixture_by_id(1387895)

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
    'api_id': 1387895,
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
        print(f"      Mercados favorecidos: {', '.join(pattern.get('favorable_markets', [])[:3])}")
        
        # ✅ VALIDAR: Nomenclatura canônica
        for market in pattern.get('favorable_markets', []):
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
    
    # Enriquecer odds
    odds_calc = OddsCalculator()
    market_odds = odds_calc.enrich_odds_dict(base_odds)
    
    print(f"✅ Odds enriquecidas: {len(market_odds)} mercados")
    print(f"   - Odds da API: {sum(1 for v in base_odds.values() if v)}")
    print(f"   - Odds calculadas (DC/DNB/Asian): {len(market_odds) - sum(1 for v in base_odds.values() if v)}")
    
    # ✅ VALIDAR: Estrutura enriquecida
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

# 8. Decision Engine
print("\n7️⃣ Executando Decision Engine...")
decision_engine = DecisionEngine()

try:
    decision_data = decision_engine.make_decision(
        model_predictions=model_predictions,
        features=features,
        market_odds=market_odds,
        strategy='value',
        context_analysis=context_analysis
    )
    
    print(f"✅ Decisão gerada com sucesso!")
    print(f"\n📊 Recomendação Principal:")
    rec = decision_data.get('recommendation', {})
    print(f"   - Mercado: {rec.get('market_display', rec.get('market'))}")
    print(f"   - Probabilidade: {rec.get('probability', 0):.1%}")
    print(f"   - Odd: {rec.get('odd', 'N/A')}")
    
    # Top 3 apostas
    top_bets = decision_data.get('top_bets', [])
    print(f"\n🏆 Top 3 Apostas:")
    
    for bet in top_bets:
        print(f"\n   #{bet.get('rank', '?')}. {bet.get('market_display', bet.get('market'))}")
        print(f"      Probabilidade: {bet.get('probability', 0):.1%}")
        print(f"      Odd: {bet.get('market_odd', 'N/A')}")
        print(f"      EV: {bet.get('ev_pct', 0):+.1f}%")
        print(f"      Score: {bet.get('score', 0):.3f}")
        print(f"      Razão: {bet.get('reason', 'N/A')}")
        
        # ✅ VALIDAR: Nomenclatura canônica no market
        market = bet.get('market', '')
        if any(c.isupper() for c in market if c.isalpha()):
            print(f"      ❌ ERRO: Mercado com maiúsculas: '{market}'")
    
    # Verificar se contexto foi usado
    if context_analysis and context_analysis.get('patterns'):
        print(f"\n✅ CONTEXTO FOI CONSIDERADO ({len(patterns)} padrões)")
    else:
        print(f"\n⚠️ CONTEXTO NÃO FOI USADO (sem padrões detectados)")
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*80)
    
    # Resumo de validações
    validations = []
    
    # 1. Nomenclatura canônica
    all_canonical = True
    for bet in top_bets:
        if any(c.isupper() for c in bet.get('market', '') if c.isalpha()):
            all_canonical = False
    validations.append(("Nomenclatura canônica", all_canonical))
    
    # 2. Odds enriquecidas
    has_enriched = market_odds and any(isinstance(v, dict) for v in market_odds.values())
    validations.append(("Odds enriquecidas", has_enriched))
    
    # 3. Contexto considerado
    context_used = bool(context_analysis and context_analysis.get('patterns'))
    validations.append(("Contexto considerado", context_used))
    
    # 4. Top bets gerados
    has_top_bets = len(top_bets) > 0
    validations.append(("Top bets gerados", has_top_bets))
    
    print("\n📋 Resumo de Validações:")
    for name, passed in validations:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")
    
    all_passed = all(v[1] for v in validations)
    sys.exit(0 if all_passed else 1)
    
except Exception as e:
    print(f"\n❌ ERRO ao executar Decision Engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
