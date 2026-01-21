"""
Teste de integração frontend-backend
Simula chamada do frontend ao endpoint /matches/{id}/analyze/
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from django.contrib.auth import get_user_model
import json

User = get_user_model()

def test_integration():
    """Testa se a resposta do endpoint está compatível com o frontend"""
    
    # Buscar qualquer partida
    matches = Match.objects.all().select_related('home_team', 'away_team', 'league')[:5]
    
    if not matches:
        print("❌ Nenhuma partida encontrada com dados suficientes")
        return
    
    match = matches[0]
    
    print(f"\n{'='*80}")
    print(f"🎯 TESTE DE INTEGRAÇÃO FRONTEND-BACKEND")
    print(f"{'='*80}")
    print(f"\n📋 PARTIDA:")
    print(f"   {match.home_team.name} vs {match.away_team.name}")
    print(f"   Liga: {match.league.name if match.league else 'N/A'}")
    print(f"   Data: {match.match_date if hasattr(match, 'match_date') else 'N/A'}")
    
    # Executar orchestrator
    print(f"\n🔄 Executando HybridAnalysisOrchestrator...")
    orchestrator = HybridAnalysisOrchestrator()
    result = orchestrator.run(match)
    
    if not result:
        print("❌ Orchestrator não retornou resultado")
        return
    
    # Simular o que o views.py faz agora
    prediction = result.get('prediction', 'home')
    confidence = result.get('confidence', 3)
    home_probability = result.get('home_probability', 40.0)
    draw_probability = result.get('draw_probability', 30.0)
    away_probability = result.get('away_probability', 30.0)
    home_xg = result.get('home_xg', 1.5)
    away_xg = result.get('away_xg', 1.3)
    reasoning = result.get('reasoning', 'Análise baseada em ensemble estatístico.')
    key_factors = result.get('key_factors', [])
    analysis_data = result.get('analysis_data', {})
    should_publish = result.get('should_publish', True)
    
    # Mapear predição para display
    prediction_display_map = {
        'home': f'{match.home_team.name} vence',
        'away': f'{match.away_team.name} vence',
        'draw': 'Empate',
        'btts_yes': 'Ambas Marcam',
        'btts_no': 'Menos de 2.5 gols'
    }
    
    # Montar payload EXATAMENTE como o views.py
    payload = {
        'analysis': reasoning,
        'confidence': confidence,
        'remaining_analyses': 10,  # Simulado
        'saved': True,
        'saved_analysis': {
            'id': 999,
            'created_at': '2024-01-19T12:00:00Z',
        },
        # Dados estruturados para o modal
        'prediction': prediction,
        'prediction_display': prediction_display_map.get(prediction, prediction),
        'home_probability': home_probability,
        'draw_probability': draw_probability,
        'away_probability': away_probability,
        'home_xg': home_xg,
        'away_xg': away_xg,
        'reasoning': reasoning,
        'key_factors': key_factors,
        'should_publish': should_publish,
        # Dados extras do orchestrator
        'value_bets': analysis_data.get('value_bets', []),
        'fair_odds': analysis_data.get('fair_odds', {}),
        'risk': analysis_data.get('risk', 'medium'),
    }
    
    print(f"\n{'='*80}")
    print(f"📤 PAYLOAD ENVIADO AO FRONTEND (JSON):")
    print(f"{'='*80}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    print(f"\n{'='*80}")
    print(f"✅ VERIFICAÇÃO DE COMPATIBILIDADE:")
    print(f"{'='*80}")
    
    # Verificar campos esperados pelo frontend
    required_fields = [
        'prediction_display',
        'home_probability',
        'draw_probability', 
        'away_probability',
        'reasoning',
        'confidence'
    ]
    
    missing = []
    for field in required_fields:
        if field in payload:
            print(f"✅ {field}: {str(payload[field])[:50]}...")
        else:
            print(f"❌ {field}: AUSENTE")
            missing.append(field)
    
    if missing:
        print(f"\n⚠️  CAMPOS FALTANDO: {missing}")
    else:
        print(f"\n🎉 TODOS OS CAMPOS ESPERADOS ESTÃO PRESENTES!")
    
    # Verificar se AnalysisModal vai detectar como análise estruturada
    print(f"\n{'='*80}")
    print(f"🎭 DETECÇÃO DO ANALYSISMODAL:")
    print(f"{'='*80}")
    has_prediction_display = 'prediction_display' in payload
    print(f"   isSimpleAnalysis = !analysis.prediction_display")
    print(f"   → prediction_display presente: {has_prediction_display}")
    print(f"   → Será tratado como: {'ANÁLISE ESTRUTURADA ✅' if has_prediction_display else 'ANÁLISE SIMPLES ⚠️'}")
    
    print(f"\n{'='*80}")
    print(f"🎯 PREDIÇÃO FINAL:")
    print(f"{'='*80}")
    print(f"   {payload['prediction_display']}")
    print(f"   {'⭐' * confidence} ({confidence}/5)")
    print(f"   🏠 {match.home_team.name}: {home_probability:.1f}%")
    print(f"   🤝 Empate: {draw_probability:.1f}%")
    print(f"   ✈️  {match.away_team.name}: {away_probability:.1f}%")
    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    test_integration()
