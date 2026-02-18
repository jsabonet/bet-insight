import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet

print("\n" + "="*80)
print("🧪 TESTE: ANÁLISE DE BILHETES GERADOS COM NOVOS THRESHOLDS")
print("="*80 + "\n")

# Buscar todos os bilhetes múltiplos dos últimos 7 dias
seven_days_ago = datetime.now() - timedelta(days=7)
all_tickets = DailyBet.objects.filter(
    created_at__gte=seven_days_ago,
    bet_type='multiple'
).order_by('-created_at')

print(f"📊 Bilhetes múltiplos dos últimos 7 dias: {all_tickets.count()}\n")

if not all_tickets.exists():
    print("⚠️  Nenhum bilhete encontrado nos últimos 7 dias.")
    print("   Execute primeiro: python manage.py generate_daily_bets --mode=hybrid")
    exit(0)

print("="*80)
print("🔍 VALIDAÇÃO COM NOVOS THRESHOLDS:")
print("="*80 + "\n")

stats = {
    'total': 0,
    'would_pass': 0,
    'would_fail': 0,
    'fail_reasons': {
        'low_individual_prob': 0,
        'low_combined_prob': 0,
        'high_draw': 0,
        'low_confidence': 0,
        'high_risk': 0,
        'odd_out_of_range': 0
    }
}

for ticket in all_tickets:
    stats['total'] += 1
    selections = ticket.selections if isinstance(ticket.selections, list) else []
    num_selections = len(selections)
    
    # Determinar thresholds baseado no número de seleções
    if num_selections == 3:
        min_individual_prob = 0.80
        min_combined_prob = 0.50
        ticket_name = '3X'
    elif num_selections == 5:
        min_individual_prob = 0.87
        min_combined_prob = 0.50
        ticket_name = '5X'
    elif num_selections == 7:
        min_individual_prob = 0.91
        min_combined_prob = 0.50
        ticket_name = '7X'
    else:
        # Skip tickets que não são 3X, 5X ou 7X
        stats['total'] -= 1
        continue
    
    # Usar probabilidade combinada já calculada
    combined_prob = ticket.combined_probability
    fail_reasons = []
    has_data_issues = False
    
    for selection in selections:
        prob = selection.get('probability', 0)
        
        # Check individual probability
        if prob < min_individual_prob:
            fail_reasons.append(f"prob_individual")
            stats['fail_reasons']['low_individual_prob'] += 1
        
        # Check draw probability (se disponível)
        if 'draw_probability' in selection:
            draw_prob = selection.get('draw_probability', 0)
            if draw_prob > 0.35:
                fail_reasons.append(f"draw_high")
                stats['fail_reasons']['high_draw'] += 1
        
        # Check confidence (se disponível)
        if 'confidence' in selection:
            confidence = selection.get('confidence', {})
            if isinstance(confidence, dict):
                stars = confidence.get('stars', 0)
                if stars < 4:
                    fail_reasons.append(f"confidence_low")
                    stats['fail_reasons']['low_confidence'] += 1
        
        # Check risk (se disponível)
        if 'risk' in selection:
            risk = selection.get('risk', '')
            if risk and risk not in ['low', 'medium']:
                fail_reasons.append(f"risk_high")
                stats['fail_reasons']['high_risk'] += 1
        
        # Check odd range
        odd = selection.get('odd', 0)
        if odd < 1.10 or odd > 1.50:
            fail_reasons.append(f"odd_range")
            stats['fail_reasons']['odd_out_of_range'] += 1
    
    # Check combined probability
    if combined_prob < min_combined_prob:
        fail_reasons.append(f"prob_combined")
        stats['fail_reasons']['low_combined_prob'] += 1
    
    would_pass = len(fail_reasons) == 0
    
    if would_pass:
        stats['would_pass'] += 1
        status_emoji = "✅"
        status_text = "PASSARIA"
    else:
        stats['would_fail'] += 1
        status_emoji = "❌"
        status_text = "SERIA REJEITADO"
    
    print(f"{status_emoji} Bilhete {ticket_name} (ID: {ticket.id}) - {status_text}")
    print(f"   Data: {ticket.created_at.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Odd Total: {ticket.total_odd:.2f}")
    print(f"   Prob Combinada: {combined_prob*100:.2f}% (mín: {min_combined_prob*100:.0f}%)")
    print(f"   Status Real: {ticket.status.upper()}")
    print(f"   Número de Apostas: {num_selections}")
    
    if not would_pass:
        print(f"   Motivos de rejeição:")
        unique_reasons = set(fail_reasons)
        if 'prob_individual' in unique_reasons:
            print(f"      • Pelo menos 1 aposta com prob < {min_individual_prob*100:.0f}%")
        if 'prob_combined' in unique_reasons:
            print(f"      • Prob combinada {combined_prob*100:.2f}% < {min_combined_prob*100:.0f}%")
        if 'draw_high' in unique_reasons:
            print(f"      • Pelo menos 1 aposta com empate > 35%")
        if 'confidence_low' in unique_reasons:
            print(f"      • Pelo menos 1 aposta com confidence < 4 estrelas")
        if 'risk_high' in unique_reasons:
            print(f"      • Pelo menos 1 aposta com risco alto")
        if 'odd_range' in unique_reasons:
            print(f"      • Pelo menos 1 aposta com odd fora do range (1.10-1.50)")
    
    print()

