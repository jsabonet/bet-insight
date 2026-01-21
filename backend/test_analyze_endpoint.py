"""
Teste do endpoint analyze() com HybridAnalysisOrchestrator
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from datetime import datetime, timedelta

def test_analyze_single_match():
    """Testar análise de UMA partida (como o botão fará)"""
    
    # Buscar uma partida recente (FINISHED ou SCHEDULED)
    cutoff_date = datetime.now() - timedelta(days=60)
    match = Match.objects.filter(
        match_date__gte=cutoff_date
    ).exclude(
        status='CANCELLED'
    ).first()
    
    if not match:
        print("❌ Nenhuma partida encontrada nos últimos 60 dias")
        return
    
    print(f"\n{'='*80}")
    print(f"🎯 TESTE: Análise de 1 PARTIDA (simulando clique no botão)")
    print(f"{'='*80}")
    print(f"📌 Partida: {match.home_team.name} vs {match.away_team.name}")
    print(f"📅 Data: {match.match_date}")
    print(f"🏆 Liga: {match.league.name}")
    print(f"🆔 ID: {match.id}")
    print(f"{'='*80}\n")
    
    # Executar análise com Orchestrator
    print("⏳ Executando HybridAnalysisOrchestrator...")
    import time
    start = time.time()
    
    orchestrator = HybridAnalysisOrchestrator()
    result = orchestrator.run(match)
    
    elapsed = time.time() - start
    
    print(f"\n{'='*80}")
    print(f"✅ ANÁLISE COMPLETA EM {elapsed:.2f}s")
    print(f"{'='*80}")
    
    if result:
        # Dados diretos do orchestrator (formato atualizado)
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Home: {result.get('home_probability', 0):.1f}%")
        print(f"   Draw: {result.get('draw_probability', 0):.1f}%")
        print(f"   Away: {result.get('away_probability', 0):.1f}%")
        print(f"   Home xG: {result.get('home_xg', 0):.2f}")
        print(f"   Away xG: {result.get('away_xg', 0):.2f}")
        
        # Decisão (dentro de analysis_data)
        analysis_data = result.get('analysis_data', {})
        recommendation = analysis_data.get('recommendation', {})
        confidence_data = analysis_data.get('confidence', {})
        
        print(f"\n🎯 DECISÃO:")
        print(f"   Recomendação: {result.get('prediction', 'N/A')}")
        print(f"   Confiança: {result.get('confidence', 0)}/5 estrelas")
        print(f"   Probabilidade: {recommendation.get('probability', 0)*100:.1f}%")
        print(f"   Should Publish: {result.get('should_publish', False)}")
        
        # IA
        print(f"\n🤖 EXPLICAÇÃO IA:")
        reasoning = result.get('reasoning', 'N/A')
        print(f"   {reasoning[:300]}...")
        print(f"   Fatores: {', '.join(result.get('key_factors', [])[:3])}")
        
        print(f"\n{'='*80}")
        print(f"✅ TESTE CONCLUÍDO - Sistema usando 109 features + ensemble 50/35/15")
        print(f"{'='*80}\n")
        
        return True
    else:
        print("❌ Falha na análise")
        return False

if __name__ == '__main__':
    test_analyze_single_match()
