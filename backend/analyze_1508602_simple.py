"""
Análise simplificada da partida 1508602
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService

def main():
    fixture_id = 1508602
    
    # Buscar detalhes da API
    api = APIFootballService()
    details = api.fetch_fixture_details(fixture_id)
    
    if not details:
        print(f"Erro: Partida {fixture_id} nao encontrada")
        return
    
    # Informações básicas
    home = details['home_team']['name']
    away = details['away_team']['name']
    league = details['league']['name']
    date = details.get('date', 'N/A')
    status = details.get('status', 'N/A')
    
    print("\n" + "="*80)
    print(f"PARTIDA: {home} vs {away}")
    print(f"LIGA: {league}")
    print(f"DATA: {date}")
    print(f"STATUS: {status}")
    print("="*80)
    
    # Resultado
    home_score = details.get('home_score')
    away_score = details.get('away_score')
    
    if home_score is not None and away_score is not None:
        print(f"\nRESULTADO: {home} {home_score} x {away_score} {away}")
        
        if home_score > away_score:
            result = "Vitoria Casa"
            result_code = "home"
        elif away_score > home_score:
            result = "Vitoria Fora"
            result_code = "away"
        else:
            result = "Empate"
            result_code = "draw"
        
        print(f"RESULTADO: {result}")
        
        # Mercados
        total = home_score + away_score
        over_25 = "SIM" if total > 2 else "NAO"
        btts = "SIM" if home_score > 0 and away_score > 0 else "NAO"
        
        print(f"\nMERCADOS:")
        print(f"  Over 2.5: {over_25} (Total: {total} gols)")
        print(f"  BTTS: {btts}")
        
        # Agora analisar com o sistema
        print("\n" + "="*80)
        print("ANALISE DO SISTEMA")
        print("="*80)
        
        from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
        
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
            pred_map = {'home': f'Vitoria Casa', 'draw': 'Empate', 'away': 'Vitoria Fora'}
            
            print(f"\nPREVISAO: {pred_map.get(pred, pred)}")
            
            # Confiança
            conf = result_analysis.get('confidence', {})
            if isinstance(conf, dict):
                stars = conf.get('stars', 0)
                level = conf.get('level', 'N/A')
            else:
                stars = conf
                level = 'N/A'
            
            print(f"CONFIANCA: {stars}/5 ({level})")
            
            # Probabilidades
            home_p = result_analysis.get('home_probability', 0)
            draw_p = result_analysis.get('draw_probability', 0)
            away_p = result_analysis.get('away_probability', 0)
            
            print(f"\nPROBABILIDADES 1X2:")
            print(f"  Casa: {home_p:.1f}%")
            print(f"  Empate: {draw_p:.1f}%")
            print(f"  Fora: {away_p:.1f}%")
            
            # Expected Goals
            home_xg = result_analysis.get('home_xg', 0)
            away_xg = result_analysis.get('away_xg', 0)
            
            print(f"\nEXPECTED GOALS (xG):")
            print(f"  {home}: {home_xg:.2f}")
            print(f"  {away}: {away_xg:.2f}")
            
            # Top Bets
            top_bets = result_analysis.get('top_bets', [])
            if top_bets:
                print(f"\nTOP 3 APOSTAS RECOMENDADAS:")
                for i, bet in enumerate(top_bets[:3], 1):
                    market = bet.get('market_display', 'N/A')
                    prob = bet.get('probability', 0) * 100
                    odd = bet.get('market_odd', 0)
                    ev = bet.get('ev_pct', 0)
                    
                    print(f"  #{i}: {market}")
                    print(f"      Prob: {prob:.1f}% | Odd: {odd:.2f} | EV: {ev:+.1f}%")
            
            # Comparação
            print(f"\n" + "="*80)
            print("COMPARACAO COM RESULTADO REAL")
            print("="*80)
            
            print(f"Previsao: {pred_map.get(pred, pred)}")
            print(f"Real: {result}")
            
            correct = (pred == result_code)
            print(f"\nRESULTADO: {'ACERTOU!' if correct else 'ERROU'}")
            
            # Probabilidade atribuída ao resultado real
            probs_dict = {'home': home_p, 'draw': draw_p, 'away': away_p}
            real_prob = probs_dict.get(result_code, 0)
            
            print(f"\nProbabilidade atribuida ao resultado real: {real_prob:.1f}%")
            
            if real_prob >= 50:
                print("Sistema tinha alta confianca no resultado correto")
            elif real_prob >= 33:
                print("Sistema considerou possivel mas nao favorito")
            else:
                print("Sistema subestimou a probabilidade do resultado real")
            
        except Exception as e:
            print(f"Erro na analise: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("\nResultado nao disponivel")

if __name__ == '__main__':
    main()
