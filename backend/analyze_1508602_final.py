"""
Análise da partida 1508602 - Anderlecht vs Antwerp (Copa da Bélgica)
Com resultado manual: 2-1 para Anderlecht
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

def main():
    fixture_id = 1508602
    
    # RESULTADO REAL (consultado externamente)
    home_team = "Anderlecht"
    away_team = "Antwerp"
    league = "Copa da Belgica - Semifinal"
    home_score = 2
    away_score = 1
    
    print("\n" + "="*80)
    print(f"PARTIDA: {home_team} vs {away_team}")
    print(f"COMPETICAO: {league}")
    print("="*80)
    
    print(f"\nRESULTADO REAL: {home_team} {home_score} x {away_score} {away_team}")
    
    result_code = 'home'  # Casa venceu
    result_text = f"Vitoria {home_team}"
    
    print(f"RESULTADO: {result_text}")
    
    # Mercados
    total_gols = home_score + away_score  # 3 gols
    over_25 = "SIM" if total_gols > 2 else "NAO"
    btts = "SIM" if home_score > 0 and away_score > 0 else "NAO"
    
    print(f"\nMERCADOS:")
    print(f"  Over 2.5: {over_25} (Total: {total_gols} gols)")
    print(f"  BTTS: {btts} (Ambos marcaram)")
    
    # Análise do sistema
    print("\n" + "="*80)
    print("ANALISE DO SISTEMA (EXECUTADA ANTES DO JOGO)")
    print("="*80)
    
    class MockMatch:
        def __init__(self, api_id):
            self.api_football_id = api_id
            self.league = None
    
    mock = MockMatch(fixture_id)
    orch = HybridAnalysisOrchestrator()
    
    try:
        result_analysis = orch.run(mock, strategy='value')
        
        # Previsão
        pred = result_analysis.get('prediction', 'N/A')
        pred_map = {
            'home': f'Vitoria {home_team}',
            'draw': 'Empate',
            'away': f'Vitoria {away_team}'
        }
        
        print(f"\nPREVISAO DO SISTEMA: {pred_map.get(pred, pred)}")
        
        # Confiança
        conf = result_analysis.get('confidence', {})
        if isinstance(conf, dict):
            stars = conf.get('stars', 0)
            level = conf.get('level', 'N/A')
        else:
            stars = conf
            level = 'N/A'
        
        print(f"CONFIANCA: {stars}/5 estrelas ({level})")
        
        # Probabilidades
        home_p = result_analysis.get('home_probability', 0)
        draw_p = result_analysis.get('draw_probability', 0)
        away_p = result_analysis.get('away_probability', 0)
        
        print(f"\nPROBABILIDADES 1X2:")
        print(f"  Casa ({home_team}): {home_p:.1f}%")
        print(f"  Empate: {draw_p:.1f}%")
        print(f"  Fora ({away_team}): {away_p:.1f}%")
        
        # Expected Goals
        home_xg = result_analysis.get('home_xg', 0)
        away_xg = result_analysis.get('away_xg', 0)
        
        print(f"\nEXPECTED GOALS (xG):")
        print(f"  {home_team}: {home_xg:.2f} (Real: {home_score})")
        print(f"  {away_team}: {away_xg:.2f} (Real: {away_score})")
        
        # Acurácia do xG
        xg_error_home = abs(home_xg - home_score)
        xg_error_away = abs(away_xg - away_score)
        print(f"\nERRO xG:")
        print(f"  Casa: {xg_error_home:.2f} gols de diferenca")
        print(f"  Fora: {xg_error_away:.2f} gols de diferenca")
        
        # Top Bets
        top_bets = result_analysis.get('top_bets', [])
        if top_bets:
            print(f"\nTOP 3 APOSTAS RECOMENDADAS:")
            for i, bet in enumerate(top_bets[:3], 1):
                market = bet.get('market_display', 'N/A')
                prob = bet.get('probability', 0) * 100
                odd = bet.get('market_odd', 0)
                ev = bet.get('ev_pct', 0)
                
                print(f"\n  #{i}: {market}")
                print(f"      Probabilidade: {prob:.1f}%")
                print(f"      Odd Mercado: {odd:.2f}")
                print(f"      EV: {ev:+.1f}%")
                
                # Verificar se acertou
                market_key = bet.get('market', '')
                bet_won = False
                
                if 'over_2_5' in market_key and total_gols > 2:
                    bet_won = True
                elif 'btts' in market_key and home_score > 0 and away_score > 0:
                    bet_won = True
                elif market_key == 'home_win' and result_code == 'home':
                    bet_won = True
                elif market_key == 'away_win' and result_code == 'away':
                    bet_won = True
                elif market_key == 'draw' and result_code == 'draw':
                    bet_won = True
                
                if bet_won:
                    print(f"      RESULTADO: ACERTOU!")
                else:
                    print(f"      RESULTADO: Errou")
        
        # Comparação final
        print(f"\n" + "="*80)
        print("AVALIACAO FINAL")
        print("="*80)
        
        print(f"\nPrevisao 1X2: {pred_map.get(pred, pred)}")
        print(f"Real 1X2: {result_text}")
        
        correct_1x2 = (pred == result_code)
        print(f"\nResultado 1X2: {'ACERTOU!' if correct_1x2 else 'ERROU'}")
        
        # Probabilidade atribuída
        probs_dict = {'home': home_p, 'draw': draw_p, 'away': away_p}
        real_prob = probs_dict.get(result_code, 0)
        
        print(f"\nProbabilidade atribuida ao resultado real: {real_prob:.1f}%")
        
        if real_prob >= 50:
            calibration = "EXCELENTE - Sistema tinha alta confianca"
        elif real_prob >= 40:
            calibration = "BOM - Sistema identificou como provavel"
        elif real_prob >= 33:
            calibration = "RAZOAVEL - Sistema viu como possivel"
        else:
            calibration = "RUIM - Sistema subestimou resultado"
        
        print(f"Calibracao: {calibration}")
        
        # Over 2.5 e BTTS
        print(f"\nMercados Secundarios:")
        print(f"  Over 2.5: Real={over_25}")
        print(f"  BTTS: Real={btts}")
        
        # Resumo de acurácia
        print(f"\n" + "="*80)
        print("RESUMO DE ACURACIA")
        print("="*80)
        print(f"1X2: {'CORRETO' if correct_1x2 else 'INCORRETO'}")
        print(f"xG Casa: {home_xg:.2f} vs Real {home_score} (erro: {xg_error_home:.2f})")
        print(f"xG Fora: {away_xg:.2f} vs Real {away_score} (erro: {xg_error_away:.2f})")
        print(f"Total de Gols: Previsto {home_xg + away_xg:.2f} vs Real {total_gols} (erro: {abs((home_xg + away_xg) - total_gols):.2f})")
        
    except Exception as e:
        print(f"\nErro na analise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
