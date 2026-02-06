"""
Análise completa da partida 1508602 - COM RESULTADO CORRETO
Anderlecht 0 x 1 Antwerp
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

# RESULTADO REAL OBTIDO DA API
HOME_TEAM = "Anderlecht"
AWAY_TEAM = "Antwerp"
HOME_SCORE = 0
AWAY_SCORE = 1
FIXTURE_ID = 1508602

print("\n" + "="*100)
print("ANALISE COMPLETA - PARTIDA 1508602")
print("="*100)

print(f"\nPARTIDA: {HOME_TEAM} vs {AWAY_TEAM}")
print(f"COMPETICAO: Copa da Belgica - Semifinal")
print(f"DATA: 05/02/2026")

print(f"\n" + "="*100)
print("RESULTADO REAL (DA API-FOOTBALL)")
print("="*100)
print(f"\n{HOME_TEAM} {HOME_SCORE} x {AWAY_SCORE} {AWAY_TEAM}")

result_code = 'away'  # Antwerp venceu
result_text = f"Vitoria {AWAY_TEAM} (FORA)"

print(f"RESULTADO: {result_text}")

# Mercados
total_goals = HOME_SCORE + AWAY_SCORE
over_25 = total_goals > 2
btts = HOME_SCORE > 0 and AWAY_SCORE > 0

print(f"\nMERCADOS:")
print(f"  Total de Gols: {total_goals}")
print(f"  Over 2.5: {'SIM' if over_25 else 'NAO (apenas 1 gol)'}")
print(f"  BTTS: {'SIM' if btts else 'NAO (apenas Antwerp marcou)'}")

# Executar análise do sistema
print(f"\n" + "="*100)
print("PREVISAO DO SISTEMA (EXECUTADA ANTES DO JOGO)")
print("="*100)

class MockMatch:
    def __init__(self, api_id):
        self.api_football_id = api_id
        self.league = None

mock = MockMatch(FIXTURE_ID)
orch = HybridAnalysisOrchestrator()

try:
    result = orch.run(mock, strategy='value')
    
    # Previsão
    pred = result.get('prediction', 'N/A')
    pred_map = {
        'home': f'Vitoria {HOME_TEAM} (Casa)',
        'draw': 'Empate',
        'away': f'Vitoria {AWAY_TEAM} (Fora)'
    }
    
    print(f"\nPREVISAO 1X2: {pred_map.get(pred, pred)}")
    
    # Confiança
    conf = result.get('confidence', {})
    if isinstance(conf, dict):
        stars = conf.get('stars', 0)
        level = conf.get('level', 'N/A')
    else:
        stars = conf
        level = 'N/A'
    
    print(f"CONFIANCA: {stars}/5 estrelas ({level})")
    
    # Probabilidades
    home_p = result.get('home_probability', 0)
    draw_p = result.get('draw_probability', 0)
    away_p = result.get('away_probability', 0)
    
    print(f"\nPROBABILIDADES 1X2:")
    print(f"  Casa ({HOME_TEAM}): {home_p:.1f}%")
    print(f"  Empate: {draw_p:.1f}%")
    print(f"  Fora ({AWAY_TEAM}): {away_p:.1f}%")
    
    # Expected Goals
    home_xg = result.get('home_xg', 0)
    away_xg = result.get('away_xg', 0)
    
    print(f"\nEXPECTED GOALS (xG):")
    print(f"  {HOME_TEAM}: {home_xg:.2f} (Real: {HOME_SCORE}) - Erro: {abs(home_xg - HOME_SCORE):.2f}")
    print(f"  {AWAY_TEAM}: {away_xg:.2f} (Real: {AWAY_SCORE}) - Erro: {abs(away_xg - AWAY_SCORE):.2f}")
    print(f"  Total: {home_xg + away_xg:.2f} (Real: {total_goals}) - Erro: {abs((home_xg + away_xg) - total_goals):.2f}")
    
    # Top Bets
    top_bets = result.get('top_bets', [])
    if top_bets:
        print(f"\nTOP 3 APOSTAS RECOMENDADAS:")
        
        for i, bet in enumerate(top_bets[:3], 1):
            market = bet.get('market_display', 'N/A')
            market_key = bet.get('market', '')
            prob = bet.get('probability', 0) * 100
            odd = bet.get('market_odd', 0)
            ev = bet.get('ev_pct', 0)
            
            print(f"\n  #{i}: {market}")
            print(f"      Probabilidade: {prob:.1f}%")
            print(f"      Odd: {odd:.2f}")
            print(f"      EV: {ev:+.1f}%")
            
            # Verificar se acertou
            bet_won = False
            
            if 'over_2_5' in market_key.lower() and over_25:
                bet_won = True
            elif 'under_2_5' in market_key.lower() and not over_25:
                bet_won = True
            elif 'btts' in market_key.lower() and 'yes' in market_key.lower() and btts:
                bet_won = True
            elif 'btts' in market_key.lower() and 'no' in market_key.lower() and not btts:
                bet_won = True
            elif market_key == 'home_win' and result_code == 'home':
                bet_won = True
            elif market_key == 'away_win' and result_code == 'away':
                bet_won = True
            elif market_key == 'draw' and result_code == 'draw':
                bet_won = True
            
            result_emoji = "ACERTOU!" if bet_won else "Errou"
            print(f"      RESULTADO: {result_emoji}")
    
    # Comparação final
    print(f"\n" + "="*100)
    print("AVALIACAO FINAL")
    print("="*100)
    
    print(f"\nPrevisao 1X2: {pred_map.get(pred, pred)}")
    print(f"Real 1X2: {result_text}")
    
    correct_1x2 = (pred == result_code)
    print(f"\nResultado 1X2: {'ACERTOU!' if correct_1x2 else 'ERROU'}")
    
    # Probabilidade atribuída
    probs_dict = {'home': home_p, 'draw': draw_p, 'away': away_p}
    real_prob = probs_dict.get(result_code, 0)
    
    print(f"\nProbabilidade atribuida ao resultado real: {real_prob:.1f}%")
    
    if correct_1x2:
        if real_prob >= 50:
            calibration = "EXCELENTE - Sistema previu corretamente com alta confianca"
        elif real_prob >= 40:
            calibration = "MUITO BOM - Sistema previu corretamente"
        else:
            calibration = "BOM - Sistema acertou mas com probabilidade moderada"
    else:
        if real_prob >= 40:
            calibration = "RAZOAVEL - Sistema viu resultado real como muito provavel mas escolheu outro"
        elif real_prob >= 30:
            calibration = "REGULAR - Sistema viu resultado real como possivel"
        else:
            calibration = "RUIM - Sistema subestimou muito o resultado real"
    
    print(f"Calibracao: {calibration}")
    
    # Análise de mercados
    print(f"\n" + "="*100)
    print("RESUMO DE ACURACIA")
    print("="*100)
    
    print(f"\n1X2: {'CORRETO' if correct_1x2 else 'INCORRETO'}")
    print(f"  Previsto: {pred_map.get(pred, pred)}")
    print(f"  Real: {result_text}")
    
    print(f"\nExpected Goals:")
    print(f"  xG Casa: {home_xg:.2f} vs Real {HOME_SCORE} (erro: {abs(home_xg - HOME_SCORE):.2f})")
    print(f"  xG Fora: {away_xg:.2f} vs Real {AWAY_SCORE} (erro: {abs(away_xg - AWAY_SCORE):.2f})")
    print(f"  xG Total: {home_xg + away_xg:.2f} vs Real {total_goals} (erro: {abs((home_xg + away_xg) - total_goals):.2f})")
    
    # Análise crítica
    print(f"\n" + "="*100)
    print("ANALISE CRITICA DO SISTEMA")
    print("="*100)
    
    print(f"\nO que o sistema previu:")
    print(f"  - Vitoria: {pred_map.get(pred, pred)}")
    print(f"  - Confianca: {stars}/5")
    print(f"  - xG Total: {home_xg + away_xg:.2f} gols")
    
    print(f"\nO que realmente aconteceu:")
    print(f"  - Vitoria: {AWAY_TEAM} (Fora)")
    print(f"  - Total de gols: {total_goals} (apenas 1)")
    print(f"  - Apenas Antwerp marcou")
    
    print(f"\nPontos de analise:")
    
    if correct_1x2:
        print(f"  + ACERTOU o vencedor (prob {real_prob:.1f}%)")
    else:
        print(f"  - ERROU o vencedor (atribuiu {real_prob:.1f}% ao resultado real)")
    
    xg_error = abs((home_xg + away_xg) - total_goals)
    if xg_error <= 1.0:
        print(f"  + xG Total razoavel (erro {xg_error:.2f})")
    elif xg_error <= 2.0:
        print(f"  ~ xG Total com erro moderado ({xg_error:.2f})")
    else:
        print(f"  - xG Total muito alto (erro {xg_error:.2f} - previu {home_xg + away_xg:.2f}, ocorreu {total_goals})")
    
    # Análise dos top bets
    if top_bets:
        wins = sum(1 for bet in top_bets[:3] if (
            ('over_2_5' in bet.get('market', '').lower() and over_25) or
            ('under_2_5' in bet.get('market', '').lower() and not over_25) or
            (bet.get('market') == 'away_win' and result_code == 'away') or
            (bet.get('market') == 'home_win' and result_code == 'home')
        ))
        
        print(f"\n  Top 3 apostas: {wins}/3 acertos ({wins/3*100:.0f}%)")
        
        if wins >= 2:
            print(f"  + Boa taxa de acerto nas apostas recomendadas")
        elif wins == 1:
            print(f"  ~ Taxa moderada de acerto")
        else:
            print(f"  - Nenhuma das top 3 acertou")

except Exception as e:
    print(f"\nErro ao executar analise: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "="*100)
print("FIM DA ANALISE")
print("="*100)
