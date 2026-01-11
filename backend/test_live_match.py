"""
Teste com partida ao vivo: Inter vs Napoli
Verifica se correcoes melhoraram alinhamento com mercado
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

print("\n" + "="*80)
print("TESTE: PARTIDA AO VIVO (Inter vs Napoli)")
print("="*80)

# Buscar partida
match = Match.objects.filter(api_football_id=1378058).first()

if not match:
    print("\nERRO: Partida nao encontrada. Carregando da API...")
    from apps.matches.services.football_api import FootballAPIService
    api = FootballAPIService()
    
    # Carregar partida
    fixture_data = api.get_fixture(1378058)
    if fixture_data:
        print("OK: Dados recebidos da API")
        # Continuar mesmo sem salvar no banco
    else:
        print("ERRO: Nao foi possivel carregar partida")
        sys.exit(1)
else:
    print(f"\nOK: Partida encontrada")
    print(f"   {match.home_team.name} vs {match.away_team.name}")
    print(f"   Status: {match.status}")
    print(f"   Liga: {match.league.name}")

# Executar analise
print(f"\nExecutando analise completa...")
orchestrator = HybridAnalysisOrchestrator()

try:
    result = orchestrator.analyze(1378058)
    
    if not result:
        print("ERRO: Analise retornou None")
        sys.exit(1)
    
    # Extrair dados
    consensus = result.get('model_probabilities', {}).get('consensus', {})
    enriched = result.get('enriched_data', {})
    market_odds = enriched.get('odds', {})
    
    print("\n" + "-"*80)
    print("PROBABILIDADES CALCULADAS:")
    print("-"*80)
    print(f"Casa:   {consensus.get('home_win', 0)*100:.1f}%")
    print(f"Empate: {consensus.get('draw', 0)*100:.1f}%")
    print(f"Fora:   {consensus.get('away_win', 0)*100:.1f}%")
    
    print("\n" + "-"*80)
    print("ODDS DO MERCADO:")
    print("-"*80)
    print(f"Casa:   {market_odds.get('home_win', 'N/A')}")
    print(f"Empate: {market_odds.get('draw', 'N/A')}")
    print(f"Fora:   {market_odds.get('away_win', 'N/A')}")
    
    # Converter odds para probabilidades
    if all(k in market_odds for k in ['home_win', 'draw', 'away_win']):
        prob_home = 1 / market_odds['home_win']
        prob_draw = 1 / market_odds['draw']
        prob_away = 1 / market_odds['away_win']
        total = prob_home + prob_draw + prob_away
        
        # Normalizar (remover margem da casa)
        prob_home_norm = prob_home / total
        prob_draw_norm = prob_draw / total
        prob_away_norm = prob_away / total
        
        print("\n" + "-"*80)
        print("PROBABILIDADES DO MERCADO (normalizadas):")
        print("-"*80)
        print(f"Casa:   {prob_home_norm*100:.1f}%")
        print(f"Empate: {prob_draw_norm*100:.1f}%")
        print(f"Fora:   {prob_away_norm*100:.1f}%")
        
        # Calcular erro absoluto
        erro = (abs(consensus.get('home_win', 0) - prob_home_norm) +
                abs(consensus.get('draw', 0) - prob_draw_norm) +
                abs(consensus.get('away_win', 0) - prob_away_norm))
        
        print("\n" + "-"*80)
        print("COMPARACAO:")
        print("-"*80)
        print(f"Erro total:  {erro*100:.1f} pontos percentuais")
        
        # Vies casa vs fora
        vies_modelo = consensus.get('home_win', 0) - consensus.get('away_win', 0)
        vies_mercado = prob_home_norm - prob_away_norm
        diff_vies = vies_modelo - vies_mercado
        
        print(f"\nVies Casa-Fora:")
        print(f"  Modelo:     {vies_modelo*100:+.1f} pontos")
        print(f"  Mercado:    {vies_mercado*100:+.1f} pontos")
        print(f"  Diferenca:  {diff_vies*100:+.1f} pontos")
        
        print("\n" + "="*80)
        if abs(diff_vies) < 0.05:
            print("RESULTADO: APROVADO")
            print("Vies alinhado com mercado (< 5 pontos)")
        else:
            print("RESULTADO: PRECISA AJUSTE")
            print("Vies ainda desalinhado (>= 5 pontos)")
        print("="*80 + "\n")
    else:
        print("\nAVISO: Odds do mercado incompletas")
        
except Exception as e:
    print(f"\nERRO durante analise: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
