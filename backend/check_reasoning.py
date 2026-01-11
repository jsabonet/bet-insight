#!/usr/bin/env python
"""Script para verificar o reasoning da última análise."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.models import Analysis

# Buscar match pelo api_football_id dos logs
m = Match.objects.filter(api_football_id=1421815).first()

if not m:
    print("❌ Match não encontrado (api_id=1421815)")
    exit(1)

print(f"✅ Match encontrado: ID {m.id}")

# Buscar análise
a = Analysis.objects.filter(match=m).order_by('-created_at').first()

if not a:
    print("❌ Análise não encontrada")
    exit(1)

print(f"\n{'='*80}")
print("📊 REASONING COMPLETO")
print('='*80)
print(f"Tamanho: {len(a.reasoning) if a.reasoning else 0} caracteres")
print('='*80)
print(a.reasoning if a.reasoning else "NULL")
print('='*80)

# Verificar se é fallback
if a.reasoning and "Análise técnica indisponível" in a.reasoning:
    print("\n⚠️  FALLBACK DETECTADO - Gemini não respondeu a tempo!")
else:
    print("\n✅ Resposta real da IA (não é fallback)")
