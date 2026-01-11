import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.ai_analyzer import AIAnalyzer

analyzer = AIAnalyzer()

# Dados de teste simulando decisão dos modelos
decision_data = {
    'recommendation': {
        'market_display': 'Resultado Final',
        'pick': 'Liverpool (Casa)',
        'probability': 0.62,
        'odd': 1.75
    },
    'confidence': {
        'stars': 4,
        'level_pt': 'Alta',
        'score': 0.72
    },
    'risk': 'medium',
    'value_bets': [
        {
            'market_display': 'Liverpool Vence',
            'value_pct': 15.3,
            'fair_odd': 1.61,
            'market_odd': 1.75,
            'stake_suggestion': '3% da banca'
        }
    ],
    'model_probabilities': {
        'consensus': {'home_win': 0.62, 'draw': 0.21, 'away_win': 0.17},
        'poisson': {
            'expected_goals_home': 2.1,
            'expected_goals_away': 1.3,
            'most_likely_score': '2-1',
            'probabilities': {'over_2_5': 0.68, 'btts': 0.72}
        }
    }
}

enriched_data = {
    'fixture_details': {
        'home_team': {'name': 'Liverpool'},
        'away_team': {'name': 'Manchester City'}
    },
    'table_context': {
        'home': {'position': 1, 'points': 45, 'goal_difference': 25, 'form': 'WWDWW', 'home_record': '10V-2E-0D'},
        'away': {'position': 2, 'points': 43, 'goal_difference': 22, 'form': 'WWLWW', 'away_record': '8V-3E-1D'}
    },
    'home_stats': {'goals_per_game_avg': 2.3, 'goals_conceded_avg': 0.8, 'clean_sheets': 8, 'games_played': 20},
    'away_stats': {'goals_per_game_avg': 2.1, 'goals_conceded_avg': 1.0, 'clean_sheets': 6, 'games_played': 20},
    'rest_context': {'home_days_rest': 4, 'away_days_rest': 3, 'advantage': 'equal'},
    'motivation': {'context': 'Top of table clash', 'home': 'very_high', 'away': 'very_high', 'home_reason': 'Líder da liga', 'away_reason': 'Perseguidor direto'},
    'trends': {
        'home': {'games_analyzed': 10, 'over_25_pct': 70, 'btts_pct': 60},
        'away': {'games_analyzed': 10, 'over_25_pct': 65, 'btts_pct': 55}
    },
    'h2h': [],
    'odds': {'home_win': 1.75, 'draw': 3.80, 'away_win': 4.50, 'over_25': 1.50, 'under_25': 2.60}
}

print('🚀 Chamando AI Analyzer com dados completos...')
result = analyzer.explain_decision(decision_data, enriched_data)

print(f"\n{'='*80}")
print('📊 RESULTADO DA ANÁLISE:')
print(f"{'='*80}\n")
print(f"✅ Sucesso: {result['success']}")
if result['success']:
    print(f"⏱️  Tempo: {result.get('generation_time', 0)}s")
    print(f"📝 Tokens: {result.get('tokens_used', 0)}")
    print(f"\n{'─'*80}")
    print('📄 ANÁLISE GERADA:')
    print(f"{'─'*80}\n")
    print(result['analysis'])
else:
    print(f"❌ Erro: {result.get('error')}")
    print(f"🔍 Código: {result.get('error_code')}")
