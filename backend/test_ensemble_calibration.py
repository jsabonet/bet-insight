"""
Teste de Calibração do Ensemble
Valida melhorias: 50% Poisson + 35% Logística + 15% Market Prior
"""
import os
import sys

# Setup path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.analysis.services.statistical_models import PoissonBivariateModel, LogisticRegressionModel
from apps.analysis.services.decision_engine import DecisionEngine

print("="*80)
print("TESTE DE CALIBRAÇÃO DO ENSEMBLE")
print("="*80)
print()

# Modelo Poisson
poisson = PoissonBivariateModel()
logistic = LogisticRegressionModel()

# TESTE 1: Burnley vs Tottenham (favorito claro fora)
print("\n" + "="*80)
print("TESTE 1: Burnley vs Tottenham")
print("="*80)

# Dados reais do jogo
home_strength = 1.1  # Burnley fraco
away_strength = 1.8  # Tottenham forte
home_defense = 1.6   # Burnley defesa fraca (sofre muitos gols)
away_defense = 1.2   # Tottenham defesa razoável
league_id = 39  # Premier League

# Poisson (COM DEFESA)
poisson_pred = poisson.predict(
    home_strength=home_strength,
    away_strength=away_strength,
    weather_impact=0.0,
    league_id=league_id,
    home_defense=home_defense,
    away_defense=away_defense
)

# Logística (COM NOVAS FEATURES)
features = {
    'strength': {
        'strength_differential': home_strength - away_strength,  # -0.7 (Burnley mais fraco)
    },
    'form': {
        'adjusted_form_diff': -0.5,  # Tottenham melhor forma (negativo = fora melhor)
        'home_momentum': -0.2,       # Burnley perdendo momentum
        'away_momentum': 0.3         # Tottenham ganhando momentum
    },
    'statistics': {
        'home_variance': 1.2,        # Burnley inconsistente
        'away_variance': 0.8,        # Tottenham consistente
        'home_corners': 4.5,         # Burnley menos domínio
        'away_corners': 6.2,         # Tottenham mais domínio
        'home_clean_sheets': 0.15,   # Burnley raramente mantém clean sheet
        'away_clean_sheets': 0.35,   # Tottenham defensiva sólida
        'home_discipline': 2.3,      # Burnley mais cartões
        'away_discipline': 1.8       # Tottenham mais disciplinado
    },
    'context': {
        'rest_advantage': 0
    },
    'motivation': {
        'motivation_differential': -0.2  # Tottenham mais motivado
    },
    'injuries_suspensions': {
        'injury_impact_differential': 0.0
    },
    'match_importance': {
        'match_importance': 6.0
    },
    'h2h': {
        'h2h_home_win_rate': 0.3  # Tottenham domina H2H (30% casa = fora melhor)
    },
    'elo': {
        'elo_diff': -150  # Tottenham muito superior (negativo = fora melhor)
    }
}

logistic_pred = logistic.predict_1x2(features)

# Market Odds (baseado em odds reais)
market_odds = {
    'odds_home': 3.7,   # Burnley (underdog)
    'odds_draw': 3.6,   # Empate
    'odds_away': 2.46   # Tottenham (favorito)
}

# Calcular Market Prior
def calculate_market_prior(odds):
    prob_home = 1 / odds['odds_home']
    prob_draw = 1 / odds['odds_draw']
    prob_away = 1 / odds['odds_away']
    total = prob_home + prob_draw + prob_away
    return {
        'home_win': prob_home / total,
        'draw': prob_draw / total,
        'away_win': prob_away / total
    }

market_prior = calculate_market_prior(market_odds)

# Ensemble ANTIGO (60% Poisson + 40% Logística)
print("\n" + "-"*80)
print("ENSEMBLE ANTIGO (60% Poisson + 40% Logística)")
print("-"*80)

consensus_old = {
    'home_win': poisson_pred['probabilities']['home_win'] * 0.6 + logistic_pred['home_win'] * 0.4,
    'draw': poisson_pred['probabilities']['draw'] * 0.6 + logistic_pred['draw'] * 0.4,
    'away_win': poisson_pred['probabilities']['away_win'] * 0.6 + logistic_pred['away_win'] * 0.4,
}

print(f"Burnley (Casa): {consensus_old['home_win']*100:.1f}%")
print(f"Empate:         {consensus_old['draw']*100:.1f}%")
print(f"Tottenham (Fora): {consensus_old['away_win']*100:.1f}%")

# Ensemble NOVO (50% Poisson + 35% Logística + 15% Market)
print("\n" + "-"*80)
print("ENSEMBLE NOVO (50% Poisson + 35% Logística + 15% Market Prior)")
print("-"*80)

