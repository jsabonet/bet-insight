"""
Script para verificar o que o ContextAnalyzer detectou na partida Atletico vs Barcelona
"""
import os
import sys
import django
import logging

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.context_analyzer import ContextAnalyzer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s %(name)s %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def main():
    match_id = 1520391
    
    print("\n" + "="*80)
    print(f"ANALISANDO CONTEXTO DA PARTIDA {match_id}")
    print("Atletico Madrid vs Barcelona - Copa del Rey Semifinal")
    print("="*80 + "\n")
    
    # 1. Fetch match data
    api_service = APIFootballService()
    fixture_data = api_service.fetch_fixture_details(match_id)
    
    if not fixture_data:
        print("❌ Erro ao buscar dados da partida")
        return
    
    # 2. Enrich
    enricher = MatchDataEnricher()
    enriched = enricher.enrich_match_data(fixture_data)
    
    # 3. Engineer features
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(enriched)
    
    print("\n" + "="*80)
    print("FEATURES CRIADAS (resumo)")
    print("="*80)
    
    # Mostrar features relevantes
    motivation = features.get('motivation', {})
    print(f"\n📊 MOTIVAÇÃO:")
    print(f"   Casa (Atletico): {motivation.get('home_motivation', 0):.1f}/10")
    print(f"   Fora (Barcelona): {motivation.get('away_motivation', 0):.1f}/10")
    print(f"   Diferencial: {motivation.get('motivation_differential', 0):+.1f}")
    
    context = features.get('context', {})
    print(f"\n⏱️ CONTEXTO:")
    print(f"   Descanso Casa: {context.get('home_rest_days', 0)} dias")
    print(f"   Descanso Fora: {context.get('away_rest_days', 0)} dias")
    print(f"   Vantagem: {context.get('rest_advantage', 0):+.0f} dias")
    
    competition = features.get('competition', {})
    print(f"\n🏆 COMPETIÇÃO:")
    print(f"   É Copa: {competition.get('is_cup_competition', False)}")
    print(f"   Nome: {competition.get('competition_name', 'N/A')}")
    print(f"   Knockout: {competition.get('is_knockout_stage', False)}")
    
    strength = features.get('strength', {})
    print(f"\n💪 FORÇA:")
    print(f"   xG Casa: {strength.get('home_goals_per_game', 0):.2f}")
    print(f"   xG Fora: {strength.get('away_goals_per_game', 0):.2f}")
    print(f"   Diferencial: {strength.get('strength_differential', 0):+.2f}")
    
    form = features.get('form', {})
    print(f"\n📈 FORMA:")
    print(f"   Casa (ajustada): {form.get('home_adjusted_form', 0):.2f}")
    print(f"   Fora (ajustada): {form.get('away_adjusted_form', 0):.2f}")
    print(f"   Diferencial: {form.get('adjusted_form_diff', 0):+.2f}")
    
    injuries = features.get('injuries_suspensions', {})
    print(f"\n🏥 LESÕES:")
    print(f"   Impacto Casa: {injuries.get('home_injury_impact', 0):.2f}")
    print(f"   Impacto Fora: {injuries.get('away_injury_impact', 0):.2f}")
    print(f"   Diferencial: {injuries.get('injury_impact_differential', 0):+.2f}")
    
    # 4. Run ContextAnalyzer
    print("\n" + "="*80)
    print("EXECUTANDO CONTEXT ANALYZER")
    print("="*80 + "\n")
    
    analyzer = ContextAnalyzer()
    context_result = analyzer.analyze(features)
    
    # Mostrar resultados
    patterns = context_result.get('patterns', [])
    
    if not patterns:
        print("❌ Nenhum padrão contextual detectado")
    else:
        print(f"\n✅ {len(patterns)} PADRÃO(ÕES) DETECTADO(S):\n")
        
        for i, pattern in enumerate(patterns, 1):
            print(f"{i}. {pattern['name'].upper()}")
            print(f"   Confiança: {pattern['confidence']:.0%}")
            print(f"   Mercados favorecidos: {', '.join(pattern['favorable_markets'])}")
            print(f"   Raciocínio: {pattern['reasoning']}")
            print()
    
    # Top markets
    top_markets = context_result.get('top_markets', [])
    if top_markets:
        print("\n" + "-"*80)
        print("📊 TOP MERCADOS POR CONTEXTO:")
        print("-"*80)
        for market_data in top_markets[:10]:
            market = market_data['market']
            score = market_data['context_score']
            print(f"   {market:20s}: {score:.0%}")
    
    print("\n" + "="*80)
    print("ANÁLISE CONCLUÍDA")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
