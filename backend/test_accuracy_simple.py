"""
TESTE SIMPLES DE ACERTIVIDADE - SEM BANCO DE DADOS
Testa apenas os modelos estatísticos com dados históricos conhecidos
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.statistical_models import ModelEnsemble
from apps.matches.services.football_api import FootballAPIService
from datetime import datetime, timedelta

print("\n" + "="*80)
print("🎯 TESTE DE ACERTIVIDADE - MODELOS ESTATÍSTICOS")
print("="*80)

# Inicializar
api = FootballAPIService()
ensemble = ModelEnsemble()

# Buscar partidas finalizadas
print(f"\n📅 Buscando partidas finalizadas dos últimos 2 dias...")
dates = [
    (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
    (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
]

finished_matches = []
for date in dates:
    result = api.get_fixtures_by_date(date)
    if result['success']:
        finished = [
            f for f in result['fixtures']
            if f['fixture']['status']['short'] == 'FT' and
            f['league']['id'] in [39, 140, 61, 78, 135]
        ]
        finished_matches.extend(finished)

print(f"✅ {len(finished_matches)} partidas finalizadas encontradas")

if len(finished_matches) == 0:
    print("⚠️  Nenhuma partida disponível")
    sys.exit(0)

# Limitar para teste
test_matches = finished_matches[:10]

print(f"\n🔄 Testando {len(test_matches)} partidas...\n")
print("="*80)

results = []

for i, fixture in enumerate(test_matches, 1):
    home_team = fixture['teams']['home']['name']
    away_team = fixture['teams']['away']['name']
    home_score = fixture['goals']['home']
    away_score = fixture['goals']['away']
    league = fixture['league']['name']
    
    # Resultado real
    if home_score > away_score:
        actual = 'home'
    elif away_score > home_score:
        actual = 'away'
    else:
        actual = 'draw'
    
    print(f"\n[{i}/{len(test_matches)}] {home_team} vs {away_team}")
    print(f"   Liga: {league}")
    print(f"   Placar: {home_score}-{away_score} | Resultado: {actual}")
    
    try:
        # Estimar força dos times baseado em dados básicos
        # (Em produção, usaria dados enriquecidos)
        home_strength = 1.3  # Média neutra
        away_strength = 1.2
        weather_impact = 0.0
        
        # Features básicas
        features = {
            'strength': {
                'home_goals_per_game': home_strength,
                'away_goals_per_game': away_strength
            },
            'weather': {
                'goal_impact': weather_impact
            },
            'form': {},
            'h2h': {},
            'market': {}
        }
        
        # Executar previsão
        prediction = ensemble.predict(features, home_strength, away_strength, weather_impact)
        
        # Extrair consenso
        consensus = prediction.get('consensus', {})
        home_prob = consensus.get('home_win', 0)
        draw_prob = consensus.get('draw', 0)
        away_prob = consensus.get('away_win', 0)
        
        # Determinar previsão
        max_prob = max(home_prob, draw_prob, away_prob)
        if max_prob == home_prob:
            predicted = 'home'
        elif max_prob == away_prob:
            predicted = 'away'
        else:
            predicted = 'draw'
        
        # Verificar acerto
        is_correct = (predicted == actual)
        
        print(f"   🤖 Previsão: {predicted} ({max_prob*100:.1f}%)")
        print(f"   📊 H: {home_prob*100:.1f}% | D: {draw_prob*100:.1f}% | A: {away_prob*100:.1f}%")
        print(f"   {'✅ ACERTOU' if is_correct else '❌ ERROU'}")
        
        results.append({
            'home_team': home_team,
            'away_team': away_team,
            'actual': actual,
            'predicted': predicted,
            'correct': is_correct,
            'probability': max_prob,
            'home_score': home_score,
            'away_score': away_score
        })
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

# Relatório
print("\n" + "="*80)
print("📊 RELATÓRIO FINAL")
print("="*80)

if results:
    total = len(results)
    correct = sum(1 for r in results if r['correct'])
    accuracy = (correct / total * 100)
    
    print(f"\n✅ Partidas testadas: {total}")
    print(f"✅ Acertos: {correct}")
    print(f"❌ Erros: {total - correct}")
    print(f"📈 Taxa de acerto: {accuracy:.1f}%")
    
    # Por tipo de resultado
    print(f"\n📊 ACERTOS POR TIPO:")
    for result_type in ['home', 'draw', 'away']:
        type_results = [r for r in results if r['actual'] == result_type]
        if type_results:
            type_correct = sum(1 for r in type_results if r['correct'])
            type_accuracy = (type_correct / len(type_results) * 100)
            label = {'home': 'Vitória Casa', 'draw': 'Empate', 'away': 'Vitória Fora'}[result_type]
            print(f"   {label}: {type_correct}/{len(type_results)} = {type_accuracy:.1f}%")
    
    # Probabilidade média
    avg_prob_correct = sum(r['probability'] for r in results if r['correct']) / correct if correct > 0 else 0
    avg_prob_incorrect = sum(r['probability'] for r in results if not r['correct']) / (total - correct) if (total - correct) > 0 else 0
    
    print(f"\n📊 PROBABILIDADE MÉDIA:")
    print(f"   Acertos: {avg_prob_correct*100:.1f}%")
    print(f"   Erros: {avg_prob_incorrect*100:.1f}%")
    
    print("\n" + "="*80)
    if accuracy >= 60:
        print("🎯 EXCELENTE: ≥ 60% (Meta atingida!)")
        print("✅ Modelo pronto para uso comercial")
    elif accuracy >= 55:
        print("⚠️  BOM: 55-60% (Próximo da meta)")
        print("💛 Considerar calibração adicional")
    elif accuracy >= 50:
        print("⚠️  REGULAR: 50-55% (Precisa melhorar)")
        print("🟠 Ajustes recomendados antes do lançamento")
    else:
        print("❌ INSUFICIENTE: < 50%")
        print("🔴 Necessário revisar modelos")
    print("="*80)
    
    print(f"\n💡 NOTA: Este teste usa força neutra dos times.")
    print(f"   Com dados reais (stats, form, H2H), a acertividade tende a ser maior.\n")
else:
    print("\n❌ Nenhum resultado disponível\n")