W_POISSON = 0.50
W_LOGISTIC = 0.35
W_MARKET = 0.15

consensus_new = {
    'home_win': (
        poisson_pred['probabilities']['home_win'] * W_POISSON +
        logistic_pred['home_win'] * W_LOGISTIC +
        market_prior['home_win'] * W_MARKET
    ),
    'draw': (
        poisson_pred['probabilities']['draw'] * W_POISSON +
        logistic_pred['draw'] * W_LOGISTIC +
        market_prior['draw'] * W_MARKET
    ),
    'away_win': (
        poisson_pred['probabilities']['away_win'] * W_POISSON +
        logistic_pred['away_win'] * W_LOGISTIC +
        market_prior['away_win'] * W_MARKET
    ),
}

# Normalizar
total = sum(consensus_new.values())
consensus_new = {k: v/total for k, v in consensus_new.items()}

print(f"Burnley (Casa): {consensus_new['home_win']*100:.1f}%")
print(f"Empate:         {consensus_new['draw']*100:.1f}%")
print(f"Tottenham (Fora): {consensus_new['away_win']*100:.1f}%")

# Comparação
print("\n" + "-"*80)
print("ANÁLISE COMPARATIVA")
print("-"*80)

print(f"\nModelos Individuais:")
print(f"   Poisson:    Casa={poisson_pred['probabilities']['home_win']*100:.1f}% | Empate={poisson_pred['probabilities']['draw']*100:.1f}% | Fora={poisson_pred['probabilities']['away_win']*100:.1f}%")
print(f"   Logística:  Casa={logistic_pred['home_win']*100:.1f}% | Empate={logistic_pred['draw']*100:.1f}% | Fora={logistic_pred['away_win']*100:.1f}%")
print(f"   Market:     Casa={market_prior['home_win']*100:.1f}% | Empate={market_prior['draw']*100:.1f}% | Fora={market_prior['away_win']*100:.1f}%")

print(f"\nDiferença Antigo vs Novo:")
print(f"   Casa:  {consensus_old['home_win']*100:.1f}% → {consensus_new['home_win']*100:.1f}% ({(consensus_new['home_win']-consensus_old['home_win'])*100:+.1f}pp)")
print(f"   Empate: {consensus_old['draw']*100:.1f}% → {consensus_new['draw']*100:.1f}% ({(consensus_new['draw']-consensus_old['draw'])*100:+.1f}pp)")
print(f"   Fora:  {consensus_old['away_win']*100:.1f}% → {consensus_new['away_win']*100:.1f}% ({(consensus_new['away_win']-consensus_old['away_win'])*100:+.1f}pp)")

print(f"\nRecomendação:")
max_old = max(consensus_old, key=consensus_old.get)
max_new = max(consensus_new, key=consensus_new.get)
print(f"   Antigo: {max_old} ({consensus_old[max_old]*100:.1f}%)")
print(f"   Novo:   {max_new} ({consensus_new[max_new]*100:.1f}%)")

if max_old == max_new:
    print(f"   ✅ Ambos recomendam: {max_new}")
else:
    print(f"   ⚠️ Divergência! Antigo={max_old} vs Novo={max_new}")

# VALIDAÇÃO
print("\n" + "="*80)
print("VALIDAÇÃO")
print("="*80)

# Resultado real conhecido: Tottenham venceu
resultado_real = "away_win"

if max_new == resultado_real:
    print(f"✅ ENSEMBLE NOVO ACERTOU! Previu {max_new} com {consensus_new[max_new]*100:.1f}%")
else:
    print(f"❌ ENSEMBLE NOVO ERROU. Previu {max_new} mas resultado foi {resultado_real}")

if max_old == resultado_real:
    print(f"✅ ENSEMBLE ANTIGO ACERTOU! Previu {max_old} com {consensus_old[max_old]*100:.1f}%")
else:
    print(f"❌ ENSEMBLE ANTIGO ERROU. Previu {max_old} mas resultado foi {resultado_real}")

print("\n" + "="*80)
print("CONCLUSÃO")
print("="*80)
print()
print("Melhorias implementadas:")
print("✅ Ensemble 50/35/15 (Poisson/Logística/Market)")
print("✅ Market Prior adiciona sabedoria das odds")
print("✅ Home Advantage calibrado por liga (Premier=1.10)")
print("✅ Features de lesões, H2H e ELO no Logístico")
print()
print("Próximos passos:")
print("- Testar com mais jogos (>100)")
print("- Ajustar pesos dinamicamente baseado em confiança")
print("- Adicionar forma recente dos times")
print()
