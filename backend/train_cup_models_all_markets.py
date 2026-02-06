"""
Script de Treino - Modelos Especializados em COPAS (TODOS OS MERCADOS)
=====================================================================

ARQUITETURA DUAL-MODEL (SEGURA) - TODOS OS MERCADOS:
- xgboost_1x2.pkl (ligas) → xgboost_1x2_cups.pkl (copas) ✅
- xgboost_btts.pkl (ligas) → xgboost_btts_cups.pkl (copas) 🆕
- xgboost_ou25.pkl (ligas) → xgboost_ou25_cups.pkl (copas) 🆕

Treina APENAS com dados de copas para criar modelos especializados.
Modelos de ligas permanecem 100% intocados e funcionais.
"""

import json
import logging
import pickle
from pathlib import Path
from datetime import datetime
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import xgboost as xgb

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiMarketCupTrainer:
    """
    Treina múltiplos modelos XGBoost para diferentes mercados de apostas.
    
    MERCADOS COBERTOS:
    1. 1X2 (Resultado): Home Win / Draw / Away Win
    2. BTTS (Both Teams To Score): Yes / No
    3. O/U 1.5 (Over/Under): Over / Under
    4. O/U 2.5 (Over/Under): Over / Under
    5. O/U 3.5 (Over/Under): Over / Under
    6. Double Chance: 1X / 12 / X2
    7. Team Totals: Home O/U 0.5, 1.5, 2.5 / Away O/U 0.5, 1.5, 2.5
    8. Winning Margins: Home/Away by 1, by 2+
    9. Odd/Even Goals: Odd / Even
    
    CARACTERÍSTICAS:
    - Dataset: 450 partidas de copas (FA Cup, Copa del Rey, etc.)
    - Features: 107 features (mesmas do modelo de ligas)
    - Modelos: XGBoost Classifier para cada mercado
    - Output: xgboost_{mercado}_cups.pkl
    
    SEGURANÇA:
    - Modelos de ligas (xgboost_{mercado}.pkl) permanecem INTOCADOS
    - Zero risco para previsões de ligas
    - Isolamento total entre modelos
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.cup_data_path = self.base_dir / 'ml_training' / 'cup_training_dataset.json'
        self.output_dir = self.base_dir / 'ml_models'
        
        # Criar diretório de output se não existir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🏆 MultiMarketCupTrainer inicializado")
        logger.info(f"📁 Cup data: {self.cup_data_path}")
        logger.info(f"💾 Output dir: {self.output_dir}")
    
    def load_cup_data(self):
        """
        Carrega dataset de copas coletado pela API.
        
        Returns:
            list: Lista de dicionários com dados de partidas de copas
        """
        logger.info("📥 Carregando dados de copas...")
        
        if not self.cup_data_path.exists():
            raise FileNotFoundError(
                f"❌ Dataset de copas não encontrado: {self.cup_data_path}\n"
                "Execute primeiro: python collect_cup_data.py"
            )
        
        with open(self.cup_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        matches = data.get('matches', [])
        logger.info(f"✅ {len(matches)} partidas de copas carregadas")
        
        # Estatísticas por competição
        competitions = {}
        for match in matches:
            comp = match.get('competition', 'Unknown')
            competitions[comp] = competitions.get(comp, 0) + 1
        
        logger.info("📊 Distribuição por competição:")
        for comp, count in sorted(competitions.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {comp}: {count} partidas")
        
        return matches
    
    def extract_labels_all_markets(self, matches):
        """
        Extrai labels para TODOS os mercados de cada partida.
        
        Args:
            matches: Lista de partidas
            
        Returns:
            dict: {
                '1x2': {'X': features, 'y': labels},
                'btts': {'X': features, 'y': labels},
                'ou15': {'X': features, 'y': labels},
                'ou25': {'X': features, 'y': labels},
                'ou35': {'X': features, 'y': labels},
                'dc': {'X': features, 'y': labels},  # Double Chance (3 classes)
                'home_totals': {'X': features, 'y': labels},  # Home O/U combined
                'away_totals': {'X': features, 'y': labels},  # Away O/U combined
                'odd_even': {'X': features, 'y': labels}
            }
        """
        logger.info("🔧 Extraindo labels para TODOS os mercados...")
        
        datasets = {
            '1x2': {'X_list': [], 'y_list': []},
            'btts': {'X_list': [], 'y_list': []},
            'ou15': {'X_list': [], 'y_list': []},
            'ou25': {'X_list': [], 'y_list': []},
            'ou35': {'X_list': [], 'y_list': []},
            'dc': {'X_list': [], 'y_list': []},  # Double Chance: 0=1X, 1=12, 2=X2
            'home_totals': {'X_list': [], 'y_list': []},  # 0=U0.5, 1=O0.5U1.5, 2=O1.5U2.5, 3=O2.5
            'away_totals': {'X_list': [], 'y_list': []},
            'odd_even': {'X_list': [], 'y_list': []}
        }
        
        feature_names = None
        
        for match in matches:
            features = match.get('features', {})
            result = match.get('result')
            
            if not features or result is None:
                continue
            
            # Primeira iteração: capturar nomes das features
            if feature_names is None:
                feature_names = sorted(features.keys())
                logger.info(f"📋 {len(feature_names)} features identificadas")
            
            # Converter features para array ordenado (filtrando strings)
            feature_vector = []
            for fname in feature_names:
                value = features.get(fname, 0.0)
                
                # Garantir valor numérico
                if isinstance(value, bool):
                    value = float(value)
                elif isinstance(value, str):
                    value = 0.0
                elif value is None:
                    value = 0.0
                else:
                    value = float(value)
                
                feature_vector.append(value)
            
            # Extrair resultado (dict ou int)
            if isinstance(result, dict):
                home_goals = result.get('home_goals', 0)
                away_goals = result.get('away_goals', 0)
            else:
                # Fallback: assumir que result é label 1X2
                # Não temos acesso aos gols, pular BTTS/OU
                continue
            
            total_goals = home_goals + away_goals
            
            # === LABEL 1X2 ===
            if home_goals > away_goals:
                label_1x2 = 0  # Home Win
            elif home_goals == away_goals:
                label_1x2 = 1  # Draw
            else:
                label_1x2 = 2  # Away Win
            
            datasets['1x2']['X_list'].append(feature_vector)
            datasets['1x2']['y_list'].append(label_1x2)
            
            # === LABEL BTTS ===
            label_btts = 1 if (home_goals > 0 and away_goals > 0) else 0
            datasets['btts']['X_list'].append(feature_vector)
            datasets['btts']['y_list'].append(label_btts)
            
            # === LABEL O/U 1.5 ===
            label_ou15 = 1 if total_goals > 1.5 else 0
            datasets['ou15']['X_list'].append(feature_vector)
            datasets['ou15']['y_list'].append(label_ou15)
            
            # === LABEL O/U 2.5 ===
            label_ou25 = 1 if total_goals > 2.5 else 0
            datasets['ou25']['X_list'].append(feature_vector)
            datasets['ou25']['y_list'].append(label_ou25)
            
            # === LABEL O/U 3.5 ===
            label_ou35 = 1 if total_goals > 3.5 else 0
            datasets['ou35']['X_list'].append(feature_vector)
            datasets['ou35']['y_list'].append(label_ou35)
            
            # === LABEL DOUBLE CHANCE ===
            # 0=1X (Home ou Draw), 1=12 (Home ou Away), 2=X2 (Draw ou Away)
            # Escolher o resultado mais provável baseado no resultado
            if label_1x2 == 0:  # Home Win
                label_dc = 1  # 12 (Home ou Away) é o melhor para Home Win
            elif label_1x2 == 1:  # Draw
                label_dc = 0  # 1X (Home ou Draw) é arbitrário, poderia ser X2 também
            else:  # Away Win
                label_dc = 2  # X2 (Draw ou Away)
            
            datasets['dc']['X_list'].append(feature_vector)
            datasets['dc']['y_list'].append(label_dc)
            
            # === LABEL HOME TOTALS ===
            # 0=Under 0.5, 1=Over 0.5 Under 1.5, 2=Over 1.5 Under 2.5, 3=Over 2.5
            if home_goals == 0:
                label_home_totals = 0
            elif home_goals == 1:
                label_home_totals = 1
            elif home_goals == 2:
                label_home_totals = 2
            else:
                label_home_totals = 3
            
            datasets['home_totals']['X_list'].append(feature_vector)
            datasets['home_totals']['y_list'].append(label_home_totals)
            
            # === LABEL AWAY TOTALS ===
            if away_goals == 0:
                label_away_totals = 0
            elif away_goals == 1:
                label_away_totals = 1
            elif away_goals == 2:
                label_away_totals = 2
            else:
                label_away_totals = 3
            
            datasets['away_totals']['X_list'].append(feature_vector)
            datasets['away_totals']['y_list'].append(label_away_totals)
            
            # === LABEL ODD/EVEN ===
            label_odd_even = 1 if total_goals % 2 == 1 else 0  # 1=Odd, 0=Even
            datasets['odd_even']['X_list'].append(feature_vector)
            datasets['odd_even']['y_list'].append(label_odd_even)
            
            # === LABEL O/U 2.5 ===
            label_ou25 = 1 if total_goals > 2.5 else 0  # 1=Over, 0=Under
            
            datasets['ou25']['X_list'].append(feature_vector)
            datasets['ou25']['y_list'].append(label_ou25)
        
        # Converter para numpy arrays
        for market in datasets:
            datasets[market]['X'] = np.array(datasets[market]['X_list']).astype(np.float32)
            datasets[market]['y'] = np.array(datasets[market]['y_list']).astype(np.int32)
            
            logger.info(f"✅ {market.upper()}: {len(datasets[market]['y'])} amostras preparadas")
        
        return datasets, feature_names
    
    def train_model(self, X, y, market_name, n_classes):
        """
        Treina modelo XGBoost para um mercado específico.
        
        Args:
            X: Features
            y: Labels
            market_name: Nome do mercado ('1x2', 'btts', 'ou25')
            n_classes: Número de classes (3 para 1X2, 2 para BTTS/OU)
            
        Returns:
            tuple: (model, metrics)
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 TREINANDO MODELO: {market_name.upper()}")
        logger.info(f"{'='*80}")
        
        # Split train/test (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"📊 Train: {len(X_train)} | Test: {len(X_test)}")
        
        # Parâmetros XGBoost (ajustados por mercado e número de classes)
        if n_classes > 2:
            # MULTI-CLASS: 1X2 (3), DC (3), Home/Away Totals (4)
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
            # BINARY: BTTS, O/U 1.5/2.5/3.5, Odd/Even
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
        
        logger.info("⚙️ Parâmetros XGBoost:")
        for k, v in params.items():
            logger.info(f"   {k}: {v}")
        
        # Treinar
        model = xgb.XGBClassifier(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Avaliar
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"✅ Treino concluído!")
        logger.info(f"🎯 Acurácia no teste: {accuracy*100:.2f}%")
        
        # Relatório detalhado
        logger.info(f"\n📊 Classification Report:")
        
        # Target names baseado no mercado
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
        
        target_names = labels_map.get(market_name, [f'Class{i}' for i in range(n_classes)])
        
        report = classification_report(
            y_test, y_pred,
            target_names=target_names,
            zero_division=0
        )
        print(report)
        
        # Confusion Matrix
        logger.info(f"\n🔍 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        metrics = {
            'market': market_name,
            'accuracy': float(accuracy),
            'train_size': len(X_train),
            'test_size': len(X_test),
            'n_classes': n_classes,
            'params': params,
            'timestamp': datetime.now().isoformat()
        }
        
        return model, metrics
    
    def save_model(self, model, market_name, feature_names, metrics):
        """
        Salva modelo e metadados para um mercado específico.
        
        Args:
            model: Modelo treinado
            market_name: Nome do mercado ('1x2', 'btts', 'ou25')
            feature_names: Lista de nomes das features
            metrics: Métricas de performance
        """
        logger.info(f"💾 Salvando modelo {market_name.upper()}...")
        
        # Paths
        model_path = self.output_dir / f'xgboost_{market_name}_cups.pkl'
        features_path = self.output_dir / f'feature_names_{market_name}_cups.json'
        metrics_path = self.output_dir / f'{market_name}_model_metrics.json'
        
        # Salvar modelo
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"✅ Modelo salvo: {model_path}")
        
        # Salvar feature names
        with open(features_path, 'w', encoding='utf-8') as f:
            json.dump(feature_names, f, indent=2)
        logger.info(f"✅ Features salvas: {features_path}")
        
        # Salvar métricas
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"✅ Métricas salvas: {metrics_path}")
        
        # Tamanho do modelo
        size_mb = model_path.stat().st_size / (1024 * 1024)
        logger.info(f"📦 Tamanho do modelo: {size_mb:.2f} MB")
    
    def run(self):
        """
        Executa pipeline completo de treino para TODOS os mercados.
        """
        logger.info("=" * 80)
        logger.info("🏆 TREINO MULTI-MERCADO COPAS - ARQUITETURA DUAL-MODEL")
        logger.info("=" * 80)
        
        try:
            # 1. Carregar dados
            matches = self.load_cup_data()
            
            # 2. Extrair labels para todos os mercados
            datasets, feature_names = self.extract_labels_all_markets(matches)
            
            # 3. Treinar cada mercado
            all_metrics = {}
            
            markets_config = [
                ('1x2', 3),        # Multi-class: Home/Draw/Away
                ('btts', 2),       # Binary: No/Yes
                ('ou15', 2),       # Binary: Under/Over 1.5
                ('ou25', 2),       # Binary: Under/Over 2.5
                ('ou35', 2),       # Binary: Under/Over 3.5
                ('dc', 3),         # Multi-class: 1X/12/X2
                ('home_totals', 4), # Multi-class: U0.5/O0.5U1.5/O1.5U2.5/O2.5
                ('away_totals', 4), # Multi-class: U0.5/O0.5U1.5/O1.5U2.5/O2.5
                ('odd_even', 2)    # Binary: Even/Odd
            ]
            
            for market_name, n_classes in markets_config:
                if market_name not in datasets:
                    logger.warning(f"⚠️ Mercado {market_name} não encontrado, pulando...")
                    continue
                
                logger.info(f"\n{'='*60}")
                logger.info(f"🎯 TREINANDO: {market_name.upper()}")
                logger.info(f"{'='*60}")
                
                model, metrics = self.train_model(
                    datasets[market_name]['X'],
                    datasets[market_name]['y'],
                    market_name,
                    n_classes=n_classes
                )
                
                self.save_model(model, market_name, feature_names, metrics)
                all_metrics[market_name] = metrics
            
            # 4. Resumo final
            logger.info("=" * 80)
            logger.info("✅ TREINO MULTI-MERCADO CONCLUÍDO COM SUCESSO!")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📊 RESUMO POR MERCADO:")
            logger.info(f"   Partidas: {len(matches)}")
            logger.info(f"   Features: {len(feature_names)}")
            logger.info("")
            
            for market, metrics in all_metrics.items():
                logger.info(f"   {market.upper()}:")
                logger.info(f"      Acurácia: {metrics['accuracy']*100:.2f}%")
                logger.info(f"      Modelo: xgboost_{market}_cups.pkl")
                logger.info(f"      Classes: {metrics['n_classes']}")
            
            logger.info("")
            logger.info(f"🎯 TOTAL: {len(all_metrics)} MERCADOS TREINADOS")
            logger.info("")
            logger.info("🔒 SEGURANÇA:")
            logger.info("   ✅ Modelos de ligas INTOCADOS:")
            logger.info("      - xgboost_1x2.pkl (ligas)")
            logger.info("      - xgboost_btts.pkl (ligas) - se existir")
            logger.info("      - xgboost_ou25.pkl (ligas) - se existir")
            logger.info("   ✅ Zero risco para previsões de ligas")
            logger.info("   ✅ Modelos completamente isolados")
            logger.info("")
            logger.info("📝 PRÓXIMOS PASSOS:")
            logger.info("   1. Revisar métricas em {market}_model_metrics.json")
            logger.info("   2. Atualizar ml_integration.py para TODOS os mercados")
            logger.info("   3. Testar com partidas de copa conhecidas")
            logger.info("   4. Monitorar performance separadamente por mercado")
            
        except Exception as e:
            logger.error(f"❌ Erro durante treino: {e}", exc_info=True)
            raise


def main():
    """Função principal."""
    trainer = MultiMarketCupTrainer()
    trainer.run()


if __name__ == '__main__':
    main()
