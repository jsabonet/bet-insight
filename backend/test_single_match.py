"""
Teste individual de partida por ID
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator


def test_single_match(match_id=None):
    """Testa uma partida específica ou busca uma aleatória com score"""
    
    if match_id:
        match = Match.objects.filter(id=match_id).first()
        if not match:
            print(f"❌ Partida {match_id} não encontrada")
            return
    else:
        # Buscar partida com score disponível
        matches = Match.objects.filter(
            status__in=['FT', 'FINISHED', 'AET', 'PEN'],
            home_score__isnull=False,
            away_score__isnull=False
        ).order_by('?')[:10]
        
        if not matches:
            print("❌ Nenhuma partida finalizada encontrada")
            return
        
        print(f"\n📋 {matches.count()} partidas finalizadas disponíveis:\n")
        for i, m in enumerate(matches, 1):
            print(f"  {i}. ID {m.id}: {m.home_team.name} {m.home_score}-{m.away_score} {m.away_team.name} ({m.league.name})")
        
        match = matches[0]
        print(f"\n🎲 Testando: {match.home_team.name} vs {match.away_team.name}\n")
    
    # Resultado real (se disponível)
    actual = None
    if match.home_score is not None and match.away_score is not None:
        if match.home_score > match.away_score:
            actual = 'HOME'
        elif match.home_score < match.away_score:
            actual = 'AWAY'
        else:
            actual = 'DRAW'
    
    print(f"{'='*80}")
    print(f"🏟️  PARTIDA: {match.home_team.name} vs {match.away_team.name}")
    print(f"{'='*80}")
    print(f"📅 Data: {match.match_date}")
    print(f"🏆 Liga: {match.league.name}")
    if actual:
        print(f"📊 Placar Real: {match.home_score} - {match.away_score}")
        print(f"🎯 Resultado: {actual}")
    else:
        print(f"📊 Status: {match.status} (Partida ainda não jogada)")
    print(f"🆔 Match ID: {match.id}")
    print(f"{'='*80}\n")
    
    print("⏳ Executando análise...\n")
    
    import time
    start = time.time()
    
    orchestrator = HybridAnalysisOrchestrator()
    result = orchestrator.run(match)
    
    elapsed = time.time() - start
    
    if not result:
        print("❌ Erro na análise")
        return
    
    # Extrair predição
    predicted = result.get('prediction', '').upper()
    should_publish = result.get('should_publish', False)
    confidence = result.get('confidence', 0)
    home_prob = result.get('home_probability', 0)
    draw_prob = result.get('draw_probability', 0)
    away_prob = result.get('away_probability', 0)
    home_xg = result.get('home_xg', 0)
    away_xg = result.get('away_xg', 0)
    
    # Verificar resultado (se disponível)
    is_correct = None
    if actual:
        is_correct = (predicted == actual)
    
    print(f"\n{'='*80}")
    print(f"📊 RESULTADO DA ANÁLISE ({elapsed:.1f}s)")
    print(f"{'='*80}")
    print(f"🎯 Predição: {predicted}")
    if actual:
        print(f"✅ Real: {actual}")
    else:
        print(f"⏳ Real: (Partida ainda será jogada)")
    print(f"{'─'*80}")
    print(f"⭐ Confiança: {confidence}/5")
    print(f"📈 Probabilidades:")
    print(f"   🏠 Casa: {home_prob:.1f}%")
    print(f"   🤝 Empate: {draw_prob:.1f}%")
    print(f"   ✈️  Fora: {away_prob:.1f}%")
    print(f"⚽ Expected Goals:")
    print(f"   Casa: {home_xg:.2f}")
    print(f"   Fora: {away_xg:.2f}")
    print(f"📢 Publicar?: {'✅ SIM' if should_publish else '❌ NÃO (baixa confiança)'}")
    print(f"{'─'*80}")
    
    if is_correct is not None:
        if is_correct:
            print(f"✅✅✅ ACERTOU! ✅✅✅")
        else:
            print(f"❌❌❌ ERROU ❌❌❌")
    else:
        print(f"🔮 PREDIÇÃO PARA PARTIDA FUTURA")
    
    print(f"{'='*80}\n")
    
    # Detalhes do raciocínio
    analysis_data = result.get('analysis_data', {})
    recommendation = analysis_data.get('recommendation', {})
    
    print(f"💡 DETALHES DA DECISÃO:")
    print(f"   Mercado recomendado: {recommendation.get('market_display', 'N/A')}")
    print(f"   Probabilidade: {recommendation.get('probability', 0)*100:.1f}%")
    
    # Value bets
    value_bets = analysis_data.get('value_bets', [])
    if value_bets:
        print(f"\n💰 VALUE BETS IDENTIFICADAS:")
        for vb in value_bets[:3]:
            print(f"   • {vb.get('market_display')}: {vb.get('value_pct', 0):.1f}% value")
    
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste de partida específica')
    parser.add_argument('--id', type=int, help='ID da partida para testar')
    
    args = parser.parse_args()
    
    test_single_match(match_id=args.id)
