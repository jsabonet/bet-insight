"""
Treinar modelo de calibração para previsões xG do Poisson
Usa isotonic regression para mapear previsões Poisson → xG real

Com 1,343 partidas disponíveis:
- 80% treinamento (1,074 partidas)
- 20% teste (269 partidas)
"""
import os
import sys
import django
import numpy as np
import json
from datetime import datetime
from pathlib import Path

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from sklearn.isotonic import IsotonicRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle

print("=" * 80)
print("TREINAMENTO: Calibração xG Poisson → xG Real")
print("=" * 80)

# ============================================================================
# 1. CARREGAR DADOS
# ============================================================================

print("\n🔍 [1/5] Carregando partidas com xG real...")

# Buscar todas as partidas com xG real
matches = Match.objects.filter(
    home_score__isnull=False,
    away_score__isnull=False,
    stats_cache__isnull=False
).exclude(stats_cache='').select_related('home_team', 'away_team', 'league')

# Filtrar apenas as que têm xG real no stats_cache
matches_with_xg = []
for match in matches:
    if isinstance(match.stats_cache, list):
        has_xg = False
        for team_stats in match.stats_cache:
            statistics = team_stats.get('statistics', [])
            for stat in statistics:
                if 'expected' in stat.get('type', '').lower():
                    has_xg = True
                    break
            if has_xg:
                break
        if has_xg:
            matches_with_xg.append(match)

print(f"✅ {len(matches_with_xg)} partidas com xG real encontradas")

if len(matches_with_xg) < 100:
    print(f"❌ ERRO: Apenas {len(matches_with_xg)} partidas disponíveis")
    print("   Mínimo necessário: 100 partidas")
    sys.exit(1)

# ============================================================================
# 2. EXTRAIR xG REAL E PREVER xG POISSON
# ============================================================================

print("\n⚙️  [2/5] Calculando previsões Poisson e extraindo xG real...")

# Usar distribuição de Poisson para calcular xG esperado
# Lambda será estimado baseado nos gols reais + vantagem casa

X_poisson_home = []  # Previsões Poisson para casa
X_poisson_away = []  # Previsões Poisson para fora
y_real_home = []     # xG real casa
y_real_away = []     # xG real fora
match_info = []      # Info para debug

processed = 0
skipped = 0

for match in matches_with_xg:
    try:
        # Extrair xG real do stats_cache
        xg_home_real = None
        xg_away_real = None
        
        if isinstance(match.stats_cache, list) and len(match.stats_cache) >= 2:
            # Primeiro time (geralmente casa)
            stats_home = match.stats_cache[0].get('statistics', [])
            for stat in stats_home:
                if 'expected' in stat.get('type', '').lower():
                    xg_value = stat.get('value')
                    if xg_value is not None:
                        try:
                            xg_home_real = float(xg_value)
                        except (ValueError, TypeError):
                            pass
                    break
            
            # Segundo time (geralmente fora)
            stats_away = match.stats_cache[1].get('statistics', [])
            for stat in stats_away:
                if 'expected' in stat.get('type', '').lower():
                    xg_value = stat.get('value')
                    if xg_value is not None:
                        try:
                            xg_away_real = float(xg_value)
                        except (ValueError, TypeError):
                            pass
                    break
        
        if xg_home_real is None or xg_away_real is None:
            skipped += 1
            continue
        
        # Calcular xG "Poisson bruto" usando gols reais + ajustes
        # Esta é uma aproximação para treinar o calibrador
        # Em produção, usaremos o modelo real, mas aqui queremos capturar
        # a relação geral entre previsões baseadas em força e xG real
        
        home_goals = match.home_score
        away_goals = match.away_score
        
        # Estimar lambda do Poisson baseado nos gols + liga
        home_advantage = 1.07  # Default
        
        # Lambda casa: gols casa esperados (média histórica ~1.5 + vantagem)
        # Usar gols reais como proxy da força
        lambda_home = max(0.3, min(4.0, home_goals * 0.8 + 0.5))  # Clip entre 0.3 e 4.0
        lambda_away = max(0.3, min(4.0, away_goals * 0.8 + 0.3))  # Visitante geralmente menos
        
        # Aplicar vantagem casa
        lambda_home *= home_advantage
        
        # xG Poisson = lambda (média da distribuição de Poisson)
        xg_poisson_home = lambda_home
        xg_poisson_away = lambda_away
        
        # Adicionar aos arrays
        X_poisson_home.append(xg_poisson_home)
        X_poisson_away.append(xg_poisson_away)
        y_real_home.append(xg_home_real)
        y_real_away.append(xg_away_real)
        
        match_info.append({
            'id': match.id,
            'date': match.match_date.isoformat(),
            'home': match.home_team.name,
            'away': match.away_team.name,
            'league': match.league.name,
            'score': f"{match.home_score}-{match.away_score}",
            'xg_real': f"{xg_home_real:.2f}-{xg_away_real:.2f}",
            'xg_poisson': f"{xg_poisson_home:.2f}-{xg_poisson_away:.2f}"
        })
        
        processed += 1
        
        if processed % 100 == 0:
            print(f"   Processadas: {processed}/{len(matches_with_xg)}")
    
    except Exception as e:
        skipped += 1
        continue

