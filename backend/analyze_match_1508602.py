"""
Análise completa da partida 1508602 usando o fluxo completo do sistema
"""
import os
import sys
import django
import logging
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.api_football_service import APIFootballService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_finished_match(fixture_id: int):
    """
    Analisa uma partida finalizada e compara com resultado real
    """
    print("\n" + "=" * 100)
    print(f"🎯 ANÁLISE COMPLETA - PARTIDA {fixture_id}")
    print("=" * 100)
    
    # 1. Buscar detalhes da partida da API
    api_service = APIFootballService()
    fixture_details = api_service.fetch_fixture_details(fixture_id)
    
    if not fixture_details:
        print(f"❌ Erro: Partida {fixture_id} não encontrada na API")
        return
    
    # Extrair informações básicas
    home_team = fixture_details['home_team']['name']
    away_team = fixture_details['away_team']['name']
    league = fixture_details['league']['name']
    season = fixture_details['league']['season']
    match_date = fixture_details.get('date', 'N/A')
    status = fixture_details.get('status', 'N/A')
    
    print(f"\n📋 INFORMAÇÕES DA PARTIDA")
    print(f"{'─' * 100}")
    print(f"   🏠 Casa: {home_team}")
    print(f"   ✈️  Fora: {away_team}")
    print(f"   🏆 Liga: {league} ({season})")
    print(f"   📅 Data: {match_date}")
    print(f"   📊 Status: {status}")
    
    # Resultado real
    home_score = fixture_details.get('home_score')
    away_score = fixture_details.get('away_score')
    
    if home_score is not None and away_score is not None:
        print(f"\n⚽ RESULTADO REAL")
        print(f"{'─' * 100}")
        print(f"   {home_team} {home_score} x {away_score} {away_team}")
        
        # Determinar resultado
        if home_score > away_score:
            actual_result = 'home'
            result_text = f"✅ Vitória Casa"
        elif away_score > home_score:
            actual_result = 'away'
            result_text = f"✅ Vitória Fora"
        else:
            actual_result = 'draw'
            result_text = f"✅ Empate"
        
        print(f"   Resultado: {result_text}")
        
        # Mercados secundários
        total_goals = home_score + away_score
        over_25 = "Sim ✅" if total_goals > 2 else "Não ❌"
        btts = "Sim ✅" if home_score > 0 and away_score > 0 else "Não ❌"
        
        print(f"\n   📊 Mercados:")
        print(f"      Over 2.5: {over_25} (Total: {total_goals} gols)")
        print(f"      BTTS: {btts}")
    else:
        print(f"\n⚠️  Resultado não disponível (partida não finalizada ou dados incompletos)")
        actual_result = None
    
    # 2. Executar análise completa com o Orchestrator
    print(f"\n" + "=" * 100)
    print(f"🤖 EXECUTANDO ANÁLISE COM HYBRID ORCHESTRATOR")
    print(f"=" * 100)
    
    # Criar objeto de match simulado
    class MockMatch:
        def __init__(self, api_id):
            self.api_football_id = api_id
            self.league = None
    
    mock_match = MockMatch(fixture_id)
    
    # Executar ambas estratégias
    print(f"\n📊 Estratégia VALUE (apostas simples com EV)")
    print(f"{'─' * 100}")
    orchestrator = HybridAnalysisOrchestrator()
    
    try:
        result_value = orchestrator.run(mock_match, strategy='value')
        
        print(f"\n✅ Análise VALUE concluída")
        print(f"\n🎯 PREVISÃO DO SISTEMA (VALUE)")
        print(f"{'─' * 100}")
        
        # Previsão principal
        prediction = result_value.get('prediction', 'N/A')
        confidence = result_value.get('confidence', {})
        
        prediction_map = {
            'home': f'Vitória Casa ({home_team})',
            'draw': 'Empate',
            'away': f'Vitória Fora ({away_team})'
        }
        
        print(f"   Previsão: {prediction_map.get(prediction, prediction)}")
        
        # Confidence pode ser dict ou int (stars direto)
        if isinstance(confidence, dict):
            stars = confidence.get('stars', 0)
            level = confidence.get('level', 'N/A')
        else:
            stars = confidence
            level = 'N/A'
        
        print(f"   Confiança: {stars}/5 estrelas ({level})")
        
        # Probabilidades
        home_p = result_value.get('home_probability', 0)
        draw_p = result_value.get('draw_probability', 0)
        away_p = result_value.get('away_probability', 0)
        
        print(f"\n   📊 Probabilidades 1X2:")
        print(f"      Casa: {home_p:.1f}%")
        print(f"      Empate: {draw_p:.1f}%")
        print(f"      Fora: {away_p:.1f}%")
        
        # Expected Goals
        home_xg = result_value.get('home_xg', 0)
        away_xg = result_value.get('away_xg', 0)
        
        print(f"\n   ⚽ Expected Goals (xG):")
        print(f"      {home_team}: {home_xg:.2f}")
        print(f"      {away_team}: {away_xg:.2f}")
        
        # Top Bets
        top_bets = result_value.get('top_bets', [])
        if top_bets:
            print(f"\n   💰 Top 3 Apostas Recomendadas:")
            for i, bet in enumerate(top_bets[:3], 1):
                print(f"      #{i}: {bet.get('market_display', 'N/A')}")
                print(f"          Prob: {bet.get('probability', 0)*100:.1f}% | Odd: {bet.get('market_odd', 0):.2f} | EV: {bet.get('ev_pct', 0):+.1f}%")
        
        # Comparar com resultado real
        if actual_result:
            print(f"\n⚖️  COMPARAÇÃO COM RESULTADO REAL")
            print(f"{'─' * 100}")
            
            is_correct = (prediction == actual_result)
            status_icon = "✅" if is_correct else "❌"
            
            print(f"   Previsão: {prediction_map.get(prediction, prediction)}")
            print(f"   Real: {prediction_map.get(actual_result, actual_result)}")
            print(f"   {status_icon} {'ACERTOU!' if is_correct else 'ERROU'}")
            
            # Verificar probabilidades
            probs = {
                'home': home_p,
                'draw': draw_p,
                'away': away_p
            }
            
            predicted_prob = probs.get(actual_result, 0)
            print(f"\n   📊 Probabilidade atribuída ao resultado real: {predicted_prob:.1f}%")
            
            # Análise de calibração
            if predicted_prob >= 50:
                print(f"   ✅ Sistema tinha alta confiança no resultado correto")
            elif predicted_prob >= 33:
                print(f"   ⚠️  Sistema considerou possível mas não favorito")
            else:
                print(f"   ❌ Sistema subestimou a probabilidade do resultado real")
        
        # Reasoning da IA
        reasoning = result_value.get('reasoning', '')
        if reasoning:
            print(f"\n🤖 EXPLICAÇÃO DA IA")
            print(f"{'─' * 100}")
            # Limitar a 1500 caracteres para não poluir
            print(reasoning[:1500])
            if len(reasoning) > 1500:
                print(f"\n   ... (texto completo tem {len(reasoning)} caracteres)")
        
    except Exception as e:
        print(f"\n❌ Erro ao executar análise: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 100)
    print(f"✅ ANÁLISE COMPLETA FINALIZADA")
    print(f"=" * 100 + "\n")


if __name__ == '__main__':
    # Analisar partida específica
    FIXTURE_ID = 1508602
    analyze_finished_match(FIXTURE_ID)
