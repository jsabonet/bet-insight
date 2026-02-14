"""
Análise detalhada do dataset de copas (FA Cup)
"""
import json
import os
from collections import Counter

print("="*80)
print("DATASET DE COPAS - FA CUP (450 PARTIDAS)")
print("="*80)
print()

# Ler o arquivo
with open("ml_training/cup_training_dataset.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

metadata = data.get('metadata', {})
matches = data.get('matches', [])

print("METADADOS:")
print("-" * 80)
for key, value in metadata.items():
    print(f"  {key}: {value}")

print()
print("="*80)
print("ANÁLISE DAS PARTIDAS")
print("="*80)
print()

print(f"Total de partidas: {len(matches)}")
print()

# Análise por temporada
seasons = Counter([m['season'] for m in matches])
print("Distribuição por temporada:")
print("-" * 80)
for season, count in sorted(seasons.items()):
    print(f"  Temporada {season}: {count:3d} partidas")

print()

# Análise por fase
rounds = Counter([m.get('round', 'N/A') for m in matches])
print("Distribuição por fase:")
print("-" * 80)
for round_name, count in rounds.most_common():
    print(f"  {round_name:40s}: {count:3d} partidas")

print()

# Análise de knockout vs grupos
knockout_count = sum(1 for m in matches if m.get('is_knockout', False))
print(f"Partidas knockout: {knockout_count}/{len(matches)} ({knockout_count/len(matches)*100:.1f}%)")
print(f"Partidas de grupos/fase: {len(matches) - knockout_count}/{len(matches)} ({(len(matches) - knockout_count)/len(matches)*100:.1f}%)")

print()

# Top times
teams = Counter()
for m in matches:
    teams[m['teams']['home']] += 1
    teams[m['teams']['away']] += 1

print("Top 30 times mais frequentes:")
print("-" * 80)
for team, count in teams.most_common(30):
    print(f"  {team:40s}: {count:3d} partidas")

print()

# Estatísticas de gols
total_goals = [m['result']['total_goals'] for m in matches]
home_goals = [m['result']['home_goals'] for m in matches]
away_goals = [m['result']['away_goals'] for m in matches]

print("Estatísticas de gols:")
print("-" * 80)
print(f"  Total de gols (média): {sum(total_goals)/len(total_goals):.2f}")
print(f"  Gols casa (média): {sum(home_goals)/len(home_goals):.2f}")
print(f"  Gols fora (média): {sum(away_goals)/len(away_goals):.2f}")
print(f"  Gols mínimo: {min(total_goals)}")
print(f"  Gols máximo: {max(total_goals)}")

print()

# Distribuição de resultados
winners = Counter([m['result']['winner'] for m in matches])
print("Distribuição de resultados:")
print("-" * 80)
for winner, count in winners.items():
    print(f"  {winner:10s}: {count:3d} partidas ({count/len(matches)*100:.1f}%)")

print()

# Labels (1X2)
labels = Counter([m['label'] for m in matches])
print("Distribuição de labels (1X2):")
print("-" * 80)
label_names = {1: 'Casa (1)', 0: 'Empate (X)', 2: 'Fora (2)'}
for label, count in sorted(labels.items()):
    print(f"  {label_names.get(label, f'Label {label}'):15s}: {count:3d} partidas ({count/len(matches)*100:.1f}%)")

print()

# Verificar features disponíveis
if matches:
    first_match_features = matches[0].get('features', {})
    print(f"Total de features por partida: {len(first_match_features)}")
    print()
    print("Lista de features disponíveis:")
    print("-" * 80)
    
    # Agrupar por categoria
    features_by_category = {}
    for feature_name in sorted(first_match_features.keys()):
        category = feature_name.split('.')[0] if '.' in feature_name else 'other'
        if category not in features_by_category:
            features_by_category[category] = []
        features_by_category[category].append(feature_name)
    
    for category, feature_list in sorted(features_by_category.items()):
        print(f"\n  [{category.upper()}] - {len(feature_list)} features:")
        for feature in feature_list[:10]:  # Mostrar primeiras 10
            value = first_match_features[feature]
            print(f"    {feature:50s} = {value}")
        if len(feature_list) > 10:
            print(f"    ... e mais {len(feature_list) - 10} features")

print()
print("="*80)
print("AMOSTRA DE 10 PARTIDAS")
print("="*80)
print()

for i, match in enumerate(matches[:10], 1):
    teams = match['teams']
    result = match['result']
    print(f"{i:2d}. Temporada {match['season']} - {match['round']}")
    print(f"    {teams['home']} {result['home_goals']}-{result['away_goals']} {teams['away']}")
    print(f"    Total gols: {result['total_goals']} | Vencedor: {result['winner']} | Label: {match['label']}")
    print()

print("="*80)
