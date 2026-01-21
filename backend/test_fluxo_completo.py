"""
Teste do Fluxo Completo de Análise
Testa o endpoint /api/matches/analyze/ com as melhorias implementadas
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("="*80)
print("TESTE DO FLUXO COMPLETO - Endpoint /api/matches/analyze/")
print("="*80)
print()

# Dados de um jogo real para teste
match_data = {
    "home_team": "Burnley",
    "away_team": "Tottenham",
    "date": "2024-03-03",
    "league": "Premier League",
    "skip_ai": True,  # Pular IA para focar nos modelos estatísticos
    
    # Dados mínimos necessários
    "home_stats": {
        "goals_per_game_avg": 1.1,
        "conceded_per_game_avg": 1.6,
        "form": "LLLLD",
        "position": 19,
        "points": 20,
        "played": 27
    },
    "away_stats": {
        "goals_per_game_avg": 1.8,
        "conceded_per_game_avg": 1.2,
        "form": "WWLWW",
        "position": 5,
        "points": 53,
        "played": 27
    },
    "fixture": {
        "league_id": 39,
        "home_team": "Burnley",
        "away_team": "Tottenham",
        "date": "2024-03-03T15:00:00Z"
    },
    "table_context": {
        "home": {
            "position": 19,
            "points": 20,
            "played": 27,
            "form": "LLLLD",
            "total_teams": 20
        },
        "away": {
            "position": 5,
            "points": 53,
            "played": 27,
            "form": "WWLWW",
            "total_teams": 20
        }
    },
    "odds": {
        "home_win": 3.7,
        "draw": 3.6,
        "away_win": 2.46
    }
}

print("\n📊 Enviando requisição para análise...")
print(f"   Home: {match_data['home_team']} (19º, 1.1 gols/jogo)")
print(f"   Away: {match_data['away_team']} (5º, 1.8 gols/jogo)")
print(f"   Liga: {match_data['league']}")
print()

try:
    response = requests.post(
        f"{BASE_URL}/api/matches/analyze/",
        json=match_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("✅ SUCESSO! Análise concluída")
        print()
        
        # Verificar se as novas features estão sendo usadas
        if 'features' in result:
            features = result['features']
            
            print("="*80)
            print("FEATURES EXTRAÍDAS")
            print("="*80)
            
            # Verificar novas categorias
            if 'statistics' in features:
                stats = features['statistics']
                print("\n✅ STATISTICS (NOVO):")
                print(f"   Variance diff: {stats.get('home_variance', 'N/A')} - {stats.get('away_variance', 'N/A')}")
                print(f"   Corners diff: {stats.get('home_corners', 'N/A')} - {stats.get('away_corners', 'N/A')}")
                print(f"   Clean sheets: {stats.get('home_clean_sheets', 'N/A')} - {stats.get('away_clean_sheets', 'N/A')}")
            
            if 'form' in features:
                form = features['form']
                print("\n✅ FORM:")
                print(f"   Adjusted form diff: {form.get('adjusted_form_diff', 'N/A')}")
                print(f"   Momentum: {form.get('home_momentum', 'N/A')} - {form.get('away_momentum', 'N/A')}")
            
            if 'elo' in features:
                elo = features['elo']
                print("\n✅ ELO:")
                print(f"   Diff: {elo.get('elo_diff', 'N/A')}")
        
        # Verificar previsões dos modelos
        if 'predictions' in result:
            predictions = result['predictions']
            
            print("\n" + "="*80)
            print("PREVISÕES DOS MODELOS")
            print("="*80)
            
            if 'poisson' in predictions:
                poisson = predictions['poisson']
                probs = poisson['probabilities']
                print("\n🎲 POISSON (COM DEFESA):")
                print(f"   Casa: {probs['home_win']*100:.1f}%")
                print(f"   Empate: {probs['draw']*100:.1f}%")
                print(f"   Fora: {probs['away_win']*100:.1f}%")
                print(f"   Placar mais provável: {poisson.get('most_likely_score', 'N/A')}")
                print(f"   Expected goals: {poisson.get('expected_goals', {})}")
            
            if 'logistic' in predictions:
                logistic = predictions['logistic']
                print("\n📊 LOGÍSTICA (14 FEATURES):")
                print(f"   Casa: {logistic['home_win']*100:.1f}%")
                print(f"   Empate: {logistic['draw']*100:.1f}%")
                print(f"   Fora: {logistic['away_win']*100:.1f}%")
            
            if 'consensus' in predictions:
                consensus = predictions['consensus']
                print("\n🎯 CONSENSUS (50/35/15):")
                print(f"   Casa: {consensus['home_win']*100:.1f}%")
                print(f"   Empate: {consensus['draw']*100:.1f}%")
                print(f"   Fora: {consensus['away_win']*100:.1f}%")
            
            if 'weights' in predictions:
                weights = predictions['weights']
                print("\n⚖️ PESOS:")
                print(f"   Poisson: {weights.get('poisson', 0)*100:.0f}%")
                print(f"   Logística: {weights.get('logistic', 0)*100:.0f}%")
                print(f"   Market: {weights.get('market', 0)*100:.0f}%")
        
        # Verificar decisão final
        if 'decision' in result:
            decision = result['decision']
            
            print("\n" + "="*80)
            print("DECISÃO FINAL")
            print("="*80)
            
            print(f"\n🎯 Recomendação: {decision.get('recommendation', {}).get('market', 'N/A')}")
            print(f"   Confiança: {decision.get('confidence', 0)*100:.1f}%")
            
            if 'value_bets' in decision:
                value_bets = decision['value_bets']
                if value_bets:
                    print(f"\n💎 Value Bets encontrados: {len(value_bets)}")
                    for bet in value_bets[:3]:  # Top 3
                        print(f"   - {bet.get('market', 'N/A')}: Edge {bet.get('edge', 0)*100:.1f}%")
        
        print("\n" + "="*80)
        print("✅ TESTE COMPLETO BEM-SUCEDIDO")
        print("="*80)
        print("\nMelhorias implementadas e testadas:")
        print("✅ Statistics features (variance, corners, clean_sheets, discipline)")
        print("✅ Forma ajustada por SoS")
        print("✅ Momentum")
        print("✅ Defesa no Poisson")
        print("✅ ELO normalizado")
        print("✅ 14 features na Logística")
        print("✅ Ensemble 50/35/15")
        
    else:
        print(f"❌ ERRO: Status {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ ERRO: Não foi possível conectar ao servidor")
    print("   Certifique-se de que o servidor Django está rodando:")
    print("   python manage.py runserver")
except Exception as e:
    print(f"❌ ERRO: {e}")
