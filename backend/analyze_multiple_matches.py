"""
Análise comparativa de múltiplas partidas do dia 05/02/2026
Para entender por que o sistema errou Over 2.5 em Anderlecht vs Antwerp
mas acertou em outras partidas
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
import requests

# Credenciais da API
API_KEY = "e80d6c82ac7c1d03170757f605d83531"
API_HOST = "v3.football.api-sports.io"

# Partidas para analisar
matches_to_analyze = [
    {
        'name': 'SC Telstar vs Go Ahead Eagles',
        'league': 'KNVB Beker',
        'real_result': '2-1',
        'total_goals': 3,
        'over_25': False,  # 3 gols = exatamente no limite
        'teams': ['Telstar', 'Go Ahead Eagles']
    },
    {
        'name': 'Anderlecht vs Antwerp',
        'fixture_id': 1508602,  # Já sabemos o ID
        'league': 'Beker van Belgie',
        'real_result': '0-1',
        'total_goals': 1,
        'over_25': False,
        'teams': ['Anderlecht', 'Antwerp']
    },
    {
        'name': 'Real Betis vs Atletico Madrid',
        'league': 'Copa Del Rey',
        'real_result': '0-5',
        'total_goals': 5,
        'over_25': True,
        'teams': ['Real Betis', 'Atletico Madrid']
    },
    {
        'name': 'Atalanta vs Juventus',
        'league': 'Coppa Italia',
        'real_result': '3-0',
        'total_goals': 3,
        'over_25': False,  # Exatamente 3 (limite)
        'teams': ['Atalanta', 'Juventus']
    },
    {
        'name': 'Strasbourg vs Monaco',
        'league': 'Coupe de France',
        'real_result': '3-1',
        'total_goals': 4,
        'over_25': True,
        'teams': ['Strasbourg', 'Monaco']
    },
    {
        'name': 'Sporting vs AVS',
        'league': 'Taca de Portugal',
        'real_result': '3-2',
        'total_goals': 5,
        'over_25': True,
        'teams': ['Sporting CP', 'AVS']
    }
]

def search_fixture_by_teams(home_team, away_team, date='2026-02-05'):
    """Buscar fixture ID pelos nomes dos times"""
    url = f"https://{API_HOST}/fixtures"
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    params = {
        'date': date
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        fixtures = data.get('response', [])
        
        for fixture in fixtures:
            teams = fixture.get('teams', {})
            home = teams.get('home', {}).get('name', '')
            away = teams.get('away', {}).get('name', '')
            
            # Busca flexível (contém nome)
            if (home_team.lower() in home.lower() and away_team.lower() in away.lower()):
                return fixture.get('fixture', {}).get('id')
    
    return None

def analyze_match(fixture_id, match_info):
    """Analisa uma partida e retorna resultados"""
    class MockMatch:
        def __init__(self, api_id):
            self.api_football_id = api_id
            self.league = None
    
    try:
        mock = MockMatch(fixture_id)
        orch = HybridAnalysisOrchestrator()
        result = orch.run(mock, strategy='value')
        
        # Extrair dados relevantes
        home_xg = result.get('home_xg', 0)
        away_xg = result.get('away_xg', 0)
        total_xg = home_xg + away_xg
        
        # Buscar probabilidade Over 2.5 nas top bets
        top_bets = result.get('top_bets', [])
        over_25_prob = None
        over_25_recommended = False
        
        for bet in top_bets:
            market = bet.get('market', '')
            if 'over_2_5' in market.lower():
                over_25_prob = bet.get('probability', 0) * 100
                over_25_recommended = True
                break
        
        # Se não está nas top bets, buscar nas probabilidades do Poisson
        if over_25_prob is None:
            model_probs = result.get('model_probabilities', {})
            poisson = model_probs.get('poisson', {})
            poisson_probs = poisson.get('probabilities', {})
            over_25_prob = poisson_probs.get('over_2_5', 0) * 100
        
        return {
            'success': True,
            'home_xg': home_xg,
            'away_xg': away_xg,
            'total_xg': total_xg,
            'over_25_prob': over_25_prob,
            'over_25_recommended': over_25_recommended,
            'top_bets': top_bets[:3]
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Análise comparativa
print("\n" + "="*100)
print("ANALISE COMPARATIVA - PARTIDAS DO DIA 05/02/2026")
print("Foco: Por que sistema errou Over 2.5 em Anderlecht vs Antwerp?")
print("="*100)

results_summary = []

for match in matches_to_analyze:
    print(f"\n{'='*100}")
    print(f"PARTIDA: {match['name']}")
    print(f"Liga: {match['league']}")
    print(f"Resultado Real: {match['real_result']} ({match['total_goals']} gols)")
    print(f"Over 2.5 Real: {'SIM' if match['over_25'] else 'NAO'}")
    print(f"{'='*100}")
    
    # Buscar fixture_id se não tiver
    fixture_id = match.get('fixture_id')
    
    if not fixture_id:
        print(f"Buscando fixture ID...")
        home, away = match['teams']
        fixture_id = search_fixture_by_teams(home, away)
        
        if not fixture_id:
            print(f"ERRO: Nao foi possivel encontrar fixture ID")
            continue
        
        print(f"Fixture ID encontrado: {fixture_id}")
    
    # Analisar
    print(f"\nExecutando analise do sistema...")
    analysis = analyze_match(fixture_id, match)
    
    if not analysis['success']:
        print(f"ERRO na analise: {analysis.get('error')}")
        continue
    
    # Exibir resultados
    print(f"\nRESULTADOS DA ANALISE:")
    print(f"  xG Total Previsto: {analysis['total_xg']:.2f}")
    print(f"  xG Casa: {analysis['home_xg']:.2f}")
    print(f"  xG Fora: {analysis['away_xg']:.2f}")
    print(f"  Prob Over 2.5: {analysis['over_25_prob']:.1f}%")
    print(f"  Over 2.5 recomendado? {'SIM' if analysis['over_25_recommended'] else 'NAO'}")
    
    # Comparação
    total_real = match['total_goals']
    xg_error = abs(analysis['total_xg'] - total_real)
    over_25_correct = (analysis['over_25_prob'] > 50) == match['over_25']
    
    print(f"\nCOMPARACAO:")
    print(f"  Erro xG: {xg_error:.2f} gols")
    print(f"  Previu Over 2.5? {analysis['over_25_prob'] > 50}")
    print(f"  Real Over 2.5? {match['over_25']}")
    print(f"  Acertou? {'SIM' if over_25_correct else 'NAO'}")
    
    # Guardar para resumo
    results_summary.append({
        'name': match['name'],
        'total_real': total_real,
        'total_xg': analysis['total_xg'],
        'xg_error': xg_error,
        'over_25_prob': analysis['over_25_prob'],
        'over_25_real': match['over_25'],
        'correct': over_25_correct
    })

# Resumo final
print(f"\n" + "="*100)
print("RESUMO COMPARATIVO")
print("="*100)

print(f"\n{'Partida':<40} {'Gols':>5} {'xG':>6} {'Erro':>6} {'P(O2.5)':>8} {'Real':>6} {'Acertou':>8}")
print("-"*100)

for r in results_summary:
    acertou = 'SIM' if r['correct'] else 'NAO'
    over_real = 'SIM' if r['over_25_real'] else 'NAO'
    
    print(f"{r['name']:<40} {r['total_real']:>5} {r['total_xg']:>6.2f} {r['xg_error']:>6.2f} {r['over_25_prob']:>7.1f}% {over_real:>6} {acertou:>8}")

# Análise de padrões
print(f"\n" + "="*100)
print("ANALISE DE PADROES")
print("="*100)

# Partidas que erraram
erros = [r for r in results_summary if not r['correct']]
acertos = [r for r in results_summary if r['correct']]

print(f"\nPartidas com ERRO na previsao Over 2.5: {len(erros)}")
for e in erros:
    print(f"  - {e['name']}: Previu {e['total_xg']:.2f} gols, ocorreu {e['total_real']}")

print(f"\nPartidas com ACERTO na previsao Over 2.5: {len(acertos)}")
for a in acertos:
    print(f"  - {a['name']}: Previu {a['total_xg']:.2f} gols, ocorreu {a['total_real']}")

# Estatísticas
if erros:
    avg_error_wrong = sum(e['xg_error'] for e in erros) / len(erros)
    print(f"\nErro medio xG (previsoes erradas): {avg_error_wrong:.2f} gols")

if acertos:
    avg_error_correct = sum(a['xg_error'] for a in acertos) / len(acertos)
    print(f"Erro medio xG (previsoes corretas): {avg_error_correct:.2f} gols")

print(f"\n" + "="*100)
print("CONCLUSAO")
print("="*100)
print("\nO que diferencia Anderlecht vs Antwerp das outras?")
print("  - [ANALISAR FEATURES ESPECIFICAS DESTA PARTIDA]")
print("  - Tipo de competicao (Copa eliminatoria)")
print("  - Momento da temporada")
print("  - Contexto tatico")
