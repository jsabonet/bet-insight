"""
Script para testar análise diretamente via Django shell (sem HTTP)
"""
import os
import sys
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

def main():
    print("\n" + "="*80)
    print("TESTE DIRETO - SEM HTTP - DJANGO SHELL")
    print("="*80 + "\n")
    
    # Buscar partida
    try:
        match = Match.objects.get(id=3145)
        print(f"OK Partida encontrada: {match.home_team.name} vs {match.away_team.name}")
        print(f"   ID: {match.id}, Liga: {match.league.name}\n")
    except Match.DoesNotExist:
        print("ERRO Partida ID 3145 nao encontrada")
        return
    
    # Executar análise diretamente
    print(">>> Executando HybridAnalysisOrchestrator diretamente...")
    print("="*80 + "\n")
    
    orchestrator = HybridAnalysisOrchestrator()
    result = orchestrator.run(match)
    
    if result:
        print("\n" + "="*80)
        print("RESULTADO DA ANALISE")
        print("="*80)
        print(f"\nPredicao: {result.get('prediction', 'N/A')}")
        print(f"Confianca: {result.get('confidence', 3)}/5")
        print(f"\nPROBABILIDADES:")
        print(f"   Casa: {result.get('home_probability', 0):.1%}")
        print(f"   Empate: {result.get('draw_probability', 0):.1%}")
        print(f"   Fora: {result.get('away_probability', 0):.1%}")
        print(f"\nExpected Goals (xG):")
        print(f"   Casa: {result.get('home_xg', 0):.2f}")
        print(f"   Fora: {result.get('away_xg', 0):.2f}")
        print("\n" + "="*80 + "\n")
    else:
        print("ERRO Analise retornou None")

if __name__ == '__main__':
    main()
