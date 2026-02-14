"""
Testa chamada unificada da API para match externo
"""
import os
import django
import sys
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from apps.matches.views import AnalyzeMatchUnifiedView
from apps.accounts.models import User

def test_api():
    try:
        print("Iniciando teste...")
        factory = RequestFactory()
        
        # Dados do match externo
        request_data = {
            'api_id': 1520391,
            'strategy': 'value',
            'include_ai': False
        }
        
        print(f"Criando request POST com dados: {request_data}")
        request = factory.post('/api/matches/analyze/', data=json.dumps(request_data), content_type='application/json')
        
        # Simular usuário autenticado (opcional para external match)
        print("Buscando usuário...")
        user = User.objects.first()
        request.user = user if user else None
        print(f"User: {request.user}")
        
        print("Executando view...")
        view = AnalyzeMatchUnifiedView.as_view()
        response = view(request)
        
        print("\n" + "="*100)
        print("RESPOSTA DA API UNIFICADA")
        print("="*100)
        
        data = response.data
        
        print(f"\nStatus: {response.status_code}")
        print(f"Phase: {data.get('phase')}")
        print(f"Is External: {data.get('match_id')} (se 1520391, é externo)")
        
        print("\nSTATISTICAL_DATA:")
        stats = data.get('statistical_data', {})
        consensus = stats.get('consensus', {})
        print(f"   consensus: {consensus}")
        print(f"   Casa: {consensus.get('home_win', 0) * 100:.1f}%")
        print(f"   Empate: {consensus.get('draw', 0) * 100:.1f}%")
        print(f"   Fora: {consensus.get('away_win', 0) * 100:.1f}%")
        
        print("\nDECISION_DATA:")
        decision = data.get('decision_data', {})
        top_bets = decision.get('top_bets', [])
        print(f"   top_bets: {len(top_bets)} apostas")
        for idx, bet in enumerate(top_bets[:3], 1):
            print(f"   {idx}. {bet.get('market_display')} - {bet.get('probability', 0) * 100:.1f}% prob")
        
        print("\n" + "="*100)
    
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_api()