print("="*80)
print("📈 ESTATÍSTICAS FINAIS:")
print("="*80 + "\n")

print(f"   Total de bilhetes analisados: {stats['total']}")
print(f"   ✅ Passariam nos novos thresholds: {stats['would_pass']} ({stats['would_pass']/stats['total']*100:.1f}%)")
print(f"   ❌ Seriam rejeitados: {stats['would_fail']} ({stats['would_fail']/stats['total']*100:.1f}%)")

print(f"\n   🔍 Motivos de rejeição (total de violações):")
print(f"      • Probabilidade individual baixa: {stats['fail_reasons']['low_individual_prob']}")
print(f"      • Probabilidade combinada baixa: {stats['fail_reasons']['low_combined_prob']}")
print(f"      • Empate alto (>35%): {stats['fail_reasons']['high_draw']}")
print(f"      • Confidence baixa (<4 estrelas): {stats['fail_reasons']['low_confidence']}")
print(f"      • Risco alto: {stats['fail_reasons']['high_risk']}")
print(f"      • Odd fora do range (1.10-1.50): {stats['fail_reasons']['odd_out_of_range']}")

print("\n" + "="*80)
print("💡 INTERPRETAÇÃO:")
print("="*80 + "\n")

rejection_rate = stats['would_fail'] / stats['total'] * 100

if rejection_rate > 70:
    print("   ⚠️  ALTA taxa de rejeição (>70%)")
    print("      • Novos thresholds são MUITO mais restritivos")
    print("      • Sistema gerará MENOS bilhetes, mas com MAIOR qualidade")
    print("      • Esperado: Menos apostas, maior taxa de acerto")
elif rejection_rate > 40:
    print("   ✅ Taxa de rejeição MODERADA (40-70%)")
    print("      • Equilíbrio entre quantidade e qualidade")
    print("      • Sistema filtra apostas ruins mantendo volume razoável")
elif rejection_rate > 0:
    print("   ℹ️  Taxa de rejeição BAIXA (<40%)")
    print("      • Maioria dos bilhetes antigos já atendiam critérios")
    print("      • Novo sistema mantém produção similar")
else:
    print("   🎯 TODOS os bilhetes antigos passariam nos novos thresholds")
    print("      • Sistema anterior já tinha boa qualidade")
    print("      • Melhorias incrementais")

print("\n   🎯 Recomendação:")
if rejection_rate > 80:
    print("      Considere reduzir ligeiramente os thresholds se volume cair muito")
elif rejection_rate > 50:
    print("      Thresholds estão no ponto ideal - monitore resultados reais")
else:
    print("      Thresholds podem ser aumentados se quiser mais qualidade")

print("\n" + "="*80 + "\n")
