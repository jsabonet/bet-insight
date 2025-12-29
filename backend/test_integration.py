#!/usr/bin/env python
"""
Script para testar integração com APIs de futebol e IA
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.analysis.services.ai_analyzer import AIAnalyzer
from datetime import datetime


def test_football_api():
    """Testar busca de partidas"""
    print("\n⚽ TESTANDO API-FOOTBALL")
    print("=" * 60)
    
    service = FootballAPIService()
    
    # Buscar partidas de hoje
    today = datetime.now().strftime('%Y-%m-%d')
    result = service.get_fixtures_by_date(today)
    
    if result['success']:
        print(f"✅ {result['count']} partidas encontradas para {today}")
        
        # Mostrar primeiras 3 partidas
        for i, fixture in enumerate(result['fixtures'][:3], 1):
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            league = fixture['league']['name']
            time = fixture['fixture']['date']
            
            print(f"\n{i}. {home} vs {away}")
            print(f"   Liga: {league}")
            print(f"   Horário: {time}")
    else:
        print(f"❌ Erro: {result['error']}")


def test_ai_analyzer():
    """Testar análise com IA"""
    print("\n\n🤖 TESTANDO GOOGLE GEMINI AI")
    print("=" * 60)
    
    analyzer = AIAnalyzer()
    
    # Dados de teste
    match_data = {
        'home_team': {'name': 'Manchester United'},
        'away_team': {'name': 'Liverpool'},
        'league': 'Premier League'
    }
    
    print(f"Analisando: {match_data['home_team']['name']} vs {match_data['away_team']['name']}")
    
    result = analyzer.analyze_match(match_data)
    
    if result['success']:
        print(f"\n✅ Análise gerada com sucesso!")
        print(f"Confiança: {result['confidence']}/5 estrelas")
        print(f"\nAnálise:")
        print("-" * 60)
        print(result['analysis'][:500])  # Primeiros 500 caracteres
        print("...")
    else:
        print(f"❌ Erro: {result['error']}")


def test_integration():
    """Testar integração completa"""
    print("\n\n🔗 TESTANDO INTEGRAÇÃO COMPLETA")
    print("=" * 60)
    
    football_api = FootballAPIService()
    ai_analyzer = AIAnalyzer()
    
    # Buscar uma partida
    today = datetime.now().strftime('%Y-%m-%d')
    result = football_api.get_fixtures_by_date(today)
    
    if result['success'] and result['fixtures']:
        # Pegar primeira partida
        fixture = result['fixtures'][0]
        
        home = fixture['teams']['home']['name']
        away = fixture['teams']['away']['name']
        league = fixture['league']['name']
        
        print(f"\n📊 Partida selecionada: {home} vs {away}")
        print(f"Liga: {league}")
        
        # Analisar com IA
        match_data = {
            'home_team': {'name': home},
            'away_team': {'name': away},
            'league': league
        }
        
        print(f"\n🤖 Gerando análise com IA...")
        analysis = ai_analyzer.analyze_match(match_data)
        
        if analysis['success']:
            print(f"✅ Análise completa gerada!")
            print(f"Confiança: {analysis['confidence']}/5 estrelas")
            print(f"\nPrimeiros 300 caracteres:")
            print("-" * 60)
            print(analysis['analysis'][:300])
            print("...")
        else:
            print(f"❌ Erro na análise: {analysis['error']}")
    else:
        print("❌ Nenhuma partida encontrada para hoje")


if __name__ == '__main__':
    print("🚀 TESTE DE INTEGRAÇÕES - BET INSIGHT")
    print("=" * 60)
    
    try:
        test_football_api()
        test_ai_analyzer()
        test_integration()
        
        print("\n\n" + "=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
