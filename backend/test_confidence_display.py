import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.models import Analysis

print("\n" + "="*80)
print("TESTE: EXIBIÇÃO DE CONFIANÇA NO MODAL")
print("="*80 + "\n")

# Pegar uma análise salva recente
recent_analysis = Analysis.objects.order_by('-created_at').first()

if not recent_analysis:
    print("❌ Nenhuma análise encontrada no banco de dados")
else:
    print(f"✅ Análise encontrada:")
    print(f"   ID: {recent_analysis.id}")
    print(f"   Match: {recent_analysis.match}")
    print(f"   Criada em: {recent_analysis.created_at}")
    
    # Verificar analysis_data
    print(f"\n📊 Estrutura de analysis_data:")
    if recent_analysis.analysis_data:
        print(f"   Keys disponíveis: {list(recent_analysis.analysis_data.keys())}")
        
        # Verificar confidence
        if 'confidence' in recent_analysis.analysis_data:
            confidence = recent_analysis.analysis_data['confidence']
            print(f"\n⭐ CONFIDENCE encontrado:")
            print(f"   {json.dumps(confidence, indent=4)}")
            
            if isinstance(confidence, dict):
                print(f"\n   Stars: {confidence.get('stars', 'N/A')}")
                print(f"   Level: {confidence.get('level', 'N/A')}")
                print(f"   Level PT: {confidence.get('level_pt', 'N/A')}")
                print(f"   Score: {confidence.get('score', 'N/A')}")
        else:
            print(f"\n❌ Confidence NÃO encontrado em analysis_data")
            print(f"   Verificando outros campos possíveis...")
            
            if 'decision' in recent_analysis.analysis_data:
                print(f"   ⚠️ Encontrado 'decision' em analysis_data")
                decision = recent_analysis.analysis_data['decision']
                if isinstance(decision, dict) and 'confidence' in decision:
                    print(f"   ⚠️ Confidence está dentro de 'decision':")
                    print(f"   {json.dumps(decision['confidence'], indent=4)}")
        
        # Verificar consensus
        if 'consensus' in recent_analysis.analysis_data:
            consensus = recent_analysis.analysis_data['consensus']
            print(f"\n📈 CONSENSUS encontrado:")
            print(f"   Casa: {consensus.get('home_win', 'N/A')}")
            print(f"   Empate: {consensus.get('draw', 'N/A')}")
            print(f"   Fora: {consensus.get('away_win', 'N/A')}")
        
        # Verificar top_bets
        if 'top_bets' in recent_analysis.analysis_data:
            top_bets = recent_analysis.analysis_data['top_bets']
            print(f"\n🏆 TOP BETS encontrados: {len(top_bets)}")
    else:
        print("   ❌ analysis_data está vazio")

print("\n" + "="*80 + "\n")