print(f"\n✅ Dados processados:")
print(f"   Total de observações: {processed * 2} (casa + fora)")
print(f"   Partidas processadas: {processed}")
print(f"   Partidas ignoradas: {skipped}")

# Combinar casa + fora em um único dataset
X_poisson = np.array(X_poisson_home + X_poisson_away)
y_real = np.array(y_real_home + y_real_away)

print(f"\n📊 Dataset final:")
print(f"   Tamanho: {len(X_poisson)} observações")
print(f"   xG Poisson range: [{X_poisson.min():.2f}, {X_poisson.max():.2f}]")
print(f"   xG Real range: [{y_real.min():.2f}, {y_real.max():.2f}]")

# ============================================================================
# 3. SPLIT TREINO/TESTE
# ============================================================================

print("\n🔀 [3/5] Dividindo em treino e teste (80/20)...")

X_train, X_test, y_train, y_test = train_test_split(
    X_poisson, y_real, 
    test_size=0.2, 
    random_state=42
)

print(f"   Treino: {len(X_train)} observações")
print(f"   Teste: {len(X_test)} observações")

# ============================================================================
# 4. TREINAR ISOTONIC REGRESSION
# ============================================================================

print("\n🧠 [4/5] Treinando IsotonicRegression...")

calibrator = IsotonicRegression(
    y_min=0.0,    # xG mínimo
    y_max=10.0,   # xG máximo (limite superior realista)
    increasing=True,  # Relação monotônica crescente
    out_of_bounds='clip'  # Clipar valores fora do range treinado
)

calibrator.fit(X_train, y_train)

print("✅ Modelo treinado")

# ============================================================================
# 5. VALIDAÇÃO
# ============================================================================

print("\n📈 [5/5] Validando modelo...")

# Previsões
y_train_pred = calibrator.predict(X_train)
y_test_pred = calibrator.predict(X_test)

# Métricas - TREINO
mae_train = mean_absolute_error(y_train, y_train_pred)
rmse_train = np.sqrt(mean_squared_error(y_train, y_train_pred))
mape_train = np.mean(np.abs((y_train - y_train_pred) / (y_train + 0.1))) * 100

# Métricas - TESTE
mae_test = mean_absolute_error(y_test, y_test_pred)
rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))
mape_test = np.mean(np.abs((y_test - y_test_pred) / (y_test + 0.1))) * 100

# Métricas - ANTES DA CALIBRAÇÃO (Poisson bruto)
mae_before = mean_absolute_error(y_test, X_test)
rmse_before = np.sqrt(mean_squared_error(y_test, X_test))
mape_before = np.mean(np.abs((y_test - X_test) / (y_test + 0.1))) * 100

print("\n" + "=" * 80)
print("RESULTADOS DA CALIBRAÇÃO")
print("=" * 80)

print("\n📊 MÉTRICAS DE TREINO:")
print(f"   MAE:  {mae_train:.4f}")
print(f"   RMSE: {rmse_train:.4f}")
print(f"   MAPE: {mape_train:.2f}%")

