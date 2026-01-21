"""
TESTE RÁPIDO DE ACERTIVIDADE
Valida com 5-10 partidas finalizadas recentes
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from datetime import datetime, timedelta

print("\n" + "="*80)
print("🎯 TESTE RÁPIDO DE ACERTIVIDADE")
print("="*80)

# Inicializar
api = FootballAPIService()
orchestrator = HybridAnalysisOrchestrator()

# Buscar partidas finalizadas de ontem
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
print(f"\n📅 Buscando partidas finalizadas de {yesterday}...")

result = api.get_fixtures_by_date(yesterday)

if not result['success']:
    print(f"❌ Erro ao buscar partidas: {result.get('error')}")
    sys.exit(1)

# Filtrar apenas finalizadas de ligas principais
finished = [
    f for f in result['fixtures']
    if f['fixture']['status']['short'] == 'FT' and
    f['league']['id'] in [39, 140, 61, 78, 135]  # Top 5 ligas
]

print(f"✅ Encontradas {len(finished)} partidas finalizadas")

if len(finished) == 0:
    print("\n⚠️  Nenhuma partida disponível. Tente outro dia.")
    sys.exit(0)

# Limitar a 5 partidas para teste rápido
test_matches = finished[:5]

print(f"\n🔄 Testando com {len(test_matches)} partidas...\n")
print("="*80)

results = []

for i, fixture in enumerate(test_matches, 1):
    fixture_id = fixture['fixture']['id']
    home = fixture['teams']['home']['name']
    away = fixture['teams']['away']['name']
    home_score = fixture['goals']['home']
    away_score = fixture['goals']['away']
    
    # Determinar resultado real
    if home_score > away_score:
        actual = 'home'
    elif away_score > home_score:
        actual = 'away'
    else:
        actual = 'draw'
    
    print(f"\n[{i}/{len(test_matches)}] {home} vs {away}")
    print(f"   Placar: {home_score}-{away_score} (Resultado: {actual})")
    
    try:
        # Criar objeto Match temporário
        from apps.matches.models import Match
        
        # Buscar ou criar match
        match, created = Match.objects.get_or_create(
            api_football_id=fixture_id,
            defaults={
                'home_team_id': fixture['teams']['home']['id'],
                'away_team_id': fixture['teams']['away']['id'],
                'league_id': fixture['league']['id'],
                'match_date': fixture['fixture']['date'],
                'status': fixture['fixture']['status']['short']
            }
        )
        
        # Executar análise
        analysis = orchestrator.run(match)
        
        if not analysis:
            print(f"   ❌ Análise falhou")
            continue
        
        # Extrair dados
        predicted = analysis.get('prediction')  # 'home', 'draw', 'away'
        home_prob = analysis.get('home_probability', 0) / 100  # Converter de percentual
        draw_prob = analysis.get('draw_probability', 0) / 100
        away_prob = analysis.get('away_probability', 0) / 100
        confidence_level = analysis.get('confidence', 3)
        
        # Determinar probabilidade da previsão
        if predicted == 'home':
            max_prob = home_prob
        elif predicted == 'away':
            max_prob = away_prob
        else:
            max_prob = draw_prob
        
        # Verificar acerto
        is_correct = (predicted == actual)
        
        print(f"   🤖 Previsão: {predicted} ({max_prob*100:.1f}%) | Confiança: {confidence_level}★")
        print(f"   📊 Probabilidades: Casa {home_prob*100:.1f}% | Empate {draw_prob*100:.1f}% | Fora {away_prob*100:.1f}%")
        print(f"   {'✅ ACERTOU!' if is_correct else '❌ ERROU'}")
        
        results.append({
            'correct': is_correct,
            'probability': max_prob,
            'predicted': predicted,
            'actual': actual
        })
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

# Relatório final
print("\n" + "="*80)
print("📊 RESULTADO DO TESTE")
print("="*80)

if results:
    total = len(results)
    correct = sum(1 for r in results if r['correct'])
    accuracy = (correct / total * 100)
    
    print(f"\n✅ Partidas testadas: {total}")
    print(f"✅ Previsões corretas: {correct}")
    print(f"❌ Previsões incorretas: {total - correct}")
    print(f"📈 Taxa de acerto: {accuracy:.1f}%")
    
    avg_prob = sum(r['probability'] for r in results) / total
    print(f"📊 Probabilidade média: {avg_prob*100:.1f}%")
    
    print("\n" + "="*80)
    if accuracy >= 60:
        print("🎯 RESULTADO: EXCELENTE (≥ 60%)")
    elif accuracy >= 50:
        print("⚠️  RESULTADO: BOM (50-60%)")
    else:
        print("❌ RESULTADO: PRECISA MELHORAR (< 50%)")
    print("="*80 + "\n")
    
    print("💡 Para validação completa, execute: python validate_accuracy_with_real_matches.py\n")
else:
    print("\n❌ Nenhum resultado disponível\n")
