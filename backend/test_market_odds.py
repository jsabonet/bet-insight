"""
Script de teste para verificar se market_odds está sendo retornado corretamente
"""
import requests
import json

url = "http://localhost:8000/api/matches/statistical_preview/"
payload = {
    "home_team": "Real Madrid",
    "away_team": "Barcelona",
    "league": "La Liga",
    "date": "2026-01-15"
}

headers = {
    "Content-Type": "application/json"
}

print("Enviando requisição...")
response = requests.post(url, json=payload, headers=headers)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    analysis_data = data.get('analysis_data', {})
    
    print("\n=== MARKET ODDS ===")
    market_odds = analysis_data.get('market_odds')
    print(json.dumps(market_odds, indent=2))
    
    print("\n=== FAIR ODDS ===")
    fair_odds = analysis_data.get('fair_odds')
    print(json.dumps(fair_odds, indent=2))
    
else:
    print(f"Erro: {response.text}")
