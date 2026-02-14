"""
Script para simular requisição do frontend para análise de partida
Brentford vs Arsenal - Premier League - 12/02/2026
"""
import os
import sys
import io

# Fix encoding para Windows PowerShell
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import django
import requests
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.matches.models import Match, Team, League
from apps.subscriptions.models import Subscription
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

# Configurações
BASE_URL = "http://127.0.0.1:8000/api"
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')
API_FOOTBALL_URL = "https://v3.football.api-sports.io"


def criar_usuario_teste():
    """Criar ou obter usuário de teste"""
    username = "teste_simulacao"
    email = "teste@simulacao.com"
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ Usuário existente: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password="teste123"
        )
        # Criar assinatura premium para ter análises ilimitadas
        Subscription.objects.create(
            user=user,
            plan='yearly',  # Campo necessário
            plan_slug='premium',
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=365),
            amount_paid=4499.00  # Campo obrigatório
        )
        print(f"✅ Usuário criado: {username}")
    
    # Gerar token JWT
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    return user, access_token


def buscar_partida_api():
    """Buscar partida Brentford vs Arsenal da API-Football pelo ID"""
    print("\n🔍 Buscando partida Brentford vs Arsenal na API-Football...")
    
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': API_FOOTBALL_KEY
    }
    
    # Buscar partida específica pelo ID
    FIXTURE_ID = 1379220  # ID real da partida Brentford vs Arsenal
    
    params = {
        'id': FIXTURE_ID
    }
    
    response = requests.get(
        f"{API_FOOTBALL_URL}/fixtures",
        headers=headers,
        params=params,
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"❌ Erro ao buscar partida: {response.status_code}")
        return None
    
    data = response.json()
    fixtures = data.get('response', [])
    
    if fixtures and len(fixtures) > 0:
        fixture = fixtures[0]
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']
        print(f"✅ Partida encontrada: {home_team} vs {away_team}")
        print(f"   ID: {fixture['fixture']['id']}")
        print(f"   Data: {fixture['fixture']['date']}")
        print(f"   Status: {fixture['fixture']['status']['long']}")
        return fixture
    
    print("❌ Partida não encontrada")
    return None


def criar_partida_local(fixture_data):
    """Criar partida no banco de dados local"""
    print("\n📝 Criando/atualizando partida no banco local...")
    
    # Obter ou criar liga
    league_data = fixture_data['league']
    league = League.objects.filter(api_football_id=league_data['id']).first()
    if not league:
        league = League.objects.create(
            api_football_id=league_data['id'],
            name=league_data['name'],
            country=league_data['country'],
            logo=league_data['logo']
        )
    
    # Obter ou criar times
    home_data = fixture_data['teams']['home']
    away_data = fixture_data['teams']['away']
    
    home_team = Team.objects.filter(api_football_id=home_data['id']).first()
    if not home_team:
        home_team = Team.objects.create(
            api_football_id=home_data['id'],
            name=home_data['name'],
            logo=home_data['logo']
        )
    
    away_team = Team.objects.filter(api_football_id=away_data['id']).first()
    if not away_team:
        away_team = Team.objects.create(
            api_football_id=away_data['id'],
            name=away_data['name'],
            logo=away_data['logo']
        )
    
    # Criar partida
    fixture_info = fixture_data['fixture']
    match_date = datetime.fromisoformat(fixture_info['date'].replace('Z', '+00:00'))
    
    match = Match.objects.filter(api_football_id=fixture_info['id']).first()
    if not match:
        match = Match.objects.create(
            api_football_id=fixture_info['id'],
            league=league,
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            status='scheduled'
        )
        print(f"✅ Partida criada: ID {match.id}")
    else:
        print(f"✅ Partida já existe: ID {match.id}")
    
    return match


def analisar_partida_via_api(match_id, access_token):
    """Fazer requisição POST para analisar partida (simulando o frontend)"""
    print(f"\n🎯 Analisando partida ID {match_id} via API...")
    
    url = f"{BASE_URL}/matches/{match_id}/analyze/"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "="*80)
        print("📊 RESULTADO DA ANÁLISE")
        print("="*80)
        print(f"\n🏆 Predição: {data.get('prediction_display', 'N/A')}")
        print(f"⭐ Confiança: {data.get('confidence', 0)}/5")
        print(f"\n📈 PROBABILIDADES:")
        print(f"   • Casa: {data.get('home_probability', 0):.1f}%")
        print(f"   • Empate: {data.get('draw_probability', 0):.1f}%")
        print(f"   • Fora: {data.get('away_probability', 0):.1f}%")
        print(f"\n⚽ Expected Goals (xG):")
        print(f"   • Casa: {data.get('home_xg', 0):.2f}")
        print(f"   • Fora: {data.get('away_xg', 0):.2f}")
        print(f"\n💡 Reasoning:")
        print(f"   {data.get('reasoning', 'N/A')}")
        print(f"\n🔑 Fatores-chave:")
        for factor in data.get('key_factors', []):
            print(f"   • {factor}")
        print("\n" + "="*80)
        
        return data
    else:
        print(f"\n❌ Erro na análise: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None


def main():
    print("="*80)
    print("🎯 SIMULAÇÃO DE REQUISIÇÃO DO FRONTEND")
    print("Partida: Brentford vs Arsenal - Premier League")
    print("="*80)
    
    # 1. Criar usuário e obter token
    user, access_token = criar_usuario_teste()
    
    # 2. Buscar partida na API-Football
    fixture = buscar_partida_api()
    
    if not fixture:
        print("\n⚠️  Partida não encontrada na API. Vou criar uma simulada...")
        # Criar partida simulada para teste
        from apps.matches.models import Match, Team, League
        
        # Usar filter().first() para evitar erro de múltiplos objetos
        league = League.objects.filter(api_football_id=39).first()
        if not league:
            league = League.objects.create(
                api_football_id=39,
                name='Premier League',
                country='England',
                logo='https://media.api-sports.io/football/leagues/39.png'
            )
        
        brentford = Team.objects.filter(api_football_id=55).first()
        if not brentford:
            brentford = Team.objects.create(
                api_football_id=55,
                name='Brentford',
                logo='https://media.api-sports.io/football/teams/55.png'
            )
        
        arsenal = Team.objects.filter(api_football_id=42).first()
        if not arsenal:
            arsenal = Team.objects.create(
                api_football_id=42,
                name='Arsenal',
                logo='https://media.api-sports.io/football/teams/42.png'
            )
        
        # Buscar partida existente ou criar nova
        match = Match.objects.filter(
            home_team=brentford,
            away_team=arsenal,
            league=league
        ).first()
        
        if not match:
            match = Match.objects.create(
                home_team=brentford,
                away_team=arsenal,
                league=league,
                api_football_id=999999,  # ID fictício
                match_date=datetime(2026, 2, 12, 15, 0),
                status='scheduled'
            )
    else:
        # 3. Criar partida no banco local
        match = criar_partida_local(fixture)
    
    print(f"\n📋 Partida a analisar:")
    print(f"   {match.home_team.name} vs {match.away_team.name}")
    print(f"   Liga: {match.league.name}")
    print(f"   Data: {match.match_date}")
    print(f"   ID Local: {match.id}")
    
    # 4. Analisar partida via API REST
    resultado = analisar_partida_via_api(match.id, access_token)
    
    if resultado:
        print("\n✅ Simulação concluída com sucesso!")
    else:
        print("\n❌ Falha na simulação")


if __name__ == '__main__':
    main()
