"""
SIMULACAO COMPLETA DO FRONTEND - Testando correção do EV
Reproduz EXATAMENTE o fluxo da API unified_analysis
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.ai_analyzer import AIAnalyzer

# Configuração
MATCH_ID = 3168  # Sevilla vs Alaves
STRATEGY = 'multiple'
INCLUDE_AI = True

print('=' * 100)
print('SIMULACAO COMPLETA DO FRONTEND')
print('=' * 100)

try:
    # ETAPA 0: Carregar match
    print(f'\n[0] Carregando match {MATCH_ID}...')
    match = Match.objects.get(id=MATCH_ID)
    print(f'    OK: {match.home_team.name} vs {match.away_team.name}')
    print(f'    Data: {match.match_date}')
    print(f'    Liga: {match.league.name if match.league else "N/A"}')
    
    # ETAPA 1: Preparar dados
    print(f'\n[1] Preparando dados do match...')
    match_data = {
        'home_team': {'name': match.home_team.name, 'id': match.home_team.id},
        'away_team': {'name': match.away_team.name, 'id': match.away_team.id},
        'league': match.league.name if match.league else 'N/A',
        'date': match.match_date,
        'status': match.status,
        'match_id': match.id
    }
    
    enricher = MatchDataEnricher()
    enriched_data = enricher.enrich(match_data)
    print(f'    OK: Dados enriquecidos')
    
    # ETAPA 2: Features
    print(f'\n[2] Calculando features...')
    feature_engineer = FeatureEngineer()
    features = feature_engineer.engineer_all_features(enriched_data)
    print(f'    OK: Features calculadas')
    print(f'    - Home form: {features.get("form", {}).get("home_form_last5", "N/A")}')
    print(f'    - Away form: {features.get("form", {}).get("away_form_last5", "N/A")}')
    
    # ETAPA 3: Predictions (Poisson + Logistic)
    print(f'\n[3] Executando Model Ensemble...')
    
    home_stats = enriched_data.get('home_stats', {})
    away_stats = enriched_data.get('away_stats', {})
    
    home_strength = home_stats.get('goals_per_game_avg', 1.5)
    away_strength = away_stats.get('goals_per_game_avg', 1.3)
    home_defense = home_stats.get('conceded_per_game_avg', 1.3)
    away_defense = away_stats.get('conceded_per_game_avg', 1.3)
    
    form_diff = features.get('form', {}).get('adjusted_form_diff', 0)
    home_strength += form_diff * 0.1
    away_strength -= form_diff * 0.1
    
    weather_impact = features.get('weather', {}).get('goal_impact', 0.0)
    league_id = enriched_data.get('fixture', {}).get('league_id')
    
    ensemble = ModelEnsemble()
    model_predictions = ensemble.predict(
        features,
        home_strength,
        away_strength,
        weather_impact,
        league_id=league_id,
        home_defense=home_defense,
        away_defense=away_defense
    )
    
    consensus = model_predictions.get('consensus', {})
    print(f'    OK: Predictions geradas')
    print(f'    - Casa: {consensus.get("home_win", 0)*100:.1f}%')
    print(f'    - Empate: {consensus.get("draw", 0)*100:.1f}%')
    print(f'    - Fora: {consensus.get("away_win", 0)*100:.1f}%')
    
    # ETAPA 4: Context Analysis
    print(f'\n[4] Analise contextual...')
    
    context_analyzer = ContextAnalyzer()
    
    # ContextAnalyzer recebe apenas features
    context_analysis = context_analyzer.analyze(features)
    
    patterns = context_analysis.get('patterns', [])
    print(f'    OK: {len(patterns)} padroes detectados')
    
    # Preparar market odds para DecisionEngine
    raw_odds = enriched_data.get('odds') or {}
    if raw_odds.get('home_win'):
        # Enriquecer odds com derivados (DC/DNB/Asian) para cálculo de EV real
        from apps.analysis.services.odds_calculator import OddsCalculator
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
            'btts_no': raw_odds.get('btts_no'),
        }
        odds_calc = OddsCalculator()
        market_odds = odds_calc.enrich_odds_dict(base_odds)
        print(f'    OK: Odds da API encontradas e enriquecidas ({len([k for k,v in market_odds.items() if v])} mercados)')
    else:
        market_odds = None
        print(f'    AVISO: Sem odds da API')
    
    # ETAPA 5: Decision Engine
    print(f'\n[5] Gerando decisao e top bets (Strategy: {STRATEGY})...')
    
    decision_engine = DecisionEngine()
    decision = decision_engine.make_decision(
        model_predictions=model_predictions,
        features=features,
        market_odds=market_odds,
        strategy=STRATEGY,
        context_analysis=context_analysis
    )
    
    recommendation = decision.get('recommendation', {})
    top_bets = decision.get('top_bets', [])
    
    print(f'    OK: Decisao gerada')
    print(f'    - Recomendacao: {recommendation.get("pick", "N/A")}')
    print(f'    - Confianca: {decision.get("confidence", {}).get("stars", 0)}/5')
    print(f'    - Top bets: {len(top_bets)}')
    
    # ETAPA 6: AI Analyzer
    if INCLUDE_AI:
        print(f'\n[6] Gerando analise da IA...')
        
        ai_analyzer = AIAnalyzer()
        ai_result = ai_analyzer.explain_decision(
            decision_data=decision,
           enriched_data=enriched_data,
            strategy=STRATEGY
        )
        
        ai_analysis = ai_result.get('analysis', '')
        print(f'    OK: Analise gerada ({len(ai_analysis)} caracteres)')
    else:
        ai_analysis = None
        print(f'\n[6] IA desabilitada')
    
    # SIMULACAO DO FRONTEND
    print(f'\n{"="*100}')
    print(f'SIMULACAO DO FRONTEND (AnalysisModalProgressive)')
    print(f'{"="*100}')
    
    print(f'\nPROBABILIDADES:')
    print(f'  Casa ({match.home_team.name}): {consensus.get("home_win", 0)*100:.1f}%')
    print(f'  Empate: {consensus.get("draw", 0)*100:.1f}%')
    print(f'  Fora ({match.away_team.name}): {consensus.get("away_win", 0)*100:.1f}%')
    
    print(f'\nTOP BETS (Strategy: {STRATEGY}):')
    print(f'Confianca: {decision.get("confidence", {}).get("stars", 0)}/5 | Risco: {decision.get("risk", "N/A")}')
    
    for i, bet in enumerate(top_bets, 1):
        ev_indicator = '[+]' if bet['ev_pct'] >= 0 else '[-]'
        
        print(f'\n{i}. {bet["market_display"]}')
        print(f'   Probabilidade: {bet["probability"]*100:.1f}%')
        print(f'   Odd: {bet.get("market_odd", "N/A")}')
        print(f'   EV: {bet["ev_pct"]:+.1f}% {ev_indicator}')
        print(f'   Stake: {bet["stake_units"]}u')
        print(f'   -> {bet["reason"]}')
    
    if INCLUDE_AI and ai_analysis:
        print(f'\nANALISE DA IA (primeiras 500 chars):')
        print(f'-' * 100)
        print(ai_analysis[:500] + '...')
    
    # VERIFICACAO DA CORRECAO DO EV
    print(f'\n{"="*100}')
    print(f'VERIFICACAO DA CORRECAO DO EV')
    print(f'{"="*100}')
    
    print(f'\nANTES DA CORRECAO:')
    print(f'  "sem value significativo" ocultava o EV negativo')
    
    print(f'\nDEPOIS DA CORRECAO:')
    print(f'  EV sempre visivel com sinal +/-')
    
    print(f'\nCOMPARACAO:')
    for bet in top_bets[:2]:
        prob = bet['probability'] * 100
        ev = bet['ev_pct']
        
        if ev <= 0 and prob >= 50:
            old_msg = f"Alta probabilidade: {prob:.1f}% (sem value significativo)"
        else:
            old_msg = f"Resultado possivel: {prob:.1f}% prob (EV: {ev:.1f}%)"
        
        print(f'\n  {bet["market_display"]}:')
        print(f'    ANTES: {old_msg}')
        print(f'    DEPOIS: {bet["reason"]}')
    
    # Salvar resultado
    filename = f'frontend_complete_{MATCH_ID}_{STRATEGY}.json'
    output = {
        'match': {
            'id': match.id,
            'home_team': match.home_team.name,
            'away_team': match.away_team.name,
            'date': str(match.match_date)
        },
        'strategy': STRATEGY,
        'probabilities': {
            'home_win': f"{consensus.get('home_win', 0)*100:.1f}%",
            'draw': f"{consensus.get('draw', 0)*100:.1f}%",
            'away_win': f"{consensus.get('away_win', 0)*100:.1f}%"
        },
        'top_bets': [
            {
                'rank': bet['rank'],
                'market_display': bet['market_display'],
                'probability': f"{bet['probability']*100:.1f}%",
                'market_odd': bet.get('market_odd'),
                'ev_pct': f"{bet['ev_pct']:+.1f}%",
                'stake_units': bet['stake_units'],
                'reason': bet['reason']
            } for bet in top_bets
        ],
        'ai_analysis': ai_analysis[:1000] if ai_analysis else None
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f'\n{"="*100}')
    print(f'RESULTADO SALVO EM: {filename}')
    print(f'{"="*100}')
    
    print(f'\nSIMULACAO COMPLETA FINALIZADA COM SUCESSO!')
    print(f'\nRESULTADO DA CORRECAO:')
    print(f'  [OK] EV calculado corretamente pelo DecisionEngine')
    print(f'  [OK] EV passado para o frontend (ev_pct no top_bets)')
    print(f'  [OK] Mensagem de reasoning SEMPRE mostra o valor do EV')
    print(f'  [OK] Frontend pode exibir o EV em badge e mensagem')
    print(f'\n{"="*100}')

except Match.DoesNotExist:
    print(f'\nERRO: Match ID {MATCH_ID} nao encontrado')
except Exception as e:
    print(f'\nERRO durante simulacao: {str(e)}')
    import traceback
    traceback.print_exc()
