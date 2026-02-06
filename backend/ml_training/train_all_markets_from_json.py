"""
Treina TODOS os 9 mercados ML usando as 850 partidas de ligas do JSON
Baseado no mesmo pipeline de train_cup_models_all_markets.py
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import xgboost as xgb

class MultiMarketTrainer:
    """Treina 9 mercados ML com dados de LIGAS do JSON"""
    
    def __init__(self, json_path='training_dataset_checkpoint.json'):
        self.json_path = Path(__file__).parent / json_path
        self.models_dir = Path(__file__).parent / 'trained_models'
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # MERCADOS SUPORTADOS
        self.markets = ['1x2', 'btts', 'ou15', 'ou25', 'ou35', 'dc', 'home_totals', 'away_totals', 'odd_even']
    
    def load_data(self):
        """Carrega dataset JSON"""
        print("\n" + "="*80)
        print("CARREGANDO DATASET DE LIGAS DO JSON")
        print("="*80)
        
        with open(self.json_path, 'r') as f:
            data = json.load(f)
        
        meta = data['metadata']
        matches = data['data']
        
        print(f"\nTotal partidas: {meta['total_matches']}")
        print(f"Ligas: {', '.join(meta['leagues'][:5])}...")
        print(f"Temporadas: {meta['seasons']}")
        
        return matches
    
    def extract_labels_all_markets(self, matches):
        """
        Extrai labels para TODOS os mercados a partir do resultado
        
        Returns:
            dict com datasets de cada mercado: {'1x2': {...}, 'btts': {...}, ...}
        """
        datasets = {market: {} for market in self.markets}
        
        for i, match in enumerate(matches):
            result = match['result']
            home_goals = result['home_goals']
            away_goals = result['away_goals']
            total_goals = home_goals + away_goals
            match_id = match['fixture_id']
            
            # 1X2 (0=Home, 1=Draw, 2=Away)
            if home_goals > away_goals:
                datasets['1x2'][match_id] = 0
            elif home_goals == away_goals:
                datasets['1x2'][match_id] = 1
            else:
                datasets['1x2'][match_id] = 2
            
            # BTTS (0=No, 1=Yes)
            datasets['btts'][match_id] = 1 if home_goals > 0 and away_goals > 0 else 0
            
            # Over/Under 1.5, 2.5, 3.5
            datasets['ou15'][match_id] = 1 if total_goals > 1.5 else 0
            datasets['ou25'][match_id] = 1 if total_goals > 2.5 else 0
            datasets['ou35'][match_id] = 1 if total_goals > 3.5 else 0
            
            # Double Chance (0=1X, 1=12, 2=X2)
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
    
    def train_model(self, market_name, X, y, n_classes):
        """Treina modelo XGBoost para um mercado específico"""
        print(f"\n{'='*80}")
        print(f"TREINANDO MODELO: {market_name.upper()}")
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
        
        print(f"\nACURACIA: {accuracy*100:.2f}%")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
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
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=target_names))
        
        # Salvar modelo
        model_path = self.models_dir / f'xgboost_{market_name}.pkl'
        joblib.dump(model, model_path)
        print(f"Modelo salvo: {model_path}")
        
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
        print("TREINAMENTO MULTI-MARKET - LIGAS (850 PARTIDAS)")
        print("="*80)
        
        # 1. Carregar dados
        matches = self.load_data()
        
        # 2. Extrair labels para todos mercados
        print(f"\nExtraindo labels para {len(self.markets)} mercados...")
        labels_datasets = self.extract_labels_all_markets(matches)
        
        # 3. Preparar features matrix
        print(f"\nPreparando matriz de features...")
        feature_list = []
        match_ids = []
        
        for match in matches:
            # Features já estão flat no JSON
            features = match['features']
            
            # LIMPAR valores não numéricos
            clean_features = {}
            for key, value in features.items():
                # Converter booleanos para int
                if isinstance(value, bool):
                    value = int(value)
                # Converter None para 0
                elif value is None:
                    value = 0
                # Ignorar strings não numéricas
                elif isinstance(value, str):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        # String não numérica - pular
                        continue
                
                clean_features[key] = value
            
            feature_list.append(clean_features)
            match_ids.append(match['fixture_id'])
        
        # Converter para DataFrame
        df_features = pd.DataFrame(feature_list, index=match_ids)
        df_features = df_features.fillna(0)
        
        print(f"Features preparadas: {df_features.shape}")
        print(f"Primeira amostra de features: {list(df_features.columns)[:10]}")
        
        # 4. Treinar cada mercado
        results = {}
        
        for market in self.markets:
            labels = labels_datasets[market]
            
            # Alinhar labels com features
            common_ids = df_features.index.intersection(labels.keys())
            X = df_features.loc[common_ids]
            y = pd.Series([labels[mid] for mid in common_ids])
            
            n_classes = len(y.unique())
            
            try:
                model, accuracy = self.train_model(market, X, y, n_classes)
                results[market] = accuracy
            except Exception as e:
                print(f"\nERRO ao treinar {market}: {e}")
                results[market] = 0.0
        
        # 5. Resumo final
        print("\n" + "="*80)
        print("RESUMO FINAL - ACURACIAS POR MERCADO (LIGAS)")
        print("="*80)
        
        for market, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
            print(f"   {market.upper():15s}: {acc*100:.2f}%")
        
        print(f"\n{len([r for r in results.values() if r > 0])} modelos treinados com sucesso!")
        print("="*80)
        
        # Comparação com copas
        print("\n" + "="*80)
        print("COMPARACAO: LIGAS vs COPAS")
        print("="*80)
        
        cup_accuracies = {
            '1x2': 87.78,
            'btts': 94.44,
            'ou15': 97.78,
            'ou25': 98.89,
            'ou35': 91.11,
            'dc': 84.44,
            'home_totals': 78.89,
            'away_totals': 85.56,
            'odd_even': 77.78
        }
        
        print(f"\n{'Mercado':<15} {'Ligas':<10} {'Copas':<10} {'Delta':<10}")
        print("-" * 50)
        for market in self.markets:
            league_acc = results.get(market, 0) * 100
            cup_acc = cup_accuracies.get(market, 0)
            delta = league_acc - cup_acc
            symbol = "+" if delta >= 0 else ""
            print(f"{market.upper():<15} {league_acc:>6.2f}%   {cup_acc:>6.2f}%   {symbol}{delta:>6.2f}%")
        
        print("="*80)


if __name__ == '__main__':
    trainer = MultiMarketTrainer()
    trainer.train_all_markets()
