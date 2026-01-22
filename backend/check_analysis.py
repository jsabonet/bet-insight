#!/usr/bin/env python
"""Script para verificar análises salvas no banco de dados"""
import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Analysis
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*80)
print("🔍 VERIFICAÇÃO DE ANÁLISES SALVAS NO BANCO DE DADOS")
print("="*80 + "\n")

# Buscar análise mais recente
latest_analysis = Analysis.objects.select_related('match', 'user').order_by('-created_at').first()

if not latest_analysis:
    print("❌ Nenhuma análise encontrada no banco de dados")
    sys.exit(0)

print(f"📊 ANÁLISE MAIS RECENTE (ID: {latest_analysis.id})")
print(f"{'─'*80}")
print(f"👤 Usuário: {latest_analysis.user.username}")
print(f"📅 Data: {latest_analysis.created_at}")
print(f"⚽ Partida: {latest_analysis.match.home_team} vs {latest_analysis.match.away_team}")
print(f"🎯 Predição: {latest_analysis.prediction} ({latest_analysis.get_prediction_display()})")
print(f"💪 Confiança: {latest_analysis.confidence} ({latest_analysis.get_confidence_display()})")
print()

print(f"📈 PROBABILIDADES:")
print(f"{'─'*80}")
print(f"   Casa: {latest_analysis.home_probability}%")
print(f"   Empate: {latest_analysis.draw_probability}%")
print(f"   Fora: {latest_analysis.away_probability}%")
print()

print(f"⚽ EXPECTED GOALS (xG):")
print(f"{'─'*80}")
print(f"   Casa xG: {latest_analysis.home_xg}")
print(f"   Fora xG: {latest_analysis.away_xg}")
print()

print(f"📋 ANALYSIS_DATA (decision_data):")
print(f"{'─'*80}")
if latest_analysis.analysis_data:
    print(json.dumps(latest_analysis.analysis_data, indent=2, ensure_ascii=False))
    
    # Verificar campos específicos
    print(f"\n🔍 CAMPOS ESPECÍFICOS:")
    print(f"{'─'*80}")
    
    if 'top_bets' in latest_analysis.analysis_data:
        top_bets = latest_analysis.analysis_data['top_bets']
        print(f"✅ top_bets presente: {len(top_bets)} apostas")
        for i, bet in enumerate(top_bets[:3], 1):
            print(f"   {i}. {bet.get('market', 'N/A')} - {bet.get('outcome', 'N/A')} ({bet.get('probability', 0)*100:.1f}%)")
    else:
        print(f"❌ top_bets NÃO encontrado em analysis_data")
    
    if 'recommendation' in latest_analysis.analysis_data:
        rec = latest_analysis.analysis_data['recommendation']
        print(f"✅ recommendation presente:")
        print(f"   Mercado: {rec.get('market', 'N/A')}")
        print(f"   Resultado: {rec.get('outcome', 'N/A')}")
        print(f"   Probabilidade: {rec.get('probability', 0)*100:.1f}%")
    else:
        print(f"❌ recommendation NÃO encontrado em analysis_data")
    
    if 'risk' in latest_analysis.analysis_data:
        print(f"✅ risk presente: {latest_analysis.analysis_data['risk']}")
    else:
        print(f"❌ risk NÃO encontrado em analysis_data")
else:
    print("❌ analysis_data está vazio ou None")

print()

print(f"💭 REASONING (AI Analysis):")
print(f"{'─'*80}")
if latest_analysis.reasoning:
    print(latest_analysis.reasoning[:500] + "..." if len(latest_analysis.reasoning) > 500 else latest_analysis.reasoning)
else:
    print("❌ reasoning está vazio")

print("\n" + "="*80)
print(f"📊 TOTAL DE ANÁLISES NO BANCO: {Analysis.objects.count()}")
print(f"📊 ANÁLISES DO USUÁRIO {latest_analysis.user.username}: {Analysis.objects.filter(user=latest_analysis.user).count()}")
print("="*80 + "\n")
