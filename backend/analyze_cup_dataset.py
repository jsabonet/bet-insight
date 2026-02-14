"""
Analisa o dataset local de copas (cup_training_dataset.json)
"""
import json
import os
from collections import Counter
from datetime import datetime

print("="*80)
print("ANALISANDO DATASET LOCAL DE COPAS")
print("="*80)
print()

# Caminho do arquivo
cup_dataset_path = "ml_training/cup_training_dataset.json"

if not os.path.exists(cup_dataset_path):
    print(f"ERRO: Arquivo não encontrado: {cup_dataset_path}")
    exit(1)

print(f"Arquivo encontrado: {cup_dataset_path}")
print(f"Tamanho do arquivo: {os.path.getsize(cup_dataset_path) / 1024:.2f} KB")
print()

# Ler o arquivo
with open(cup_dataset_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*80)
print("ESTRUTURA DOS DADOS")
print("="*80)
print()

if isinstance(data, dict):
    print(f"Tipo: Dicionário")
    print(f"Chaves principais: {list(data.keys())}")
    
    if 'matches' in data:
        matches = data['matches']
        print(f"\nTotal de partidas: {len(matches)}")
        
        # Analisar primeira partida para ver estrutura
        if matches:
            print("\nEstrutura da primeira partida:")
            first_match = matches[0]
            for key, value in first_match.items():
                print(f"  {key}: {type(value).__name__} = {str(value)[:100]}")
    else:
        print(f"\nChave 'matches' não encontrada. Explorando outras chaves...")
        for key, value in data.items():
            if isinstance(value, list):
                print(f"\n  {key}: Lista com {len(value)} itens")
            else:
                print(f"\n  {key}: {type(value).__name__}")

elif isinstance(data, list):
    print(f"Tipo: Lista")
    print(f"Total de itens: {len(data)}")
    matches = data
    
    # Analisar primeira partida
    if matches:
        print("\nEstrutura do primeiro item:")
        first_match = matches[0]
        if isinstance(first_match, dict):
            for key, value in first_match.items():
                print(f"  {key}: {type(value).__name__} = {str(value)[:100]}")
else:
    print(f"Tipo desconhecido: {type(data)}")
    matches = []

print()
print("="*80)
print("ANÁLISE DAS PARTIDAS")
print("="*80)
print()

if matches:
    # Estatísticas
    total = len(matches)
    print(f"Total de partidas: {total}")
    
    # Ligas/Competições
    if isinstance(matches[0], dict):
        # Tentar identificar campo de liga
        league_field = None
        for field in ['league', 'competition', 'league_name', 'tournament']:
            if field in matches[0]:
                league_field = field
                break
        
        if league_field:
            leagues = Counter([m.get(league_field, 'Desconhecido') for m in matches])
            print(f"\nCompetições ({league_field}):")
            print("-" * 80)
            for league, count in leagues.most_common():
                print(f"  {league:50s} - {count:4d} partidas ({count/total*100:.1f}%)")
        
        # Datas
        date_field = None
        for field in ['date', 'match_date', 'datetime', 'fixture_date']:
            if field in matches[0]:
                date_field = field
                break
        
        if date_field:
            dates = [m.get(date_field) for m in matches if m.get(date_field)]
            if dates:
                print(f"\nPeríodo das partidas:")
                print(f"  Primeira partida: {min(dates)}")
                print(f"  Última partida: {max(dates)}")
        
        # Times
        home_field = None
        away_field = None
        for field in ['home_team', 'home', 'home_team_name']:
            if field in matches[0]:
                home_field = field
                break
        for field in ['away_team', 'away', 'away_team_name']:
            if field in matches[0]:
                away_field = field
                break
        
        if home_field and away_field:
            teams = Counter()
            for m in matches:
                teams[m.get(home_field, '')] += 1
                teams[m.get(away_field, '')] += 1
            
            print(f"\nTop 20 times mais frequentes:")
            print("-" * 80)
            for team, count in teams.most_common(20):
                print(f"  {team:40s} - {count:3d} partidas")
        
        # Resultados
        home_score_field = None
        away_score_field = None
        for field in ['home_score', 'home_goals', 'score_home']:
            if field in matches[0]:
                home_score_field = field
                break
        for field in ['away_score', 'away_goals', 'score_away']:
            if field in matches[0]:
                away_score_field = field
                break
        
        if home_score_field and away_score_field:
            with_score = [m for m in matches if m.get(home_score_field) is not None]
            print(f"\nPartidas com placar: {len(with_score)}/{total} ({len(with_score)/total*100:.1f}%)")
            
            if len(with_score) >= 10:
                print("\nAmostra de 10 partidas:")
                print("-" * 80)
                for i, m in enumerate(with_score[:10], 1):
                    date = m.get(date_field, 'N/A')
                    league = m.get(league_field, 'N/A')
                    home = m.get(home_field, 'N/A')
                    away = m.get(away_field, 'N/A')
                    score_home = m.get(home_score_field, 'N/A')
                    score_away = m.get(away_score_field, 'N/A')
                    print(f"{i:2d}. [{date}] {league:30s}")
                    print(f"    {home} {score_home}-{score_away} {away}")

print()
print("="*80)
print("VERIFICANDO OUTROS DATASETS")
print("="*80)
print()

other_datasets = [
    "ml_training/training_dataset.json",
    "ml_training/training_dataset_full.json",
    "ml_training/database_dataset.csv"
]

for dataset_path in other_datasets:
    if os.path.exists(dataset_path):
        size = os.path.getsize(dataset_path) / 1024
        print(f"  {dataset_path:60s} - {size:8.2f} KB")
    else:
        print(f"  {dataset_path:60s} - NAO ENCONTRADO")

print()
print("="*80)
