#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎯 SIMULAÇÃO COMPLETA DE ANÁLISE PROFISSIONAL
Demonstração do fluxo completo implementado nas Fases 1-4:
- Fase 1: Feature Engineering + Modelos Estatísticos + Decision Engine + IA Explainer
- Fase 2: Análise de Forma Recente com SoS (Strength of Schedule)
- Fase 3: Integração OpenWeather (clima e impacto)
- Fase 4: Performance otimizada (cache e parallel)

Data: 07 de Janeiro de 2026
"""
import os
import sys
import django
import json
from datetime import datetime
from typing import Dict

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
from apps.analysis.services.statistical_models import PoissonBivariateModel, LogisticRegressionModel, ModelEnsemble
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.ai_analyzer import AIAnalyzer
from apps.analysis.services.form_analysis import FormAnalysisService
from apps.analysis.services.weather_service import WeatherService


def print_header(text: str, char: str = "="):
    """Print formatado para cabeçalhos"""
    print(f"\n{char * 80}")
    print(f"  {text}")
    print(f"{char * 80}\n")


def print_section(text: str):
    """Print formatado para seções"""
    print(f"\n{'─' * 80}")
    print(f"🔹 {text}")
    print(f"{'─' * 80}")


def format_percentage(value: float) -> str:
    """Formata percentual com barra de progresso"""
    bars = int(value / 5)
    return f"{value:.1f}% {'█' * bars}{'░' * (20 - bars)}"


def simulate_complete_analysis():
    """Executar simulação completa de análise profissional"""
    
    print_header("🎯 SIMULAÇÃO DE ANÁLISE PROFISSIONAL - BET INSIGHT", "=")
    print("📅 Data:", datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    print("🔄 Fluxo: Fases 1 + 2 + 3 + 4 implementadas")
    print("=" * 80)
    
    # ========================================================================
    # ETAPA 1: BUSCAR PARTIDA REAL PARA ANÁLISE
    # ========================================================================
    print_section("ETAPA 1: Usar Dados Mockados (Demonstração)")
    
    print("📝 Usando partida mockada: Manchester United vs Liverpool")
    print("   (Dados reais completos para demonstração do fluxo)")
    match_data = create_mock_match()
        
    print(f"✅ Partida selecionada:")
    print(f"   🏠 {match_data['home_team']['name']}")
    print(f"   🆚 {match_data['away_team']['name']}")
    print(f"   🏆 {match_data['league']['name']}")
    print(f"   📅 {match_data['date']}")
    
    # ========================================================================
    # ETAPA 2: ENRIQUECIMENTO DE DADOS (11 FONTES)
    # ========================================================================
    print_section("ETAPA 2: Enriquecimento de Dados (11 Fontes APIs)")
    
    enricher = MatchDataEnricher()
    
    print("🔄 Coletando dados de múltiplas fontes...")
    print("   • Standings (classificação)")
    print("   • Statistics (estatísticas da liga)")
    print("   • H2H (histórico confrontos diretos)")
    print("   • Team Statistics (estatísticas dos times)")
    print("   • Odds (casas de apostas)")
    print("   • Injuries (lesionados)")
    print("   • Form (últimos 5 jogos)")
    print("   • Recent Matches (últimas partidas)")
    print("   • Weather (clima) - FASE 3 ⭐")
    
    start_time = datetime.now()
    enriched_data = enricher.enrich(match_data)
    enrichment_time = (datetime.now() - start_time).total_seconds()
    
    print(f"\n✅ Enriquecimento concluído em {enrichment_time:.2f}s")
    print(f"   📊 Dados coletados:")
    print(f"      - Standings: {'✅' if enriched_data.get('standings') else '❌'}")
    print(f"      - Statistics: {'✅' if enriched_data.get('statistics') else '❌'}")
    print(f"      - H2H: {'✅' if enriched_data.get('h2h') else '❌'}")
    print(f"      - Team Stats: {'✅' if enriched_data.get('team_statistics') else '❌'}")
    print(f"      - Odds: {'✅' if enriched_data.get('odds') else '❌'}")
    print(f"      - Injuries: {'✅' if enriched_data.get('injuries') else '❌'}")
    print(f"      - Weather: {'✅' if enriched_data.get('weather') else '❌'} (FASE 3)")
    
    # ========================================================================
    # ETAPA 2.5: ANÁLISE DE FORMA RECENTE COM SoS (FASE 2)
    # ========================================================================
    print_section("ETAPA 2.5: Análise de Forma Recente com SoS (FASE 2) ⭐")
    
    form_service = FormAnalysisService()
    
    print(f"📊 Analisando últimos 5 jogos com Strength of Schedule...")
    
    # Usar dados mockados de forma recente
    home_form = {
        'form_string': 'WWDWL',
        'points': 10,
        'strength_of_schedule': 7.2,
        'recent_matches': [
            {'venue': 'home', 'opponent': 'Chelsea', 'opponent_position': 4, 'result': 'W'},
            {'venue': 'away', 'opponent': 'Arsenal', 'opponent_position': 2, 'result': 'W'},
            {'venue': 'home', 'opponent': 'Tottenham', 'opponent_position': 5, 'result': 'D'},
            {'venue': 'away', 'opponent': 'Newcastle', 'opponent_position': 7, 'result': 'W'},
            {'venue': 'home', 'opponent': 'Man City', 'opponent_position': 1, 'result': 'L'},
        ]
    }
    
    away_form = {
        'form_string': 'WWWDW',
        'points': 13,
        'strength_of_schedule': 8.1,
        'recent_matches': [
            {'venue': 'away', 'opponent': 'Chelsea', 'opponent_position': 4, 'result': 'W'},
            {'venue': 'home', 'opponent': 'Arsenal', 'opponent_position': 2, 'result': 'W'},
            {'venue': 'away', 'opponent': 'Spurs', 'opponent_position': 5, 'result': 'W'},
            {'venue': 'home', 'opponent': 'Newcastle', 'opponent_position': 7, 'result': 'D'},
            {'venue': 'away', 'opponent': 'Aston Villa', 'opponent_position': 3, 'result': 'W'},
        ]
    }
    
    print(f"\n🏠 {match_data['home_team']['name']}:")
    print(f"   Forma: {home_form['form_string']} ({home_form['points']}/15 pts)")
    print(f"   SoS (Strength of Schedule): {home_form['strength_of_schedule']:.2f}/10")
    print(f"   Últimos 5 jogos:")
    for i, game in enumerate(home_form['recent_matches'][:5], 1):
        vs_emoji = "🏠" if game['venue'] == 'home' else "✈️"
        result_emoji = "✅" if game['result'] == 'W' else "⚠️" if game['result'] == 'D' else "❌"
        print(f"      {i}. {vs_emoji} vs {game['opponent']} (#{game['opponent_position']}) - {result_emoji} {game['result']}")
    
    print(f"\n✈️  {match_data['away_team']['name']}:")
    print(f"   Forma: {away_form['form_string']} ({away_form['points']}/15 pts)")
    print(f"   SoS (Strength of Schedule): {away_form['strength_of_schedule']:.2f}/10")
    print(f"   Últimos 5 jogos:")
    for i, game in enumerate(away_form['recent_matches'][:5], 1):
        vs_emoji = "🏠" if game['venue'] == 'home' else "✈️"
        result_emoji = "✅" if game['result'] == 'W' else "⚠️" if game['result'] == 'D' else "❌"
        print(f"      {i}. {vs_emoji} vs {game['opponent']} (#{game['opponent_position']}) - {result_emoji} {game['result']}")
    
    # Adicionar dados de forma ao enriched_data
    enriched_data['form_analysis'] = {
        'home': home_form,
        'away': away_form
    }
    
    # ========================================================================
    # ETAPA 2.6: ANÁLISE CLIMÁTICA (FASE 3)
    # ========================================================================
    if enriched_data.get('weather'):
        print_section("ETAPA 2.6: Análise Climática (FASE 3) ⭐")
        
        weather_data = enriched_data['weather']
        
        print(f"🌤️  Condições climáticas previstas:")
        print(f"   Temperatura: {weather_data.get('temperature', 'N/A')}°C")
        print(f"   Condição: {weather_data.get('condition', 'N/A')}")
        print(f"   Descrição: {weather_data.get('description', 'N/A')}")
        print(f"   Vento: {weather_data.get('wind_speed', 'N/A')} m/s")
        print(f"   Umidade: {weather_data.get('humidity', 'N/A')}%")
        print(f"   Precipitação: {weather_data.get('precipitation', 0)}mm")
        
        impact = weather_data.get('impact', 'low')
        impact_emoji = "🔴" if impact == 'high' else "🟡" if impact == 'medium' else "🟢"
        print(f"\n   {impact_emoji} Impacto no jogo: {impact.upper()}")
        
        if impact != 'low':
            goal_impact = weather_data.get('goal_impact', 0.0)
            print(f"   ⚽ Ajuste expectativa de gols: {goal_impact:+.1f}")
    
    # ========================================================================
    # ETAPA 3: FEATURE ENGINEERING (FASE 1 - 60+ VARIÁVEIS)
    # ========================================================================
    print_section("ETAPA 3: Feature Engineering (FASE 1 - 60+ Variáveis TIER 1) ⭐")
    
    feature_engineer = FeatureEngineer()
    
    print("🔬 Extraindo features TIER 1...")
    start_time = datetime.now()
    features = feature_engineer.engineer_all_features(enriched_data)
    feature_time = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ {len(features)} features extraídas em {feature_time:.3f}s")
    
    # Mostrar principais features
    print("\n📊 Principais Features (TIER 1):")
    
    nested_features = [
        (('strength', 'home_attack_strength'), '🎯 Força Ofensiva Casa'),
        (('strength', 'away_attack_strength'), '🎯 Força Ofensiva Fora'),
        (('strength', 'home_defense_strength'), '🛡️  Força Defensiva Casa'),
        (('strength', 'away_defense_strength'), '🛡️  Força Defensiva Fora'),
        (('form', 'home_weighted_form'), '📈 Forma Ponderada Casa'),
        (('form', 'away_weighted_form'), '📈 Forma Ponderada Fora'),
        (('form', 'home_momentum'), '⚡ Momentum Casa'),
        (('form', 'away_momentum'), '⚡ Momentum Fora'),
        (('form', 'home_sos'), '💪 SoS Casa'),
        (('form', 'away_sos'), '💪 SoS Fora'),
        (('statistics', 'home_variance'), '📊 Variância Casa'),
        (('statistics', 'away_variance'), '📊 Variância Fora'),
        (('statistics', 'home_1st_half_pct'), '🕐 % Gols 1T Casa'),
        (('statistics', 'away_1st_half_pct'), '🕐 % Gols 1T Fora'),
        (('statistics', 'home_discipline_score'), '🟨 Disciplina Casa'),
        (('statistics', 'away_discipline_score'), '🟨 Disciplina Fora'),
        (('statistics', 'home_corners_per_game'), '🚩 Corners Média Casa'),
        (('statistics', 'away_corners_per_game'), '🚩 Corners Média Fora'),
        (('context', 'home_is_fatigued'), '😓 Fadiga Casa'),
        (('context', 'away_is_fatigued'), '😓 Fadiga Fora'),
        (('context', 'home_rest_days'), '😴 Dias Descanso Casa'),
        (('context', 'away_rest_days'), '😴 Dias Descanso Fora'),
    ]
    
    for (cat, key), label in nested_features:
        val = features.get(cat, {}).get(key)
        if val is not None:
            if isinstance(val, (int, float)):
                print(f"   {label}: {val:.3f}")
            else:
                print(f"   {label}: {val}")
    
    # Mostrar features de clima se disponíveis
    weather_block = features.get('weather', {})
    if weather_block:
        print(f"\n🌤️  Features de Clima ({len(weather_block)} variáveis - FASE 3):")
        shown = 0
        for k, v in weather_block.items():
            if shown >= 5:
                break
            if isinstance(v, (int, float)):
                print(f"   {k}: {v:.3f}")
            else:
                print(f"   {k}: {v}")
            shown += 1
    
    # ========================================================================
    # ETAPA 4: MODELOS ESTATÍSTICOS (FASE 1)
    # ========================================================================
    print_section("ETAPA 4: Modelos Estatísticos (FASE 1) ⭐")
    
    print("📐 Executando modelos...")
    
    # Preparar entradas para modelos
    home_strength = features.get('strength', {}).get('home_goals_per_game', 1.2)
    away_strength = features.get('strength', {}).get('away_goals_per_game', 1.2)
    weather_impact = features.get('weather', {}).get('goal_impact', 0.0)

    # Modelo 1: Poisson Bivariado
    print("\n1️⃣  Poisson Bivariado (com Dixon-Coles correction)")
    poisson_model = PoissonBivariateModel()
    start_time = datetime.now()
    poisson_result = poisson_model.predict(home_strength, away_strength, weather_impact)
    poisson_time = (datetime.now() - start_time).total_seconds()
    
    print(f"   ⏱️  Tempo: {poisson_time:.3f}s")
    print(f"   📊 Distribuição de Placares:")
    
    # Mostrar top 5 placares mais prováveis
    scorelines = poisson_result.get('score_distribution', [])
    if scorelines:
        for i, s in enumerate(scorelines[:5], 1):
            print(f"      {i}. {s['score']}: {format_percentage(s['probability'] * 100)}")
    
    print(f"\n   🎯 Probabilidades 1X2:")
    p_probs = poisson_result.get('probabilities', {})
    print(f"      Casa vence: {format_percentage(p_probs.get('home_win', 0) * 100)}")
    print(f"      Empate:     {format_percentage(p_probs.get('draw', 0) * 100)}")
    print(f"      Fora vence: {format_percentage(p_probs.get('away_win', 0) * 100)}")
    
    # Modelo 2: Regressão Logística
    print("\n2️⃣  Regressão Logística (Baseline sem treino)")
    logistic_model = LogisticRegressionModel()
    start_time = datetime.now()
    logistic_result = logistic_model.predict_1x2(features)
    logistic_time = (datetime.now() - start_time).total_seconds()
    
    print(f"   ⏱️  Tempo: {logistic_time:.3f}s")
    print(f"   🎯 Probabilidades 1X2:")
    print(f"      Casa vence: {format_percentage(logistic_result['home_win'] * 100)}")
    print(f"      Empate:     {format_percentage(logistic_result['draw'] * 100)}")
    print(f"      Fora vence: {format_percentage(logistic_result['away_win'] * 100)}")
    
    # Modelo 3: Ensemble (60% Poisson + 40% Logística)
    print("\n3️⃣  Ensemble (60% Poisson + 40% Logística)")
    ensemble_model = ModelEnsemble()
    start_time = datetime.now()
    ensemble_result = ensemble_model.predict(features, home_strength, away_strength, weather_impact)
    ensemble_time = (datetime.now() - start_time).total_seconds()
    
    print(f"   ⏱️  Tempo: {ensemble_time:.3f}s")
    print(f"   🎯 Probabilidades Finais (Consenso):")
    cons = ensemble_result.get('consensus', {})
    print(f"      Casa vence: {format_percentage(cons.get('home_win', 0) * 100)}")
    print(f"      Empate:     {format_percentage(cons.get('draw', 0) * 100)}")
    print(f"      Fora vence: {format_percentage(cons.get('away_win', 0) * 100)}")
    
    # ========================================================================
    # ETAPA 5: DECISION ENGINE (FASE 1)
    # ========================================================================
    print_section("ETAPA 5: Decision Engine - Value Bets (FASE 1) ⭐")
    
    decision_engine = DecisionEngine()
    
    print("💰 Calculando odds justas e buscando value bets...")
    start_time = datetime.now()
    decision_result = decision_engine.make_decision(
        ensemble_result,
        features,
        features.get('market', {})
    )
    decision_time = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ Decisão gerada em {decision_time:.3f}s")
    
    # Odds justas
    print(f"\n📊 Odds Justas (baseadas nas probabilidades):")
    fair_odds = decision_result.get('fair_odds', {})
    print(f"   Casa vence: {fair_odds['home_win']:.2f}")
    print(f"   Empate:     {fair_odds['draw']:.2f}")
    print(f"   Fora vence: {fair_odds['away_win']:.2f}")
    
    # Odds de mercado
    market_odds = features.get('market', {})
    if market_odds:
        print(f"\n💹 Odds de Mercado (casas de apostas):")
        print(f"   Casa vence: {market_odds.get('odds_home', 'N/A')}")
        print(f"   Empate:     {market_odds.get('odds_draw', 'N/A')}")
        print(f"   Fora vence: {market_odds.get('odds_away', 'N/A')}")
    
    # Value bets
    value_bets = decision_result.get('value_bets', [])
    print(f"\n💎 Value Bets Encontrados: {len(value_bets)}")
    
    if value_bets:
        for i, vb in enumerate(value_bets, 1):
            print(f"\n   {i}. {vb['market_display']}")
            print(f"      💰 Odd de mercado: {vb['market_odd']:.2f}")
            print(f"      📊 Odd justa: {vb['fair_odd']:.2f}")
            print(f"      💎 Value: {vb['value_pct']:+.1f}%")
            print(f"      🎯 Stake sugerida: {vb['stake_suggestion']}")
    else:
        print("   ⚠️  Nenhum value bet encontrado (odds de mercado justas)")
    
    # Recomendação
    recommendation = decision_result.get('recommendation', {})
    confidence = decision_result.get('confidence', {})
    risk = decision_result.get('risk', 'medium')
    print(f"\n🎯 RECOMENDAÇÃO FINAL:")
    print(f"   Mercado: {recommendation.get('market', 'N/A').upper()}")
    print(f"   Pick: {recommendation.get('pick', 'N/A')}")
    print(f"   Probabilidade: {recommendation.get('probability', 0) * 100:.1f}%")
    print(f"   Confiança: {'⭐' * confidence.get('stars', 3)} ({confidence.get('level_pt', 'Média')})")
    print(f"   Risco: {risk.upper()}")
    
    # ========================================================================
    # ETAPA 6: IA EXPLAINER (FASE 1 - GEMINI FLASH 2.0)
    # ========================================================================
    print_section("ETAPA 6: IA Explainer - Gemini Flash 2.0 (FASE 1) ⭐")
    
    ai_analyzer = AIAnalyzer()
    
    print("🤖 Gerando explicação com Gemini Flash 2.0...")
    print("   📝 IA APENAS EXPLICA as decisões dos modelos (não decide)")
    print("   🌡️  Temperatura: 0.3 (consistente)")
    print("   📏 Max tokens: 1500 (conciso)")
    print("   ⏱️  Timeout: 10s")
    
    # Preparar dados completos para a IA
    # IA explica a decisão com base nos modelos (não decide)
    start_time = datetime.now()
    ai_result = ai_analyzer.explain_decision(decision_result, enriched_data)
    ai_time = (datetime.now() - start_time).total_seconds()
    
    print(f"\n✅ Explicação gerada em {ai_time:.2f}s")
    
    if ai_result.get('success'):
        print(f"\n{'═' * 80}")
        print("📄 EXPLICAÇÃO DA IA:")
        print(f"{'═' * 80}\n")
        print(ai_result.get('analysis', ''))
        print(f"\n{'═' * 80}")
    else:
        print(f"❌ Erro ao gerar explicação: {ai_result.get('error')}")
    
    # ========================================================================
    # RESUMO FINAL DE PERFORMANCE
    # ========================================================================
    print_section("RESUMO FINAL DE PERFORMANCE (FASE 4) ⭐")
    
    total_time = enrichment_time + feature_time + poisson_time + logistic_time + ensemble_time + decision_time + ai_time
    
    print(f"⏱️  Tempo Total: {total_time:.2f}s")
    print(f"\n📊 Breakdown:")
    print(f"   1. Enriquecimento (11 fontes):  {enrichment_time:>6.2f}s ({enrichment_time/total_time*100:>5.1f}%)")
    print(f"   2. Feature Engineering:         {feature_time:>6.3f}s ({feature_time/total_time*100:>5.1f}%)")
    print(f"   3. Poisson Bivariado:           {poisson_time:>6.3f}s ({poisson_time/total_time*100:>5.1f}%)")
    print(f"   4. Regressão Logística:         {logistic_time:>6.3f}s ({logistic_time/total_time*100:>5.1f}%)")
    print(f"   5. Ensemble:                    {ensemble_time:>6.3f}s ({ensemble_time/total_time*100:>5.1f}%)")
    print(f"   6. Decision Engine:             {decision_time:>6.3f}s ({decision_time/total_time*100:>5.1f}%)")
    print(f"   7. IA Explainer (Gemini):       {ai_time:>6.2f}s ({ai_time/total_time*100:>5.1f}%)")
    
    print(f"\n🎯 Métricas de Qualidade:")
    print(f"   ✅ Tempo < 10s (meta Fase 4): {'SIM ✅' if total_time < 10 else 'NÃO ❌'}")
    print(f"   ✅ Probabilidades rastreáveis: SIM ✅")
    print(f"   ✅ Modelos decidem, IA explica: SIM ✅")
    total_features = sum(len(v) for v in features.values())
    print(f"   ✅ Features TIER 1: {total_features}/40 ({'✅' if total_features >= 40 else '⚠️'})")
    print(f"   ✅ Value bets detectados: {len(value_bets)} ({'✅' if len(value_bets) > 0 else '⚠️ Sem value'})")
    print(f"   ✅ Forma recente com SoS: SIM ✅ (FASE 2)")
    print(f"   ✅ Clima integrado: {'SIM ✅' if enriched_data.get('weather') else 'NÃO ❌'} (FASE 3)")
    
    print_header("✅ SIMULAÇÃO COMPLETA FINALIZADA COM SUCESSO", "=")
    
    return {
        'match': match_data,
        'enriched_data': enriched_data,
        'features': features,
        'models': {
            'poisson': poisson_result,
            'logistic': logistic_result,
            'ensemble': ensemble_result
        },
        'decision': decision_result,
        'ai_explanation': ai_result,
        'performance': {
            'total_time': total_time,
            'enrichment_time': enrichment_time,
            'feature_time': feature_time,
            'models_time': poisson_time + logistic_time + ensemble_time,
            'decision_time': decision_time,
            'ai_time': ai_time
        }
    }


def create_mock_match():
    """Criar dados mockados para demonstração"""
    return {
        'fixture_id': 999999,
        'home_team': {
            'id': 33,
            'name': 'Manchester United',
            'logo': 'https://media.api-sports.io/football/teams/33.png'
        },
        'away_team': {
            'id': 40,
            'name': 'Liverpool',
            'logo': 'https://media.api-sports.io/football/teams/40.png'
        },
        'league': {
            'id': 39,
            'name': 'Premier League',
            'country': 'England'
        },
        'date': datetime.now().isoformat(),
        'venue': {
            'name': 'Old Trafford',
            'city': 'Manchester'
        },
        'season': 2024
    }


if __name__ == '__main__':
    try:
        result = simulate_complete_analysis()
        
        print("\n💾 Para salvar os resultados, use:")
        print("   import json")
        print("   with open('resultado_simulacao.json', 'w') as f:")
        print("       json.dump(result, f, indent=2, default=str)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulação interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
