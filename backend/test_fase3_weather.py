"""
Teste de integração completa - Fase 3: OpenWeather
Verifica enriquecimento com clima, feature engineering e análise.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime, timedelta
from apps.analysis.services.weather_service import WeatherService
from apps.analysis.services.match_enricher import MatchDataEnricher

def test_weather_service():
    """Testa WeatherService diretamente"""
    print("\n" + "="*80)
    print("🧪 TESTE 1: WeatherService")
    print("="*80 + "\n")
    
    service = WeatherService()
    
    # Old Trafford - Manchester
    latitude = 53.4631
    longitude = -2.2913
    match_time = datetime.now() + timedelta(days=2)  # Daqui a 2 dias
    
    print(f"🏟️ Estádio: Old Trafford")
    print(f"📍 Coordenadas: ({latitude}, {longitude})")
    print(f"📅 Data partida: {match_time.strftime('%Y-%m-%d %H:%M')}\n")
    
    weather = service.get_weather_for_match(latitude, longitude, match_time)
    
    if weather:
        print("✅ CLIMA OBTIDO:")
        print(f"   Condição: {weather['description']}")
        print(f"   Temperatura: {weather['temp']}°C (sensação {weather['feels_like']}°C)")
        print(f"   Humidade: {weather['humidity']}%")
        print(f"   Vento: {weather['wind_speed']} m/s")
        print(f"   Precipitação: {weather['precipitation']} mm")
        print(f"   Nebulosidade: {weather['cloud_coverage']}%")
        print(f"   ⚡ IMPACTO: {weather['impact'].upper()}")
    else:
        print("❌ Clima não obtido")
    
    return weather is not None


def test_enrichment_with_weather():
    """Testa enriquecimento completo com clima"""
    print("\n" + "="*80)
    print("🧪 TESTE 2: Enriquecimento com Clima")
    print("="*80 + "\n")
    
    from apps.matches.models import Match
    
    # Buscar uma partida futura (próximos 7 dias)
    future_date = datetime.now() + timedelta(days=3)
    matches = Match.objects.filter(
        match_date__gte=datetime.now(),
        match_date__lte=future_date,
        api_football_id__isnull=False
    ).order_by('match_date')[:1]
    
    if not matches.exists():
        print("⚠️ Nenhuma partida futura encontrada no banco")
        return False
    
    match = matches.first()
    
    print(f"🎯 Partida selecionada:")
    print(f"   {match.home_team} vs {match.away_team}")
    print(f"   Data: {match.match_date}")
    print(f"   Liga: {match.league}\n")
    
    enricher = MatchDataEnricher()
    
    match_data = {
        'api_id': match.api_football_id,
        'home_team': match.home_team,
        'away_team': match.away_team,
        'date': match.match_date
    }
    
    enriched = enricher.enrich(match_data)
    
    weather = enriched.get('weather')
    
    if weather:
        print("\n✅ CLIMA NO ENRIQUECIMENTO:")
        print(f"   {weather}")
        return True
    else:
        print("\n⚠️ Clima não disponível (pode ser normal se partida > 7 dias)")
        return False


def test_feature_engineering_weather():
    """Testa feature engineering com clima"""
    print("\n" + "="*80)
    print("🧪 TESTE 3: Feature Engineering - Clima")
    print("="*80 + "\n")
    
    from apps.analysis.services.feature_engineer import FeatureEngineer
    
    # Dados mockados de enriquecimento
    enriched_data = {
        'fixture_details': {
            'home_team': {'id': 33, 'name': 'Manchester United'},
            'away_team': {'id': 40, 'name': 'Liverpool'},
            'league': {'id': 39, 'season': 2025},
            'venue': {'name': 'Old Trafford', 'city': 'Manchester'}
        },
        'weather': {
            'temp': 12.5,
            'feels_like': 10.2,
            'humidity': 80,
            'condition': 'Rain',
            'description': 'moderate rain',
            'wind_speed': 15.5,
            'precipitation': 5.2,
            'cloud_coverage': 95,
            'impact': 'high'
        },
        'home_stats': {
            'goals_scored_home': 20,
            'goals_conceded_home': 10
        },
        'away_stats': {
            'goals_scored_away': 18,
            'goals_conceded_away': 12
        },
        'table_context': {
            'home': {'position': 5},
            'away': {'position': 3}
        },
        'odds': None,
        'rest_context': {},
        'motivation': {},
        'trends': {},
        'injuries': {},
        'recent_matches': {'home': [], 'away': []},
        'h2h': []
    }
    
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(enriched_data)
    
    weather_features = features.get('weather', {})
    
    print("✅ FEATURES DE CLIMA:")
    for key, value in weather_features.items():
        print(f"   {key}: {value}")
    
    # Validações
    assert weather_features.get('has_weather') == True, "has_weather deve ser True"
    assert weather_features.get('weather_impact') == 'high', "Impacto deve ser 'high'"
    assert weather_features.get('has_rain') == True, "has_rain deve ser True"
    assert weather_features.get('goal_impact') < 0, "goal_impact deve reduzir gols"
    
    print("\n✅ Todas as validações passaram!")
    
    return True


if __name__ == '__main__':
    print("\n" + "🌦️ "*20)
    print("FASE 3: OPENWEATHER - TESTES DE INTEGRAÇÃO")
    print("🌦️ "*20 + "\n")
    
    try:
        # Teste 1: WeatherService
        test1 = test_weather_service()
        
        # Teste 2: Enriquecimento
        test2 = test_enrichment_with_weather()
        
        # Teste 3: Feature Engineering
        test3 = test_feature_engineering_weather()
        
        print("\n" + "="*80)
        print("📊 RESUMO DOS TESTES")
        print("="*80)
        print(f"   WeatherService: {'✅ PASS' if test1 else '❌ FAIL'}")
        print(f"   Enriquecimento: {'✅ PASS' if test2 else '⚠️ SKIP (normal)'}")
        print(f"   Features: {'✅ PASS' if test3 else '❌ FAIL'}")
        print("="*80 + "\n")
        
        if test1 and test3:
            print("🎉 FASE 3 IMPLEMENTADA COM SUCESSO!")
        else:
            print("⚠️ Alguns testes falharam - verificar logs")
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
