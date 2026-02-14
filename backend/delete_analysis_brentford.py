#!/usr/bin/env python
"""Deletar análise de Brentford vs Arsenal"""
import os, sys, django

sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import Analysis
from apps.matches.models import Match

print("\n" + "="*80)
print("🗑️  DELETANDO ANÁLISE - Brentford vs Arsenal")
print("="*80 + "\n")

# Buscar partida
matches = Match.objects.filter(
    home_team__name__icontains='Brentford',
    away_team__name__icontains='Arsenal'
)

if not matches.exists():
    print("❌ Partida não encontrada")
    sys.exit(1)

match = matches.first()
print(f"✅ Partida: {match.home_team.name} vs {match.away_team.name}")
print(f"   Data: {match.match_date}")
print(f"   Liga: {match.league.name}\n")

# Buscar análises
analyses = Analysis.objects.filter(match=match)
count = analyses.count()

print(f"📊 Análises encontradas: {count}")

if count == 0:
    print("\n✅ Nenhuma análise para deletar")
    print("   Próxima análise será calculada do zero!\n")
    print("="*80 + "\n")
    sys.exit(0)

# Mostrar detalhes
for analysis in analyses:
    print(f"\n   ID: {analysis.id}")
    print(f"   Usuário: {analysis.user.username}")
    print(f"   Criada: {analysis.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   Arsenal: {analysis.away_probability}%")

# Deletar
deleted_count, _ = analyses.delete()

print(f"\n✅ {deleted_count} análise(s) deletada(s)!\n")
print("="*80)
print("PRÓXIMA ANÁLISE:")
print("="*80 + "\n")
print("Será RECALCULADA com código CLEAR_FAVORITE")
print("Arsenal deve mostrar ~57% (não mais 42.4%)\n")
print("="*80 + "\n")
