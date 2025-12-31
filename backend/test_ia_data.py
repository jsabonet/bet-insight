"""
Script de teste para verificar se a IA está recebendo todos os dados da API
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService, FootballDataService
from apps.analysis.services.ai_analyzer import AIAnalyzer
import logging

# Configurar logging para ver todos os detalhes
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def test_ia_with_real_data():
    """Testar IA com dados reais de AMBAS as APIs"""
    
    # IDs de partidas reais para testar (você pode ajustar conforme necessário)
    test_fixture_ids = [
        1035134,  # ID exemplo - ajuste com um ID real do seu from_api
    ]
    
    print("\n" + "="*100)
    print("🧪 TESTE: Verificando se a IA recebe dados de AMBAS as APIs")
    print("="*100 + "\n")
    
    api_service = FootballAPIService()
    fd_service = FootballDataService()
    
    # Primeiro, buscar partidas disponíveis
    print("📥 Buscando partidas disponíveis da API-Football...")
    from datetime import datetime, timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    fixtures_result = api_service.get_fixtures_by_date(today)
    
    if fixtures_result.get('success') and fixtures_result.get('fixtures'):
        print(f"✅ Encontradas {len(fixtures_result['fixtures'])} partidas")
        # Pegar primeira partida
        first_fixture = fixtures_result['fixtures'][0]
        test_fixture_id = first_fixture['fixture']['id']
        print(f"🎯 Usando partida: {first_fixture['teams']['home']['name']} vs {first_fixture['teams']['away']['name']}")
        print(f"   ID (API-Football): {test_fixture_id}")
    else:
        print(f"❌ Nenhuma partida encontrada. Usando ID de teste: {test_fixture_ids[0]}")
        test_fixture_id = test_fixture_ids[0]
    
    print(f"\n{'='*100}")
    print(f"🔍 TESTE 1: Buscar dados da API-FOOTBALL para fixture_id={test_fixture_id}")
    print(f"{'='*100}\n")
    
    # Simular o que o quick_analyze faz
    match_data = {
        'home_team': {'name': 'Time A'},
        'away_team': {'name': 'Time B'},
        'league': 'Liga Teste',
    }
    
    print("📊 DADOS INICIAIS (sem API):")
    print(f"   - home_team: {match_data['home_team']}")
    print(f"   - away_team: {match_data['away_team']}")
    print(f"   - league: {match_data['league']}")
    print(f"   - fixture_details: ❌")
    print(f"   - statistics: ❌")
    print(f"   - predictions: ❌")
    print(f"   - h2h: ❌")
    print(f"   - football_data_match: ❌")
    
    # Buscar fixture details
    print(f"\n📥 [API-Football] Buscando fixture_details...")
    fixture_result = api_service.get_fixture_by_id(test_fixture_id)
    if fixture_result.get('success'):
        match_data['fixture_details'] = fixture_result['fixture']
        print(f"   ✅ Fixture carregado")
        print(f"   📋 Chaves: {list(fixture_result['fixture'].keys())}")
    else:
        print(f"   ❌ Erro: {fixture_result.get('error')}")
    
    # Buscar statistics
    print(f"\n📥 [API-Football] Buscando statistics...")
    stats_result = api_service.get_fixture_statistics(test_fixture_id)
    if stats_result.get('success'):
        match_data['statistics'] = stats_result['statistics']
        print(f"   ✅ Statistics carregadas")
        print(f"   📊 Times: {len(stats_result['statistics'])}")
        if stats_result['statistics']:
            first_team = stats_result['statistics'][0]
            print(f"   📈 Exemplo stats: {[s.get('type') for s in first_team.get('statistics', [])[:5]]}")
    else:
        print(f"   ❌ Erro: {stats_result.get('error')}")
    
    # Buscar predictions
    print(f"\n📥 [API-Football] Buscando predictions...")
    predictions_result = api_service.get_predictions(test_fixture_id)
    if predictions_result.get('success'):
        match_data['predictions'] = predictions_result['predictions']
        print(f"   ✅ Predictions carregadas")
        print(f"   🎲 Chaves: {list(predictions_result['predictions'].keys())[:10]}")
    else:
        print(f"   ❌ Erro: {predictions_result.get('error')}")
    
    # NOVO: Buscar dados do Football-Data.org
    print(f"\n{'='*100}")
    print(f"🔍 TESTE 2: Buscar dados da FOOTBALL-DATA.ORG")
    print(f"{'='*100}\n")
    
    # Buscar partidas disponíveis no Football-Data.org
    print("📥 [Football-Data.org] Buscando partidas disponíveis...")
    fd_matches = fd_service.get_upcoming_matches(days=7)
    
    if fd_matches and 'matches' in fd_matches:
        print(f"✅ Encontradas {len(fd_matches['matches'])} partidas no Football-Data.org")
        if len(fd_matches['matches']) > 0:
            # Pegar primeira partida
            first_match = fd_matches['matches'][0]
            test_fd_id = first_match['id']
            print(f"🎯 Usando partida: {first_match['homeTeam']['name']} vs {first_match['awayTeam']['name']}")
            print(f"   ID (Football-Data): {test_fd_id}")
            
            # Buscar H2H
            print(f"\n📥 [Football-Data.org] Buscando H2H para match_id={test_fd_id}...")
            h2h_data = fd_service.get_h2h(test_fd_id)
            if h2h_data and 'matches' in h2h_data:
                match_data['h2h'] = h2h_data['matches']
                print(f"   ✅ H2H carregado: {len(h2h_data['matches'])} jogos anteriores")
                if h2h_data['matches']:
                    recent = h2h_data['matches'][0]
                    print(f"   📜 Último jogo: {recent['homeTeam']['name']} {recent['score']['fullTime']['home']} x {recent['score']['fullTime']['away']} {recent['awayTeam']['name']}")
            else:
                print(f"   ❌ H2H não disponível")
            
            # Buscar match details
            print(f"\n📥 [Football-Data.org] Buscando match details...")
            match_details = fd_service.get_match_details(test_fd_id)
            if match_details:
                match_data['football_data_match'] = match_details
                print(f"   ✅ Match details carregados")
                print(f"   📋 Chaves: {list(match_details.keys())[:10]}")
            else:
                print(f"   ❌ Match details não disponível")
        else:
            print(f"⚠️  Nenhuma partida futura disponível no Football-Data.org")
    else:
        print(f"❌ Erro ao buscar partidas do Football-Data.org")
    
    print(f"\n{'='*100}")
    print(f"📊 DADOS FINAIS (com AMBAS APIs):")
    print(f"{'='*100}")
    print(f"   API-Football:")
    print(f"     - fixture_details: {'✅' if match_data.get('fixture_details') else '❌'}")
    print(f"     - statistics: {'✅' if match_data.get('statistics') else '❌'}")
    print(f"     - predictions: {'✅' if match_data.get('predictions') else '❌'}")
    print(f"   Football-Data.org:")
    print(f"     - h2h: {'✅' if match_data.get('h2h') else '❌'}")
    print(f"     - football_data_match: {'✅' if match_data.get('football_data_match') else '❌'}")
    
    # Agora testar se a IA recebe tudo isso
    print(f"\n{'='*100}")
    print(f"🤖 TESTE 3: Enviar para a IA")
    print(f"{'='*100}\n")
    
    analyzer = AIAnalyzer()
    
    print("⚠️  ATENÇÃO: Veja os logs abaixo para confirmar que a IA recebeu os dados:")
    print("-"*100)
    
    result = analyzer.analyze_match(match_data)
    
    print("-"*100)
    
    if result.get('success'):
        print(f"\n✅ Análise gerada com sucesso!")
        print(f"⭐ Confiança: {result['confidence']}/5")
        print(f"\n📝 Análise (primeiros 500 caracteres):")
        print(result['analysis'][:500] + "...")
    else:
        print(f"\n❌ Erro na análise: {result.get('error')}")
    
    print(f"\n{'='*100}")
    print(f"✅ TESTE CONCLUÍDO")
    print(f"{'='*100}\n")
    
    print("💡 ANÁLISE DOS RESULTADOS:")
    print("   1. Verifique se AMBAS as APIs retornaram dados")
    print("   2. API-Football: fixture_details, statistics, predictions")
    print("   3. Football-Data.org: h2h (histórico direto), match_details")
    print("   4. Procure por '🔍 DADOS RECEBIDOS PARA ANÁLISE' nos logs da IA")
    print("   5. Se h2h aparecer como ✅, a integração funcionou!")

if __name__ == '__main__':
    test_ia_with_real_data()
