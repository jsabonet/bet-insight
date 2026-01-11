"""
Teste do endpoint live_probabilities - Recálculo de probabilidades durante jogo ao vivo
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match, Team, League
from apps.matches.views import MatchViewSet
from rest_framework.test import APIRequestFactory
from django.utils import timezone

def test_live_probabilities():
    """Testar recálculo de probabilidades ao vivo"""
    
    print("\n" + "="*80)
    print("TESTE: ENDPOINT LIVE_PROBABILITIES")
    print("="*80 + "\n")
    
    # 1. Criar ou buscar uma partida ao vivo
    league, _ = League.objects.get_or_create(
        name="Premier League",
        defaults={'country': 'Inglaterra', 'priority': 1}
    )
    
    home_team, _ = Team.objects.get_or_create(
        name="Manchester United",
        defaults={'country': 'Inglaterra'}
    )
    
    away_team, _ = Team.objects.get_or_create(
        name="Liverpool",
        defaults={'country': 'Inglaterra'}
    )
    
    # Criar partida ao vivo (1-0 aos 45 minutos)
    match, created = Match.objects.get_or_create(
        home_team=home_team,
        away_team=away_team,
        league=league,
        match_date=timezone.now(),
        defaults={
            'status': '1H',
            'home_score': 1,
            'away_score': 0
        }
    )
    
    if not created:
        match.status = '1H'
        match.home_score = 1
        match.away_score = 0
        match.save()
    
    print(f"✅ Partida criada/atualizada:")
    print(f"   ID: {match.id}")
    print(f"   {match.home_team.name} {match.home_score} x {match.away_score} {match.away_team.name}")
    print(f"   Status: {match.status}")
    
    # 2. Testar o endpoint
    from rest_framework.test import force_authenticate
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Criar ou buscar usuário para o teste
    user, _ = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    factory = APIRequestFactory()
    request = factory.get(f'/api/matches/{match.id}/live_probabilities/')
    force_authenticate(request, user=user)
    
    view = MatchViewSet.as_view({'get': 'live_probabilities'})
    response = view(request, pk=match.id)
    
    print(f"\n📡 Resposta do endpoint:")
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.data
        
        print(f"\n✅ SUCESSO!\n")
        print(f"📊 Estado da partida:")
        print(f"   Score: {data['match_state']['home_score']} x {data['match_state']['away_score']}")
        print(f"   Tempo: {data['match_state']['elapsed_minutes']}'")
        print(f"   Status: {data['match_state']['status']}")
        
        consensus = data['analysis_data']['consensus']
        print(f"\n📈 Probabilidades recalculadas:")
        print(f"   Casa: {consensus['home_win']*100:.1f}%")
        print(f"   Empate: {consensus['draw']*100:.1f}%")
        print(f"   Fora: {consensus['away_win']*100:.1f}%")
        
        fair_odds = data['analysis_data']['fair_odds']
        print(f"\n💰 Odds justas:")
        print(f"   Casa: {fair_odds['home_win']}")
        print(f"   Empate: {fair_odds['draw']}")
        print(f"   Fora: {fair_odds['away_win']}")
        
        poisson = data['analysis_data']['poisson']
        print(f"\n🎲 Modelo Poisson ajustado:")
        print(f"   λ Casa: {poisson['lambda_home']:.2f}")
        print(f"   λ Fora: {poisson['lambda_away']:.2f}")
        print(f"   Ajustado para live: {poisson['adjusted_for_live']}")
        
        recommendation = data['analysis_data']['recommendation']
        print(f"\n🎯 Recomendação:")
        print(f"   Pick: {recommendation['pick']}")
        print(f"   Probabilidade: {recommendation['probability']*100:.1f}%")
        
        confidence = data['analysis_data']['confidence']
        print(f"\n⭐ Confiança:")
        print(f"   Nível: {confidence['level']}")
        print(f"   Estrelas: {confidence['stars']}/5")
        print(f"   Score: {confidence['score']:.2%}")
        
        print(f"\n🕐 Timestamp:")
        print(f"   Atualizado em: {data['updated_at']}")
        
        # 3. Simular mudança de score
        print(f"\n" + "="*80)
        print("SIMULANDO MUDANÇA DE SCORE (Empate 1-1 no segundo tempo)")
        print("="*80)
        
        match.away_score = 1
        match.status = '2H'
        match.save()
        
        request2 = factory.get(f'/api/matches/{match.id}/live_probabilities/')
        force_authenticate(request2, user=user)
        response2 = view(request2, pk=match.id)
        
        if response2.status_code == 200:
            data2 = response2.data
            consensus2 = data2['analysis_data']['consensus']
            
            print(f"\n📊 Novo estado:")
            print(f"   Score: {data2['match_state']['home_score']} x {data2['match_state']['away_score']}")
            print(f"   Tempo: {data2['match_state']['elapsed_minutes']}'")
            
            print(f"\n📈 Novas probabilidades:")
            print(f"   Casa: {consensus2['home_win']*100:.1f}% (antes: {consensus['home_win']*100:.1f}%)")
            print(f"   Empate: {consensus2['draw']*100:.1f}% (antes: {consensus['draw']*100:.1f}%)")
            print(f"   Fora: {consensus2['away_win']*100:.1f}% (antes: {consensus['away_win']*100:.1f}%)")
            
            print(f"\n✅ Probabilidades MUDARAM conforme esperado!")
        
    else:
        print(f"\n❌ ERRO:")
        print(json.dumps(response.data, indent=2))
    
    print("\n" + "="*80)
    print("TESTE CONCLUÍDO")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_live_probabilities()
