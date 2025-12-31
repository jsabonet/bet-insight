"""
Teste para simular o payload que o frontend envia para quick_analyze
Verificar se todos os dados necessários estão sendo enviados
"""
import os
import django
import sys
import json

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.views import MatchViewSet
from rest_framework.test import APIRequestFactory
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def test_frontend_payload():
    """Simular requisição do frontend para quick_analyze"""
    
    print("\n" + "="*100)
    print("🧪 TESTE: Simulando payload do FRONTEND para quick_analyze")
    print("="*100 + "\n")
    
    # Simular dados que o frontend envia (com TODOS os campos)
    frontend_payload = {
        'home_team': 'Manchester United',
        'away_team': 'Liverpool',
        'league': 'Premier League',
        'date': '2025-12-31T20:00:00Z',
        'status': 'NS',
        'venue': 'Old Trafford',
        'home_score': None,
        'away_score': None,
        'api_id': 1234567,  # ID da API-Football
        'football_data_id': 537970  # ID da Football-Data.org
    }
    
    print("📊 PAYLOAD DO FRONTEND:")
    print("-"*100)
    for key, value in frontend_payload.items():
        status = "✅" if value is not None else "⚠️  NULL"
        print(f"   {status} {key}: {value}")
    print("-"*100)
    
    # Verificar campos obrigatórios
    print("\n🔍 VERIFICAÇÃO DE CAMPOS:")
    required_fields = ['home_team', 'away_team']
    optional_but_important = ['league', 'date', 'status', 'venue', 'api_id', 'football_data_id']
    
    print("\n  Obrigatórios:")
    for field in required_fields:
        has_field = field in frontend_payload and frontend_payload[field] is not None
        print(f"    {'✅' if has_field else '❌'} {field}")
    
    print("\n  Opcionais (mas importantes para análise):")
    for field in optional_but_important:
        has_field = field in frontend_payload and frontend_payload[field] is not None
        print(f"    {'✅' if has_field else '⚠️ '} {field}")
    
    # Criar requisição fake SEM AUTENTICAÇÃO (quick_analyze tem AllowAny)
    print("\n" + "="*100)
    print("🔄 SIMULANDO REQUISIÇÃO PARA O BACKEND...")
    print("="*100 + "\n")
    
    factory = APIRequestFactory()
    django_request = factory.post('/api/matches/quick_analyze/', frontend_payload, format='json')
    
    # Forçar sem autenticação para simular AllowAny
    from django.contrib.auth.models import AnonymousUser
    from rest_framework.request import Request
    django_request.user = AnonymousUser()
    
    # Converter para DRF Request
    request = Request(django_request)
    
    # Criar view diretamente
    from apps.matches.views import MatchViewSet
    view_instance = MatchViewSet()
    view_instance.action = 'quick_analyze'
    view_instance.request = request
    view_instance.format_kwarg = None
    
    print("⚠️  ATENÇÃO: Veja os logs do backend para confirmar recepção dos dados:")
    print("-"*100)
    
    try:
        response = view_instance.quick_analyze(request)
        
        print("-"*100)
        
        print(f"\n📥 RESPOSTA DO BACKEND:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print(f"   ✅ Análise gerada com sucesso!")
            print(f"   ⭐ Confiança: {data.get('confidence', 'N/A')}/5")
            
            # Verificar metadata
            metadata = data.get('metadata', {})
            if metadata:
                print(f"\n   📊 METADATA (dados analisados):")
                print(f"      Previsões API-Football: {'✅' if metadata.get('has_predictions') else '❌'}")
                print(f"      Estatísticas ao vivo: {'✅' if metadata.get('has_statistics') else '❌'}")
                print(f"      H2H (Football-Data): {'✅' if metadata.get('has_h2h') else '❌'}")
                if metadata.get('has_h2h'):
                    print(f"      └─ Jogos H2H: {metadata.get('h2h_count', 0)}")
                print(f"      Detalhes da partida: {'✅' if metadata.get('has_fixture_details') else '❌'}")
            
            # Verificar se a análise menciona dados de H2H
            analysis_text = data.get('analysis', '')
            has_h2h_mention = 'H2H' in analysis_text or 'histórico' in analysis_text.lower() or 'confronto' in analysis_text.lower()
            has_stats_mention = 'estatística' in analysis_text.lower() or 'posse' in analysis_text.lower()
            
            print(f"\n   📝 Análise menciona:")
            print(f"      {'✅' if has_h2h_mention else '❌'} Histórico direto (H2H)")
            print(f"      {'✅' if has_stats_mention else '❌'} Estatísticas dos times")
            
            print(f"\n   📄 Primeiros 500 caracteres da análise:")
            print(f"   {analysis_text[:500]}...")
        else:
            print(f"   ❌ Erro: {response.data}")
    
    except Exception as e:
        print(f"   ❌ ERRO na requisição: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*100)
    print("✅ TESTE CONCLUÍDO")
    print("="*100 + "\n")
    
    print("💡 CONCLUSÃO:")
    print("   ✅ Se viu 'H2H (Football-Data): ✅' nos metadados, tudo OK!")
    print("   ✅ Se a análise mencionar 'histórico' ou 'confrontos', o H2H foi usado")
    print("   ⚠️  Se aparecer '❌', verifique se o football_data_id está sendo enviado")
    
    # Teste sem football_data_id (cenário antigo)
    print("\n\n" + "="*100)
    print("🧪 TESTE 2: Payload SEM football_data_id (cenário antigo)")
    print("="*100 + "\n")
    
    old_payload = frontend_payload.copy()
    old_payload.pop('football_data_id')
    
    print("📊 PAYLOAD ANTIGO (sem Football-Data.org):")
    print("-"*100)
    for key, value in old_payload.items():
        print(f"   {key}: {value}")
    print("-"*100)
    
    request2 = factory.post('/api/matches/quick_analyze/', old_payload, format='json')
    request2.user = None  # Quick_analyze tem permissão AllowAny
    view2 = MatchViewSet.as_view({'post': 'quick_analyze'})
    
    print("\n⚠️  Logs do backend (sem football_data_id):")
    print("-"*100)
    response2 = view2(request2)
    print("-"*100)
    
    print(f"\n📥 RESPOSTA:")
    print(f"   Status: {response2.status_code}")
    if response2.status_code == 200:
        print(f"   Confiança: {response2.data.get('confidence', 'N/A')}/5")
        print(f"   ⚠️  Sem H2H = análise menos precisa")
    
    print("\n" + "="*100)
    print("✅ TESTES CONCLUÍDOS")
    print("="*100)

if __name__ == '__main__':
    test_frontend_payload()
