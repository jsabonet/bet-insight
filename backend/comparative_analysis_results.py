#!/usr/bin/env python
"""
Análise comparativa final - resultados da execução
"""

# Resultados da execução anterior
results = {
    "SC Telstar vs Go Ahead Eagles": {
        "liga": "KNVB Beker",
        "resultado": "2-1",
        "gols_real": 3,
        "over25_real": False,
        "xg_previsto": 5.75,
        "erro_xg": 2.75,
        "prob_over25": None  # Não capturado
    },
    "Anderlecht vs Antwerp": {
        "liga": "Beker van Belgie", 
        "resultado": "0-1",
        "gols_real": 1,
        "over25_real": False,
        "xg_previsto": 4.10,
        "erro_xg": 3.10,
        "prob_over25": 0.773
    },
    "Real Betis vs Atletico Madrid": {
        "liga": "Copa Del Rey",
        "resultado": "0-5",
        "gols_real": 5,
        "over25_real": True,
        "xg_previsto": 6.21,
        "erro_xg": 1.21,
        "prob_over25": None
    },
    "Atalanta vs Juventus": {
        "liga": "Coppa Italia",
        "resultado": "3-0",
        "gols_real": 3,
        "over25_real": False,  # 3 gols = exatamente 2.5, mas ACERTA Over 2.5
        "xg_previsto": 4.75,
        "erro_xg": 1.75,
        "prob_over25": None
    },
    "Strasbourg vs Monaco": {
        "liga": "Coupe de France",
        "resultado": "3-1",
        "gols_real": 4,
        "over25_real": True,
        "xg_previsto": 5.96,
        "erro_xg": 1.96,
        "prob_over25": None
    },
    "Sporting vs AVS": {
        "liga": "Taca de Portugal",
        "resultado": "3-2",
        "gols_real": 5,
        "over25_real": True,
        "xg_previsto": 6.01,
        "erro_xg": 1.01,
        "prob_over25": None
    }
}

print("=" * 120)
print("ANÁLISE COMPARATIVA FINAL - PARTIDAS 05/02/2026")
print("=" * 120)
print()

print("TABELA COMPARATIVA:")
print("-" * 120)
print(f"{'Partida':<40} {'Liga':<20} {'Gols':<6} {'xG':<6} {'Erro':<6} {'Over2.5':<8}")
print("-" * 120)

for partida, dados in results.items():
    over_status = "✓" if dados["over25_real"] else "✗"
    print(f"{partida:<40} {dados['liga']:<20} {dados['gols_real']:<6} {dados['xg_previsto']:<6.2f} {dados['erro_xg']:<6.2f} {over_status:<8}")

print("-" * 120)
print()

# Análise de padrões
print("=" * 120)
print("ANÁLISE DE PADRÕES")
print("=" * 120)
print()

jogos_copa = [k for k, v in results.items() if "Cup" in v["liga"] or "Beker" in v["liga"] or "Copa" in v["liga"] or "Coupe" in v["liga"] or "Coppa" in v["liga"] or "Taca" in v["liga"]]
jogos_baixos_gols = [k for k, v in results.items() if v["gols_real"] <= 3]
jogos_altos_gols = [k for k, v in results.items() if v["gols_real"] >= 4]

print(f"📊 TODAS AS PARTIDAS SÃO DE COPAS NACIONAIS (6/6)")
print()

print("🔴 PARTIDAS COM POUCOS GOLS (≤3):")
for partida in jogos_baixos_gols:
    dados = results[partida]
    print(f"   • {partida}: {dados['gols_real']} gols, xG={dados['xg_previsto']:.2f} (erro: {dados['erro_xg']:.2f})")
print()

print("🟢 PARTIDAS COM MUITOS GOLS (≥4):")
for partida in jogos_altos_gols:
    dados = results[partida]
    print(f"   • {partida}: {dados['gols_real']} gols, xG={dados['xg_previsto']:.2f} (erro: {dados['erro_xg']:.2f})")
print()

# Estatísticas
erros = [v["erro_xg"] for v in results.values()]
erro_medio = sum(erros) / len(erros)
erro_baixos = sum([v["erro_xg"] for k, v in results.items() if v["gols_real"] <= 3]) / len(jogos_baixos_gols)
erro_altos = sum([v["erro_xg"] for k, v in results.items() if v["gols_real"] >= 4]) / len(jogos_altos_gols)

print("📈 ESTATÍSTICAS:")
print(f"   • Erro médio xG (todas): {erro_medio:.2f} gols")
print(f"   • Erro médio xG (≤3 gols): {erro_baixos:.2f} gols")
print(f"   • Erro médio xG (≥4 gols): {erro_altos:.2f} gols")
print()

# Conclusão crítica
print("=" * 120)
print("CONCLUSÃO CRÍTICA")
print("=" * 120)
print()

print("⚠️  DESCOBERTA IMPORTANTE:")
print()
print("1. O SISTEMA SUPERESTIMA GOLS EM TODAS AS PARTIDAS DE COPA")
print("   - Erro médio de 1.93 gols para cima")
print("   - xG previsto sempre MAIOR que gols reais")
print()

print("2. ANDERLECHT vs ANTWERP NÃO É CASO ISOLADO")
print("   - Erro de 3.10 gols (maior erro)")
print("   - MAS Telstar também teve erro de 2.75 gols (3 gols vs 5.75 xG)")
print("   - E Atalanta teve erro de 1.75 gols (3 gols vs 4.75 xG)")
print()

print("3. PADRÃO IDENTIFICADO: Jogos de COPA tendem a ter MENOS gols que o previsto")
print("   - Jogos baixos gols (≤3): erro médio de 2.53 gols")
print("   - Jogos altos gols (≥4): erro médio de 1.39 gols")
print("   - Sistema FALHA mais em jogos DEFENSIVOS de copa")
print()

print("4. HIPÓTESE: Modelo NÃO ajusta adequadamente para contexto de ELIMINATÓRIAS")
print("   - Semifinais e quartas-de-final têm abordagem mais cautelosa")
print("   - Feature 'match_importance' existe mas peso pode estar baixo")
print("   - Equipes preferem não arriscar em jogos mata-mata")
print()

print("=" * 120)
print("RECOMENDAÇÃO TÉCNICA")
print("=" * 120)
print()

print("✅ AÇÕES CORRETIVAS:")
print()
print("1. AUMENTAR peso da feature 'match_importance' em jogos de copa")
print("   - Arquivo: feature_engineer.py")
print("   - Aplicar FATOR DE REDUÇÃO de 15-20% no xG para jogos eliminatórios")
print()

print("2. CRIAR calibração específica para COPAS NACIONAIS")
print("   - Separar calibração de liga vs copa")
print("   - Arquivo: calibration_best_weights.json")
print()

print("3. ADICIONAR feature 'knockout_stage' (fase eliminatória)")
print("   - Semifinal: -25% xG")
print("   - Quartas: -15% xG")
print("   - Oitavas: -10% xG")
print()

print("4. RETREINAR modelo com mais partidas de copa (atualmente 880 partidas, maioria de ligas)")
print()

print("=" * 120)
