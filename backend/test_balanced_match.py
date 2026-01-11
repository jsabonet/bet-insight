"""
Testa análise com jogo EQUILIBRADO (nenhuma prob > 45%)
Deve PRIORIZAR Dupla Chance ou Draw No Bet
"""
import os
import sys
import django

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.ai_analyzer import AIAnalyzer

def test_balanced_match():
    print("TESTE: JOGO EQUILIBRADO (Mallorca vs Rayo Vallecano)")
    print("="*77)
    
    # Jogo equilibrado: Mallorca 32.9%, Empate 30.6%, Rayo 36.4%
    decision_data = {
        'recommendation': {
            'pick': 'Away Win',
            'probability': 0.364,
            'odd': 2.75,
            'expected_value': 0.001,
        },
        'confidence': {
            'level': 'medium',
            'stars': 3,
            'explanation': 'Jogo equilibrado'
        },
        'risk': 'medium',
        'model_probabilities': {
            'poisson': {
                'expected_goals_home': 1.15,
                'expected_goals_away': 1.25,
                'most_likely_score': '1-1',
            },
            'consensus': {
                'home_win': 0.329,
                'draw': 0.306,
                'away_win': 0.364,
            }
        }
    }
    
    enriched_data = {
        'fixture_details': {
            'teams': {
                'home': {'name': 'Mallorca'},
                'away': {'name': 'Rayo Vallecano'}
            },
            'league': {
                'name': 'La Liga'
            },
            'fixture': {
                'date': '2026-01-12T15:00:00+00:00'
            }
        }
    }
    
    analyzer = AIAnalyzer()
    print("✅ AIAnalyzer inicializado\n")
    
    print("📊 DADOS DO JOGO:")
    print(f"   Mallorca: 32.9% | Empate: 30.6% | Rayo: 36.4%")
    print(f"   xG: 1.15 x 1.25 (total 2.40)")
    print(f"   Nenhuma prob > 45% → JOGO EQUILIBRADO\n")
    
    print("📝 Chamando explain_decision()...\n")
    result = analyzer.explain_decision(decision_data, enriched_data)
    
    if result['success']:
        print("✅ Resultado recebido!\n")
        print("="*77)
        print("📄 REASONING COMPLETO:")
        print("="*77)
        print(result['reasoning'])
        print("\n" + "="*77)
        
        # Verificar se priorizou Dupla Chance
        reasoning = result['reasoning'].lower()
        
        print("\n✅ VERIFICAÇÕES:")
        print(f"   ✅ Mencionou 'jogo equilibrado'?: {'equilibrado' in reasoning}")
        print(f"   ✅ Analisou Dupla Chance?: {'dupla chance' in reasoning}")
        print(f"   ✅ Justificou escolha de mercado?: {'descartad' in reasoning or 'rejeitad' in reasoning}")
        print(f"   ✅ Comparou >= 4 mercados?: {reasoning.count('mercado') >= 4}")
        
        # Verificar se NÃO inventou dados
        print(f"\n   ❌ Inventou confronto direto?: {'confronto' in reasoning or 'histórico' in reasoning}")
        print(f"   ❌ Inventou forma recente?: {'últimos jogos' in reasoning or 'forma recente' in reasoning}")
    else:
        print(f"❌ Erro: {result.get('error', 'Desconhecido')}")

if __name__ == '__main__':
    test_balanced_match()
