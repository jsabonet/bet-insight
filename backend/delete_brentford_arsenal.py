#!/usr/bin/env python
"""
Script para deletar análise antiga de Brentford vs Arsenal
Permite que o sistema recalcule com o código CLEAR_FAVORITE correto
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import Analysis
from apps.matches.models import Match

def delete_analysis():
    """Deleta análise antiga de Brentford vs Arsenal"""
    
    print("\n" + "="*80)
    print("🗑️  DELETAR ANÁLISE ANTIGA - Brentford vs Arsenal")
    print("="*80 + "\n")
    
    # Buscar partida Brentford vs Arsenal
    matches = Match.objects.filter(
        home_team__name__icontains='Brentford',
        away_team__name__icontains='Arsenal'
    ).order_by('-match_date')
    
    if not matches.exists():
        print("❌ Partida Brentford vs Arsenal não encontrada")
        return
    
    match = matches.first()
    print(f"📅 Partida encontrada:")
    print(f"   {match.home_team.name} vs {match.away_team.name}")
    print(f"   Data: {match.match_date}")
    print(f"   Liga: {match.league.name}\n")
    
    # Buscar análises dessa partida
    analyses = Analysis.objects.filter(match=match)
    count = analyses.count()
    
    if count == 0:
        print("✅ Nenhuma análise antiga encontrada")
        print("   Pode criar nova análise direto no frontend!\n")
        return
    
    print(f"🔍 Encontradas {count} análise(s) antiga(s):")
    for analysis in analyses:
        print(f"\n   ID: {analysis.id}")
        print(f"   Usuário: {analysis.user.username}")
        print(f"   Criada: {analysis.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   Probabilidades:")
        print(f"      Brentford: {analysis.home_probability}%")
        print(f"      Empate: {analysis.draw_probability}%")
        print(f"      Arsenal: {analysis.away_probability}%")
    
    print("\n" + "="*80)
    response = input("❓ Deletar todas essas análises? (s/N): ")
    
    if response.lower() != 's':
        print("\n❌ Operação cancelada")
        return
    
    # Deletar análises
    deleted_count = analyses.delete()[0]
    
    print(f"\n✅ {deleted_count} análise(s) deletada(s) com sucesso!")
    print("\n" + "="*80)
    print("🎯 PRÓXIMO PASSO:")
    print("="*80 + "\n")
    print("1. Vá ao frontend")
    print("2. Busque 'Brentford vs Arsenal'")
    print("3. Clique 'Análise Completa'")
    print("4. AGUARDE 30 segundos (calculando...)")
    print("5. Verifique: Arsenal ~57% ✅ (não mais 42.4%)\n")
    print("="*80 + "\n")

if __name__ == '__main__':
    try:
        delete_analysis()
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}\n")
        import traceback
        traceback.print_exc()
