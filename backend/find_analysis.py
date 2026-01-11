import os, sys, django, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.models import Analysis

# Buscar análise recente com odds
a = Analysis.objects.select_related('match').filter(
    match__api_football_id__isnull=False,
    home_probability__gt=0
).order_by('-created_at').first()

if a:
    m = a.match
    data = json.loads(a.analysis_data) if isinstance(a.analysis_data, str) else a.analysis_data
    odds = data.get('market_odds', {})
    
    print(f"\nFixture: {m.api_football_id}")
    print(f"Partida: {m.home_team} vs {m.away_team}")
    print(f"\nConsenso Modelo:")
    print(f"  Casa: {a.home_probability*100:.1f}%")
    print(f"  Empate: {a.draw_probability*100:.1f}%")
    print(f"  Fora: {a.away_probability*100:.1f}%")
    print(f"\nOdds Mercado:")
    print(f"  Casa: {odds.get('home_win', 'N/A')}")
    print(f"  Empate: {odds.get('draw', 'N/A')}")
    print(f"  Fora: {odds.get('away_win', 'N/A')}")
    
    if all(k in odds for k in ['home_win', 'draw', 'away_win']):
        # Normalizar odds para comparar
        p_h = 1/odds['home_win']
        p_d = 1/odds['draw']
        p_a = 1/odds['away_win']
        total = p_h + p_d + p_a
        
        print(f"\nMercado Normalizado:")
        print(f"  Casa: {(p_h/total)*100:.1f}%")
        print(f"  Empate: {(p_d/total)*100:.1f}%")
        print(f"  Fora: {(p_a/total)*100:.1f}%")
        
        # Calcular erro
        erro = abs(a.home_probability - p_h/total) + abs(a.draw_probability - p_d/total) + abs(a.away_probability - p_a/total)
        print(f"\nERRO TOTAL: {erro*100:.1f} pontos")
        
        # Viés casa/fora
        vies_modelo = a.home_probability - a.away_probability
        vies_mercado = (p_h/total) - (p_a/total)
        diff = vies_modelo - vies_mercado
        
        print(f"\nVIÉS (Casa - Fora):")
        print(f"  Modelo: {vies_modelo*100:+.1f}pp")
        print(f"  Mercado: {vies_mercado*100:+.1f}pp")
        print(f"  Diferença: {diff*100:+.1f}pp")
        
        if abs(diff) < 0.05:
            print("\n✅ APROVADO: Viés < 5pp")
        else:
            print(f"\n❌ PRECISA AJUSTE: Viés de {abs(diff)*100:.1f}pp")
else:
    print("Nenhuma análise encontrada")