print("\n📊 MÉTRICAS DE TESTE:")
print(f"   MAE:  {mae_test:.4f}")
print(f"   RMSE: {rmse_test:.4f}")
print(f"   MAPE: {mape_test:.2f}%")

print("\n📊 ANTES DA CALIBRAÇÃO (Poisson bruto):")
print(f"   MAE:  {mae_before:.4f}")
print(f"   RMSE: {rmse_before:.4f}")
print(f"   MAPE: {mape_before:.2f}%")

print("\n📊 MELHORIA:")
mae_improvement = ((mae_before - mae_test) / mae_before) * 100
rmse_improvement = ((rmse_before - rmse_test) / rmse_before) * 100
mape_improvement = ((mape_before - mape_test) / mape_before) * 100

print(f"   MAE:  {mae_improvement:+.1f}%")
print(f"   RMSE: {rmse_improvement:+.1f}%")
print(f"   MAPE: {mape_improvement:+.1f}%")

# Exemplos de calibração
print("\n📋 EXEMPLOS DE CALIBRAÇÃO:")
print("-" * 80)
print(f"{'xG Poisson':<15} {'xG Calibrado':<15} {'xG Real':<15} {'Erro Antes':<15} {'Erro Depois':<15}")
print("-" * 80)

# Mostrar 10 exemplos aleatórios do conjunto de teste
np.random.seed(42)
sample_indices = np.random.choice(len(X_test), min(10, len(X_test)), replace=False)

for idx in sample_indices:
    poisson_val = X_test[idx]
    calibrated_val = y_test_pred[idx]
    real_val = y_test[idx]
    error_before = abs(poisson_val - real_val)
    error_after = abs(calibrated_val - real_val)
    
    print(f"{poisson_val:<15.3f} {calibrated_val:<15.3f} {real_val:<15.3f} {error_before:<15.3f} {error_after:<15.3f}")

# ============================================================================
# 6. SALVAR MODELO
# ============================================================================

print("\n💾 Salvando modelo...")

# Criar diretório se não existir
model_dir = Path(__file__).parent / 'ml_models'
model_dir.mkdir(exist_ok=True)

# Salvar modelo
model_path = model_dir / 'xg_calibration_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(calibrator, f)

print(f"✅ Modelo salvo em: {model_path}")

# Salvar metadados
metadata = {
    'trained_at': datetime.now().isoformat(),
    'n_samples_total': len(X_poisson),
    'n_samples_train': len(X_train),
    'n_samples_test': len(X_test),
    'n_matches': processed,
    'metrics_train': {
        'mae': float(mae_train),
        'rmse': float(rmse_train),
        'mape': float(mape_train)
    },
    'metrics_test': {
        'mae': float(mae_test),
        'rmse': float(rmse_test),
        'mape': float(mape_test)
    },
    'metrics_before': {
        'mae': float(mae_before),
        'rmse': float(rmse_before),
        'mape': float(mape_before)
    },
    'improvement': {
        'mae_pct': float(mae_improvement),
        'rmse_pct': float(rmse_improvement),
        'mape_pct': float(mape_improvement)
    },
    'date_range': {
        'min': min([m['date'] for m in match_info]),
        'max': max([m['date'] for m in match_info])
    }
}

metadata_path = model_dir / 'xg_calibration_metadata.json'
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"✅ Metadados salvos em: {metadata_path}")

# Salvar exemplos de partidas para análise posterior
sample_matches_path = model_dir / 'xg_calibration_sample_matches.json'
with open(sample_matches_path, 'w', encoding='utf-8') as f:
    json.dump(match_info[:100], f, indent=2, ensure_ascii=False)

print(f"✅ Exemplos salvos em: {sample_matches_path}")

print("\n" + "=" * 80)
print("✅ CALIBRAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 80)

print("\n💡 PRÓXIMOS PASSOS:")
print("   1. Integrar calibrador no PoissonModel")
print("   2. Atualizar análises para usar xG calibrado")
print("   3. Testar em partidas recentes")
print("   4. Monitorar melhoria nas previsões")

print("\n" + "=" * 80)
