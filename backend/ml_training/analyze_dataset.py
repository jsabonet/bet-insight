import json

data = json.load(open('training_dataset_checkpoint.json'))

print('='*60)
print('DATASET DE LIGAS - 880 PARTIDAS')
print('='*60)

meta = data['metadata']
print(f'\nTotal partidas: {meta["total_matches"]}')
print(f'Coletado em: {meta["collected_at"]}')
print(f'\nLigas ({len(meta["leagues"])}):')
for l in meta['leagues']:
    print(f'  - {l}')

print(f'\nTemporadas: {meta["seasons"]}')

print(f'\nPrimeira partida:')
first = data['data'][0]
print(f'  {first["teams"]["home"]} vs {first["teams"]["away"]}')
print(f'  Liga: {first["league"]}')
print(f'  Data: {first["date"]}')
print(f'  Resultado: {first["result"]["home_goals"]}-{first["result"]["away_goals"]}')

print(f'\nTotal features por partida: {len(first["features"])}')

# Verificar labels disponíveis
labels_count = {0: 0, 1: 0, 2: 0}
for match in data['data']:
    home = match['result']['home_goals']
    away = match['result']['away_goals']
    
    if home > away:
        label = 0  # Home win
    elif home == away:
        label = 1  # Draw
    else:
        label = 2  # Away win
    
    labels_count[label] += 1

print(f'\nDistribuição de resultados (1X2):')
print(f'  Home Win (0): {labels_count.get(0, 0)} ({labels_count.get(0, 0)/len(data["data"])*100:.1f}%)')
print(f'  Draw (1): {labels_count.get(1, 0)} ({labels_count.get(1, 0)/len(data["data"])*100:.1f}%)')
print(f'  Away Win (2): {labels_count.get(2, 0)} ({labels_count.get(2, 0)/len(data["data"])*100:.1f}%)')

print('='*60)
