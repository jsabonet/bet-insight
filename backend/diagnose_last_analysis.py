#!/usr/bin/env python
"""Script para verificar última análise e diagnosticar problema."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.models import Analysis

# Buscar última análise (Rayo Vallecano vs Mallorca)
m = Match.objects.filter(api_football_id=1391004).first()

if not m:
    print("❌ Match não encontrado (api_football_id=1391004)")
    exit(1)

print(f"✅ Match encontrado: {m.home_team} vs {m.away_team}")

# Buscar última análise
a = Analysis.objects.filter(match=m).order_by('-created_at').first()

if not a:
    print("❌ Análise não encontrada")
    exit(1)

print(f"\n{'='*80}")
print("📊 REASONING SALVO NO BANCO")
print('='*80)
print(f"Tamanho: {len(a.reasoning) if a.reasoning else 0} caracteres")
print('='*80)
print(a.reasoning if a.reasoning else "NULL")
print('='*80)

# Verificar se é fallback
if a.reasoning:
    if "📌 Mercado:" in a.reasoning and "➡️ DECISÃO:" in a.reasoning:
        if "Fair odd calculada:" in a.reasoning:
            print("\n✅ Resposta DECISÓRIA detectada (formato novo)")
        else:
            print("\n⚠️ Formato incompleto")
    elif "Análise técnica indisponível" in a.reasoning:
        print("\n⚠️ FALLBACK DETECTADO - Gemini não respondeu")
    else:
        print("\n⚠️ Formato desconhecido")
        
    # Verificar se tem as seções esperadas
    has_decision = "➡️ DECISÃO:" in a.reasoning or "DECISÃO:" in a.reasoning
    has_justification = "JUSTIFICATIVA" in a.reasoning
    has_risk = "RISCO" in a.reasoning
    
    print(f"\n📊 Seções presentes:")
    print(f"   {'✅' if has_decision else '❌'} DECISÃO")
    print(f"   {'✅' if has_justification else '❌'} JUSTIFICATIVA")
    print(f"   {'✅' if has_risk else '❌'} RISCO")
else:
    print("\n❌ Reasoning está NULL")
