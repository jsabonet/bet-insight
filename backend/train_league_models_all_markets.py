"""
Treina TODOS os modelos ML (9 mercados) usando dados de LIGAS do banco de dados
Baseado no mesmo pipeline de train_cup_models_all_markets.py
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import xgboost as xgb

class MultiMarketLeagueTrainer:
    """Treina 9 mercados ML com dados de LIGAS"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.models_dir = self.base_path / 'ml_training' / 'trained_models'
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # MERCADOS SUPORTADOS
        self.markets = ['1x2', 'btts', 'ou15', 'ou25', 'ou35', 'dc', 'home_totals', 'away_totals', 'odd_even']
    
    def load_league_data(self):
        """Carrega partidas de LIGAS do banco de dados"""
        from apps.matches.models import Match
        from apps.analysis.services.feature_engineer import FeatureEngineer
        from apps.analysis.services.match_enricher import MatchDataEnricher
        
        print("\n" + "="*80)
        print("📂 CARREGANDO PARTIDAS DE LIGAS DO BANCO DE DADOS")
        print("="*80)
        
        # FILTRAR APENAS LIGAS (excluir copas)
        matches = Match.objects.filter(
            status='FT',
            home_score__isnull=False,
            away_score__isnull=False
        ).exclude(
            league__name__icontains='Cup'
        ).exclude(
            league__name__icontains='FA Cup'
        ).exclude(
            league__name__icontains='Copa'
        ).order_by('-match_date')[:1000]  # Últimas 1000 partidas de ligas
        
        print(f"✅ {matches.count()} partidas de ligas encontradas")
        
        # Usar services diretamente
        enricher = MatchDataEnricher()
        fe = FeatureEngineer()
        dataset = []
        errors = 0
        
        for i, match in enumerate(matches, 1):
            if i % 50 == 0:
                print(f"   Processando {i}/{matches.count()}...")
            
            try:
                # Enriquecer dados
                match_data = {'api_id': match.api_football_id}
                enriched = enricher.enrich(match_data)
                
                # Gerar features completas
                features = fe.engineer_all_features(enriched)
                
                # Adicionar resultado
                result = {
                    'home_goals': match.home_score,
                    'away_goals': match.away_score
                }
                
                dataset.append({
                    'features': features,
                    'result': result,
                    'match_id': match.id,
                    'league': match.league.name if match.league else 'Unknown'
                })
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"⚠️ Erro na partida {match.id}: {e}")
        
        print(f"\n✅ Dataset criado: {len(dataset)} partidas válidas ({errors} erros)")
        return dataset
    
    def extract_labels_all_markets(self, matches):
        """
        Extrai labels para TODOS os mercados a partir do resultado
        
        Returns:
            dict com datasets de cada mercado: {'1x2': {...}, 'btts': {...}, ...}
        """
        datasets = {
            '1x2': {},
            'btts': {},
            'ou15': {},
            'ou25': {},
            'ou35': {},
            'dc': {},
            'home_totals': {},
            'away_totals': {},
            'odd_even': {}
        }
        
        for match_data in matches:
            result = match_data['result']
            home_goals = result['home_goals']
            away_goals = result['away_goals']
            total_goals = home_goals + away_goals
            match_id = match_data['match_id']
            
            # 1X2 (0=Home, 1=Draw, 2=Away)
            if home_goals > away_goals:
                datasets['1x2'][match_id] = 0
            elif home_goals == away_goals:
                datasets['1x2'][match_id] = 1
            else:
                datasets['1x2'][match_id] = 2
            
            # BTTS (0=No, 1=Yes)
            datasets['btts'][match_id] = 1 if home_goals > 0 and away_goals > 0 else 0
            
            # Over/Under 1.5
            datasets['ou15'][match_id] = 1 if total_goals > 1.5 else 0
            
            # Over/Under 2.5
            datasets['ou25'][match_id] = 1 if total_goals > 2.5 else 0
            
            # Over/Under 3.5
            datasets['ou35'][match_id] = 1 if total_goals > 3.5 else 0
            
            # Double Chance (0=1X, 1=12, 2=X2)
            if home_goals >= away_goals:  # Home win or draw
                datasets['dc'][match_id] = 0  # 1X
            elif home_goals > away_goals or away_goals > home_goals:  # Either team wins
                if home_goals != away_goals:
                    datasets['dc'][match_id] = 1  # 12
            if home_goals <= away_goals:  # Draw or away win
                datasets['dc'][match_id] = 2  # X2
            
            # Simplificar: usar apenas 1X2 logic
            if home_goals > away_goals:
                datasets['dc'][match_id] = 0  # 1X
            elif home_goals == away_goals:
                datasets['dc'][match_id] = 2  # X2
            else:
                datasets['dc'][match_id] = 1  # 12 (away win)
            
            # Home Totals (0=U0.5, 1=O0.5U1.5, 2=O1.5U2.5, 3=O2.5)
            if home_goals == 0:
                datasets['home_totals'][match_id] = 0
            elif home_goals == 1:
                datasets['home_totals'][match_id] = 1
            elif home_goals == 2:
                datasets['home_totals'][match_id] = 2
            else:
                datasets['home_totals'][match_id] = 3
            
            # Away Totals (mesma lógica)
            if away_goals == 0:
                datasets['away_totals'][match_id] = 0
            elif away_goals == 1:
                datasets['away_totals'][match_id] = 1
            elif away_goals == 2:
                datasets['away_totals'][match_id] = 2
            else:
                datasets['away_totals'][match_id] = 3
            
            # Odd/Even (0=Even, 1=Odd)
            datasets['odd_even'][match_id] = total_goals % 2
        
        return datasets
    
    def flatten_features(self, features):
        """Converte features nested em flat (idêntico ao treino de copas)"""
        flat = {}
        for category, values in features.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(value, bool):
                        value = int(value)
                    if value is None:
                        value = 0
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except:
                            continue
                    flat[f"{category}.{key}"] = value
            else:
                if isinstance(values, bool):
                    values = int(values)
                if values is None:
                    values = 0
                if isinstance(values, str):
                    try:
                        values = float(values)
                    except:
                        continue
                flat[category] = values
        return flat
    
    def train_model(self, market_name, X, y, n_classes):
        """Treina modelo XGBoost para um mercado específico"""
        print(f"\n{'='*80}")
        print(f"🎯 TREINANDO MODELO: {market_name.upper()}")
        print(f"{'='*80}")
        
        # Split treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   Treino: {len(X_train)} amostras")
        print(f"   Teste: {len(X_test)} amostras")
        print(f"   Classes: {n_classes}")
        
        # Configurar XGBoost baseado no número de classes
        if n_classes > 2:
            # Multi-class
            params = {
                'objective': 'multi:softmax',
                'num_class': n_classes,
                'max_depth': 5,
                'learning_rate': 0.1,
                'n_estimators': 150,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'eval_metric': 'mlogloss'
            }
        else:
            # Binary
            params = {
                'objective': 'binary:logistic',
                'max_depth': 4,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'eval_metric': 'logloss'
            }
        
        # Treinar
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train)
        
        # Avaliar
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📊 ACURÁCIA: {accuracy*100:.2f}%")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\n🔢 Confusion Matrix:")
        print(cm)
        
        # Classification Report
        labels_map = {
            '1x2': ['Home Win', 'Draw', 'Away Win'],
            'btts': ['No BTTS', 'BTTS Yes'],
            'ou15': ['Under 1.5', 'Over 1.5'],
            'ou25': ['Under 2.5', 'Over 2.5'],
            'ou35': ['Under 3.5', 'Over 3.5'],
            'dc': ['1X', '12', 'X2'],
            'home_totals': ['U0.5', 'O0.5 U1.5', 'O1.5 U2.5', 'O2.5'],
            'away_totals': ['U0.5', 'O0.5 U1.5', 'O1.5 U2.5', 'O2.5'],
            'odd_even': ['Even', 'Odd']
        }
        
        target_names = labels_map.get(market_name, [str(i) for i in range(n_classes)])
        print(f"\n📈 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=target_names))
        
        # Salvar modelo
        model_path = self.models_dir / f'xgboost_{market_name}.pkl'
        joblib.dump(model, model_path)
        print(f"✅ Modelo salvo: {model_path}")
        
        # Salvar métricas
        metrics = {
            'market': market_name,
            'accuracy': accuracy,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'n_classes': n_classes,
            'params': params,
            'timestamp': datetime.now().isoformat()
        }
        
        metrics_path = self.models_dir / f'{market_name}_model_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Salvar feature names
        feature_names_path = self.models_dir / f'{market_name}_feature_names.json'
        feature_names = list(X.columns) if hasattr(X, 'columns') else [f'feature_{i}' for i in range(X.shape[1])]
        with open(feature_names_path, 'w') as f:
            json.dump(feature_names, f, indent=2)
        
        return model, accuracy
    
    def train_all_markets(self):
        """Pipeline completo: carrega dados e treina todos os 9 mercados"""
        print("\n" + "="*80)
        print("🚀 TREINAMENTO MULTI-MARKET - LIGAS")
        print("="*80)
        
        # 1. Carregar dados
        matches = self.load_league_data()
        
        if len(matches) < 100:
            print("❌ Dados insuficientes para treino!")
            return
        
        # 2. Extrair labels para todos mercados
        print(f"\n📊 Extraindo labels para {len(self.markets)} mercados...")
        labels_datasets = self.extract_labels_all_markets(matches)
        
        # 3. Preparar features matrix
        print(f"\n🔧 Preparando matriz de features...")
        feature_list = []
        match_ids = []
        
        for match_data in matches:
            flat = self.flatten_features(match_data['features'])
            feature_list.append(flat)
            match_ids.append(match_data['match_id'])
        
        # Converter para DataFrame
        import pandas as pd
        df_features = pd.DataFrame(feature_list, index=match_ids)
        df_features = df_features.fillna(0)
        
        print(f"✅ Features preparadas: {df_features.shape}")
        
        # 4. Treinar cada mercado
        results = {}
        
        for market in self.markets:
            labels = labels_datasets[market]
            
            # Alinhar labels com features
            common_ids = df_features.index.intersection(labels.keys())
            X = df_features.loc[common_ids]
            y = pd.Series([labels[mid] for mid in common_ids])
            
            n_classes = len(y.unique())
            
            model, accuracy = self.train_model(market, X, y, n_classes)
            results[market] = accuracy
        
        # 5. Resumo final
        print("\n" + "="*80)
        print("📊 RESUMO FINAL - ACURÁCIAS POR MERCADO")
        print("="*80)
        
        for market, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
            print(f"   {market.upper():15s}: {acc*100:.2f}%")
        
        print(f"\n✅ {len(results)} modelos treinados com sucesso!")
        print("="*80)


if __name__ == '__main__':
    trainer = MultiMarketLeagueTrainer()
    trainer.train_all_markets()
