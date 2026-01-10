"""
Teste visual da exibição de árbitros
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests

print("\n" + "="*80)
print("🧑‍⚖️ TESTE DE EXIBIÇÃO DE ÁRBITROS")
print("="*80 + "\n")

try:
    response = requests.get('http://localhost:8000/api/matches/api_detail/?id=1391001')
    data = response.json()
    match = data['match']
    
    print("📋 INFORMAÇÕES DA PARTIDA:")
    print(f"   🏠 Casa: {match['home_team']['name']}")
    print(f"   ✈️  Fora: {match['away_team']['name']}")
    print(f"   🏆 Liga: {match['league']['name']}")
    print(f"   🏟️  Estádio: {match['venue']}")
    
    if match.get('referee'):
        referee_full = match['referee']
        referee_name = referee_full.split(',')[0]  # Só o nome
        referee_country = referee_full.split(',')[1].strip() if ',' in referee_full else ''
        
        print(f"\n🧑‍⚖️ ÁRBITRO:")
        print(f"   Nome: {referee_name}")
        if referee_country:
            print(f"   País: {referee_country}")
        print(f"   Nome Completo: {referee_full}")
    else:
        print("\n⚠️  Árbitro não disponível")
    
    # Verificar escalações
    if match.get('lineups'):
        print(f"\n👥 ESCALAÇÕES:")
        for lineup in match['lineups']:
            team_name = lineup['team']['name']
            coach = lineup.get('coach', {}).get('name', 'N/A')
            formation = lineup.get('formation', 'N/A')
            players = len(lineup.get('startXI', []))
            
            print(f"   {team_name}:")
            print(f"      👔 Treinador: {coach}")
            print(f"      📐 Formação: {formation}")
            print(f"      👥 Jogadores: {players}")
    
    print("\n✅ DADOS COMPLETOS DISPONÍVEIS!")
    print("="*80 + "\n")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
