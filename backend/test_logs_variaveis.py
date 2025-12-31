"""
Script simples para testar logs das novas variáveis
"""
import os
import sys
import django
import logging

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Configurar logging para ver no console
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.matches.models import Match

def test_logs():
    """Testa logs das variáveis"""
    print("\n" + "="*80)
    print("🧪 TESTE DE LOGS DAS VARIÁVEIS")
    print("="*80 + "\n")
    
    # Criar match de teste
    match_data = {
        'api_id': 1035086,
        'home_team': {'name': 'Wolves'},
        'away_team': {'name': 'Liverpool'},
        'league': 'Premier League',
        'season': 2023
    }
    
    # Criar enricher
    enricher = MatchDataEnricher()
    
    # Enriquecer dados (isso vai gerar os logs)
    print("🔄 Iniciando enriquecimento...\n")
    enriched_data = enricher.enrich(match_data)
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO")
    print("="*80)
    
    print("\n📊 RESUMO DOS DADOS ENRIQUECIDOS:")
    print(f"   • rest_context: {bool(enriched_data.get('rest_context'))}")
    print(f"   • motivation: {bool(enriched_data.get('motivation'))}")
    print(f"   • trends: {bool(enriched_data.get('trends'))}")
    
    if enriched_data.get('rest_context'):
        print(f"\n   Rest: {enriched_data['rest_context']}")
    
    if enriched_data.get('motivation'):
        print(f"\n   Motivation: {enriched_data['motivation']}")
    
    if enriched_data.get('trends'):
        print(f"\n   Trends: {enriched_data['trends']}")

if __name__ == '__main__':
    test_logs()
