import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import Analysis
from apps.analysis.serializers import AnalysisSerializer

print("\n" + "="*80)
print("TESTE: SERIALIZAÇÃO DE CONFIDENCE NO MODAL")
print("="*80 + "\n")

# Pegar uma análise salva recente
recent_analysis = Analysis.objects.order_by('-created_at').first()

if not recent_analysis:
    print("❌ Nenhuma análise encontrada no banco de dados")
else:
    print(f"✅ Análise ID {recent_analysis.id} encontrada\n")
    
    # Serializar
    serializer = AnalysisSerializer(recent_analysis)
    data = serializer.data
    
    print("📊 Dados serializados:")
    print(f"   ID: {data['id']}")
    print(f"   Match: {data['match']['home_team']['name']} vs {data['match']['away_team']['name']}")
    print(f"   Confiança (campo direto): {data['confidence']}")
    print(f"   Confiança display: {data['confidence_display']}")
    
    # Verificar analysis_data
    if 'analysis_data' in data and data['analysis_data']:
        print(f"\n📋 Analysis Data:")
        print(f"   Keys disponíveis: {list(data['analysis_data'].keys())}")
        
        if 'confidence' in data['analysis_data']:
            conf = data['analysis_data']['confidence']
            print(f"\n⭐ CONFIDENCE em analysis_data:")
            print(f"   Stars: {conf.get('stars', 'N/A')}")
            print(f"   Level: {conf.get('level', 'N/A')}")
            print(f"   Level PT: {conf.get('level_pt', 'N/A')}")
            print(f"   Score: {conf.get('score', 'N/A')}")
            print(f"\n✅ SUCESSO: Confidence está presente e será exibido no modal!")
        else:
            print(f"\n❌ ERRO: Confidence NÃO está em analysis_data")
    else:
        print(f"\n❌ ERRO: analysis_data está vazio ou não existe")

print("\n" + "="*80 + "\n")
