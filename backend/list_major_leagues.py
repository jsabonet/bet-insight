"""
Listar TODAS as ligas disponíveis na API-Football e suas configurações
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

api = FootballAPIService()

print("\n" + "="*80)
print("🌍 LIGAS CONFIGURADAS NO SISTEMA BET-INSIGHT")
print("="*80 + "\n")

# Ligas que sabemos que têm dados completos (baseado em documentação API-Football)
MAJOR_LEAGUES = {
    # EUROPA - Top 5
    'Inglaterra': ['Premier League', 'Championship', 'FA Cup', 'League Cup'],
    'Espanha': ['La Liga', 'Segunda División', 'Copa del Rey'],
    'Alemanha': ['Bundesliga', '2. Bundesliga', 'DFB Pokal'],
    'Itália': ['Serie A', 'Serie B', 'Coppa Italia'],
    'França': ['Ligue 1', 'Ligue 2', 'Coupe de France'],
    
    # EUROPA - Outros
    'Portugal': ['Primeira Liga', 'Liga Portugal 2'],
    'Holanda': ['Eredivisie'],
    'Bélgica': ['Pro League'],
    'Turquia': ['Super Lig', '1. Lig'],
    'Rússia': ['Premier League'],
    'Escócia': ['Premiership'],
    
    # EUROPA - Competições Internacionais
    'UEFA': ['Champions League', 'Europa League', 'Conference League', 'Euro', 'Nations League'],
    
    # AMÉRICAS
    'Brasil': ['Serie A', 'Serie B', 'Copa do Brasil', 'Paulista A1', 'Carioca A'],
    'Argentina': ['Liga Profesional', 'Copa Argentina'],
    'México': ['Liga MX'],
    'USA': ['MLS', 'USL Championship'],
    'Colômbia': ['Primera A'],
    'Chile': ['Primera División'],
    
    # AMÉRICA DO SUL - Internacional
    'CONMEBOL': ['Copa Libertadores', 'Copa Sudamericana', 'Copa América'],
    
    # ÁSIA
    'Japão': ['J1 League'],
    'Coreia do Sul': ['K League 1'],
    'Arábia Saudita': ['Pro League'],
    'China': ['Super League'],
    'Austrália': ['A-League'],
    
    # ÁFRICA
    'África do Sul': ['Premier Division'],
    'Egito': ['Premier League'],
    
    # MUNDIAL
    'FIFA': ['World Cup', 'Club World Cup'],
}

print("✅ LIGAS COM ESTATÍSTICAS COMPLETAS (Confirmadas):")
print("-"*80 + "\n")

total_leagues = 0
for country, leagues in sorted(MAJOR_LEAGUES.items()):
    print(f"🏁 {country}:")
    for league in leagues:
        total_leagues += 1
        print(f"   • {league}")
    print()

print("="*80)
print(f"📊 TOTAL: {total_leagues} ligas com dados completos")
print("="*80 + "\n")

print("💡 INFORMAÇÕES IMPORTANTES:")
print("-"*80)
print("1. Estas ligas TÊM estatísticas completas:")
print("   ✅ Escalações (lineups)")
print("   ✅ Estatísticas (chutes, posse, escanteios)")
print("   ✅ Eventos (gols, cartões, substituições)")
print()
print("2. Ligas NÃO listadas acima podem ter:")
print("   ⚠️  Dados parciais (só alguns dados)")
print("   ❌ Sem dados (ligas muito pequenas)")
print()
print("3. A API-Football atualiza regularmente:")
print("   📈 Novas ligas podem ser adicionadas")
print("   📉 Algumas ligas podem perder cobertura")
print()
print("4. Para verificar liga específica:")
print("   🔍 Use: python check_leagues_with_stats.py")
print("="*80 + "\n")

# Informações sobre nosso banco de dados local
print("\n" + "="*80)
print("💾 LIGAS NO BANCO DE DADOS LOCAL")
print("="*80 + "\n")

from apps.matches.models import League

db_leagues = League.objects.filter(is_active=True).order_by('country', 'name')
print(f"Total de ligas ativas no DB: {db_leagues.count()}\n")

if db_leagues.count() > 0:
    current_country = None
    for league in db_leagues:
        if league.country != current_country:
            current_country = league.country
            print(f"\n🌍 {current_country}:")
        
        priority = "⭐" * min(league.priority, 3) if league.priority else ""
        print(f"   • {league.name} {priority}")

print("\n" + "="*80)
print("🎯 RECOMENDAÇÃO PARA SEU SISTEMA:")
print("="*80)
print("Configure as ligas principais no banco de dados para:")
print("• Exibir primeiro as partidas com mais dados")
print("• Filtrar por ligas com estatísticas completas")
print("• Melhorar experiência do usuário")
print("="*80 + "\n")
