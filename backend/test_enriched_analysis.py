"""
✅ TESTE COMPLETO: Sistema de Enriquecimento de Dados
Valida que TODAS as variáveis contextuais estão sendo coletadas e usadas
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_enriched_analysis():
    """Testa análise com dados enriquecidos"""
    
    print("\n" + "="*100)
    print("🧪 TESTE COMPLETO: Sistema de Enriquecimento de Dados")
    print("="*100 + "\n")
    
    # Importar após setup do Django
    from apps.analysis.services.match_enricher import MatchDataEnricher
    from apps.analysis.services.api_football_service import APIFootballService
    
    # Dados de teste (partida real da Premier League)
    test_match = {
        'home_team': {'name': 'Manchester City'},
        'away_team': {'name': 'Arsenal'},
        'league': 'Premier League',
        'date': '2026-01-01T15:00:00+00:00',
        'status': 'NS',
        'venue': 'Etihad Stadium',
        'home_score': None,
        'away_score': None,
        'api_id': 1035086  # ID real de uma partida Premier League
    }
    
    print("📊 MATCH DATA ORIGINAL:")
    print("-"*100)
    for key, value in test_match.items():
        print(f"   {key}: {value}")
    print("-"*100 + "\n")
    
    # ETAPA 1: Testar API Football Service
    print("\n" + "="*100)
    print("🔬 ETAPA 1: Testando API Football Service")
    print("="*100 + "\n")
    
    api_service = APIFootballService()
    
    print("📥 1.1 - Testando fetch_fixture_details...")
    try:
        fixture = api_service.fetch_fixture_details(test_match['api_id'])
        if fixture:
            print(f"   ✅ Sucesso! Fixture: {fixture['home_team']['name']} vs {fixture['away_team']['name']}")
            print(f"   📍 Liga: {fixture['league']['name']} ({fixture['league']['season']})")
            print(f"   🏟️ Estádio: {fixture['venue']}")
        else:
            print(f"   ⚠️ Fixture não encontrado")
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    # ETAPA 2: Testar Enricher
    print("\n" + "="*100)
    print("🔬 ETAPA 2: Testando Match Data Enricher")
    print("="*100 + "\n")
    
    enricher = MatchDataEnricher()
    
    print("🔄 Enriquecendo dados da partida...")
    print("-"*100)
    
    try:
        enriched_data = enricher.enrich(test_match)
        
        print("\n✅ ENRIQUECIMENTO CONCLUÍDO!")
        print("="*100)
        
        # Verificar campos enriquecidos
        enriched_fields = [
            'fixture_details',
            'table_context',
            'injuries',
            'odds',
            'home_stats',
            'away_stats',
            'rest_context',
            'motivation',
            'trends',
            'season_context'
        ]
        
        print("\n📋 CHECKLIST DE CAMPOS ENRIQUECIDOS:")
        print("-"*100)
        
        for field in enriched_fields:
            has_field = field in enriched_data and enriched_data[field] is not None
            status = "✅" if has_field else "❌"
            print(f"   {status} {field}")
            
            # Mostrar detalhes se disponível
            if has_field:
                data = enriched_data[field]
                if field == 'table_context':
                    home = data.get('home', {})
                    away = data.get('away', {})
                    if home.get('position'):
                        print(f"      └─ Casa: {home.get('position')}º lugar, {home.get('points')} pts")
                    if away.get('position'):
                        print(f"      └─ Fora: {away.get('position')}º lugar, {away.get('points')} pts")
                
                elif field == 'injuries':
                    home_count = len(data.get('home', []))
                    away_count = len(data.get('away', []))
                    print(f"      └─ {home_count} lesões (casa), {away_count} (fora)")
                
                elif field == 'odds':
                    print(f"      └─ Casa: {data.get('home_win', 'N/A')} | "
                         f"Empate: {data.get('draw', 'N/A')} | "
                         f"Fora: {data.get('away_win', 'N/A')}")
                
                elif field == 'home_stats' and data:
                    print(f"      └─ {data.get('games_played', 0)} jogos, "
                         f"{data.get('goals_per_game_avg', 0):.2f} gols/jogo")
                
                elif field == 'season_context':
                    print(f"      └─ {data.get('season')} - {data.get('round')}")
        
        print("-"*100)
        
        # ETAPA 3: Resumo de Impacto
        print("\n" + "="*100)
        print("📊 RESUMO DO IMPACTO NO SISTEMA")
        print("="*100 + "\n")
        
        impact_score = 0
        max_score = len(enriched_fields)
        
        for field in enriched_fields:
            if field in enriched_data and enriched_data[field] is not None:
                impact_score += 1
        
        percentage = (impact_score / max_score) * 100
        
        print(f"🎯 Taxa de Enriquecimento: {impact_score}/{max_score} campos ({percentage:.1f}%)")
        print(f"\n📈 Análise de Impacto:")
        
        if percentage >= 80:
            print(f"   ✅ EXCELENTE! Dados altamente enriquecidos.")
            print(f"   👉 A IA terá contexto completo para gerar análises precisas.")
        elif percentage >= 60:
            print(f"   ⚠️ BOM! Maioria dos dados disponíveis.")
            print(f"   👉 Análises serão confiáveis, mas podem faltar alguns detalhes.")
        elif percentage >= 40:
            print(f"   ⚠️ MODERADO! Alguns dados importantes faltando.")
            print(f"   👉 Análises funcionarão, mas com menor precisão.")
        else:
            print(f"   ❌ BAIXO! Muitos dados essenciais faltando.")
            print(f"   👉 Considere verificar configuração das APIs.")
        
        print("\n💡 VARIÁVEIS IMPLEMENTADAS (vs proposta original):")
        print("-"*100)
        variables = [
            ("Posição na tabela", "table_context"),
            ("Lesões e suspensões", "injuries"),
            ("Odds das casas de apostas", "odds"),
            ("Estatísticas detalhadas", "home_stats/away_stats"),
            ("Contexto da temporada", "season_context"),
            ("Descanso entre jogos", "rest_context"),
            ("Motivação do time", "motivation"),
            ("Tendências (Over/Under)", "trends")
        ]
        
        for var_name, var_key in variables:
            # Verificar se o campo existe (alguns são compostos)
            if '/' in var_key:
                keys = var_key.split('/')
                has_var = any(k in enriched_data and enriched_data[k] for k in keys)
            else:
                has_var = var_key in enriched_data and enriched_data[var_key] is not None
            
            status = "✅ IMPLEMENTADO" if has_var else "⚠️  PENDENTE"
            print(f"   {status} {var_name}")
        
        print("-"*100)
        
        # ETAPA 4: Teste de Integração com IA
        print("\n" + "="*100)
        print("🤖 ETAPA 3: Testando Integração com IA Analyzer")
        print("="*100 + "\n")
        
        from apps.analysis.services.ai_analyzer import AIAnalyzer
        
        analyzer = AIAnalyzer()
        
        print("🔄 Gerando análise com dados enriquecidos...")
        print("-"*100 + "\n")
        
        result = analyzer.analyze_match(enriched_data)
        
        if result.get('success'):
            print("✅ ANÁLISE GERADA COM SUCESSO!")
            print("="*100)
            print(f"⭐ Confiança: {result.get('confidence', 'N/A')}/5")
            print(f"📊 Qualidade dos dados: {result.get('data_quality', 'N/A')}")
            print("\n📝 Primeiros 500 caracteres da análise:")
            print("-"*100)
            analysis = result.get('analysis', '')
            print(analysis[:500] + "...")
            print("-"*100)
        else:
            print(f"❌ ERRO na análise: {result.get('error')}")
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*100)
    print("✅ TESTE CONCLUÍDO")
    print("="*100 + "\n")
    
    print("📖 DOCUMENTAÇÃO:")
    print("-"*100)
    print("""
    ✅ VARIÁVEIS IMPLEMENTADAS (Alto Impacto):
       1. Posição na tabela (standings)
       2. Lesões e suspensões (injuries)
       3. Odds das casas de apostas
       4. Estatísticas detalhadas dos times
       5. Contexto da temporada (fase, rodada)
    
    ⚠️ VARIÁVEIS PARCIALMENTE IMPLEMENTADAS:
       6. Descanso entre jogos (estrutura criada, requer histórico)
       7. Motivação do time (estrutura criada, requer análise de posição)
       8. Tendências Over/Under e BTTS (estrutura criada, requer histórico)
    
    🚀 PRÓXIMOS PASSOS:
       - Implementar cálculo de descanso com histórico de partidas
       - Calcular tendências Over/Under e BTTS analisando últimos jogos
       - Adicionar análise de motivação baseada em posição na tabela
       - Implementar cache para reduzir chamadas à API
    """)
    print("-"*100 + "\n")

if __name__ == '__main__':
    test_enriched_analysis()
