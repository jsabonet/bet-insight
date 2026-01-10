#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎯 TESTE DE ANÁLISE REAL
Demonstra o fluxo completo com partida real da API
"""
import os
import sys
import django
from datetime import datetime

# Configurar UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.form_analysis import FormAnalysisService
from apps.analysis.services.ai_analyzer import AIAnalyzer


def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_section(text):
    print(f"\n{'─'*80}")
    print(f"🔹 {text}")
    print(f"{'─'*80}")


def test_real_analysis():
    """Executar teste com partida real da API"""
    
    print_header("🎯 TESTE DE ANÁLISE REAL - BET INSIGHT")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    # =================================================================
    # ETAPA 1: BUSCAR PARTIDA REAL
    # =================================================================
    print_section("ETAPA 1: Buscar Partida Real da API-Football")
    
    api = FootballAPIService()
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"📡 Buscando partidas para {today}...")
    result = api.get_fixtures_by_date(today)
    
    if not result['success'] or result['count'] == 0:
        print("⚠️  Nenhuma partida hoje. Buscando próximas da Premier League...")
        result = api.get_fixtures_by_league(39, 2024)  # Premier League
    
    if not result['success'] or result['count'] == 0:
        print("❌ Nenhuma partida encontrada.")
        return
    
    # Pegar primeira partida
    fixture = result['fixtures'][0]
    
    match_data = {
        'api_id': fixture['fixture']['id'],
        'home_team': {
            'id': fixture['teams']['home']['id'],
            'name': fixture['teams']['home']['name'],
        },
        'away_team': {
            'id': fixture['teams']['away']['id'],
            'name': fixture['teams']['away']['name'],
        },
        'league': {
            'id': fixture['league']['id'],
            'name': fixture['league']['name'],
        },
        'date': fixture['fixture']['date'],
        'season': 2024
    }
    
    print(f"\n✅ Partida selecionada:")
    print(f"   🏠 {match_data['home_team']['name']}")
    print(f"   🆚 {match_data['away_team']['name']}")
    print(f"   🏆 {match_data['league']['name']}")
    print(f"   📅 {match_data['date']}")
    
    # =================================================================
    # ETAPA 2: ENRIQUECIMENTO DE DADOS
    # =================================================================
    print_section("ETAPA 2: Enriquecimento de Dados (FASE 1-4)")
    
    enricher = MatchDataEnricher()
    
    print("🔄 Coletando dados de múltiplas fontes...")
    print("   • API-Football (standings, stats, H2H)")
    print("   • Football-Data.org (odds)")
    print("   • OpenWeather (clima) - FASE 3 ⭐")
    
    start = datetime.now()
    enriched = enricher.enrich(match_data)
    enrichment_time = (datetime.now() - start).total_seconds()
    
    print(f"\n✅ Enriquecimento concluído em {enrichment_time:.2f}s")
    
    # Verificar dados coletados
    has_standings = bool(enriched.get('standings'))
    has_stats = bool(enriched.get('statistics'))
    has_h2h = bool(enriched.get('h2h', {}).get('matches'))
    has_odds = bool(enriched.get('odds'))
    has_weather = bool(enriched.get('weather'))
    
    print(f"\n📊 Dados obtidos:")
    print(f"   Standings: {'✅' if has_standings else '❌'}")
    print(f"   Statistics: {'✅' if has_stats else '❌'}")
    print(f"   H2H: {'✅' if has_h2h else '❌'}")
    print(f"   Odds: {'✅' if has_odds else '❌'}")
    print(f"   Weather (FASE 3): {'✅' if has_weather else '❌'}")
    
    # =================================================================
    # ETAPA 3: FEATURE ENGINEERING (FASE 1)
    # =================================================================
    print_section("ETAPA 3: Feature Engineering - 60+ Variáveis TIER 1 (FASE 1)")
    
    engineer = FeatureEngineer()
    
    print("🔬 Extraindo features...")
    start = datetime.now()
    features = engineer.engineer_all_features(enriched)
    feature_time = (datetime.now() - start).total_seconds()
    
    print(f"\n✅ {len(features)} features extraídas em {feature_time:.3f}s")
    
    # Mostrar algumas features importantes
    print("\n📊 Principais Features:")
    
    important_features = [
        'offensive_strength_home',
        'defensive_strength_home',
        'offensive_strength_away',
        'defensive_strength_away',
        'form_weighted_home',
        'form_weighted_away',
        'momentum_home',
        'momentum_away',
        'sos_home',  # Fase 2
        'sos_away',  # Fase 2
    ]
    
    for feat in important_features:
        if feat in features:
            val = features[feat]
            if isinstance(val, (int, float)):
                print(f"   {feat}: {val:.3f}")
    
    # Verificar features de clima (Fase 3)
    weather_features = [k for k in features.keys() if 'weather' in k.lower()]
    if weather_features:
        print(f"\n🌤️  Features de Clima (FASE 3): {len(weather_features)} variáveis")
    
    # =================================================================
    # ETAPA 4: ANÁLISE DE FORMA (FASE 2)
    # =================================================================
    print_section("ETAPA 4: Análise de Forma Recente com SoS (FASE 2)")
    
    form_service = FormAnalysisService()
    
    print("📊 Analisando últimos 5 jogos...")
    
    try:
        home_form = form_service.analyze_recent_form(
            match_data['home_team']['id'],
            match_data['league']['id'],
            match_data['season']
        )
        
        away_form = form_service.analyze_recent_form(
            match_data['away_team']['id'],
            match_data['league']['id'],
            match_data['season']
        )
        
        print(f"\n🏠 {match_data['home_team']['name']}:")
        if home_form.get('form_string'):
            print(f"   Forma: {home_form['form_string']} ({home_form.get('points', 0)}/15 pts)")
            print(f"   SoS: {home_form.get('strength_of_schedule', 0):.2f}/10")
        
        print(f"\n✈️  {match_data['away_team']['name']}:")
        if away_form.get('form_string'):
            print(f"   Forma: {away_form['form_string']} ({away_form.get('points', 0)}/15 pts)")
            print(f"   SoS: {away_form.get('strength_of_schedule', 0):.2f}/10")
    
    except Exception as e:
        print(f"⚠️  Análise de forma não disponível: {str(e)}")
    
    # =================================================================
    # ETAPA 5: IA ANALYZER (OPCIONAL)
    # =================================================================
    print_section("ETAPA 5: Análise com IA (FASE 1 - Gemini Flash 2.0)")
    
    analyzer = AIAnalyzer()
    
    print("🤖 Gerando análise com Gemini Flash 2.0...")
    print("   (IA APENAS EXPLICA, não decide)")
    
    try:
        start = datetime.now()
        ai_result = analyzer.analyze_match(enriched)
        ai_time = (datetime.now() - start).total_seconds()
        
        if ai_result['success']:
            print(f"\n✅ Análise gerada em {ai_time:.2f}s\n")
            print("─" * 80)
            print(ai_result.get('analysis', ''))
            print("─" * 80)
        else:
            print(f"❌ Erro: {ai_result.get('error')}")
    
    except Exception as e:
        print(f"⚠️  Análise IA não disponível: {str(e)}")
    
    # =================================================================
    # RESUMO FINAL
    # =================================================================
    print_section("RESUMO FINAL")
    
    total_time = enrichment_time + feature_time
    
    print(f"⏱️  Tempo Total: {total_time:.2f}s")
    print(f"\n📊 Breakdown:")
    print(f"   Enriquecimento: {enrichment_time:.2f}s")
    print(f"   Feature Engineering: {feature_time:.3f}s")
    
    print(f"\n🎯 Métricas:")
    print(f"   ✅ Features extraídas: {len(features)}")
    print(f"   ✅ Tempo < 10s: {'SIM ✅' if total_time < 10 else 'NÃO ❌'}")
    print(f"   ✅ Dados enriquecidos: {'SIM ✅' if has_standings or has_stats else 'PARCIAL ⚠️'}")
    
    print_header("✅ TESTE COMPLETO FINALIZADO")
    
    return {
        'match': match_data,
        'enriched_data': enriched,
        'features': features,
        'performance': {
            'enrichment_time': enrichment_time,
            'feature_time': feature_time,
            'total_time': total_time
        }
    }


if __name__ == '__main__':
    try:
        result = test_real_analysis()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
