"""
Script de Treino - Modelo Especializado em COPAS
================================================

ARQUITETURA DUAL-MODEL (SEGURA):
- xgboost_1x2.pkl (880 ligas) → INTOCADO
- xgboost_1x2_cups.pkl (450 copas) → NOVO

Treina APENAS com dados de copas para criar modelo especializado.
Modelo de ligas permanece 100% intocado e funcional.
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


class CupModelTrainer:
    """
    Treina modelo XGBoost EXCLUSIVAMENTE com dados de copas.
    
    CARACTERÍSTICAS:
    - Dataset: 450 partidas de copas (FA Cup, Copa del Rey, etc.)
    - Features: 107 features (mesmas do modelo de ligas)
    - Target: Resultado 1X2 (Home Win / Draw / Away Win)
    - Modelo: XGBoost Classifier
    - Output: xgboost_1x2_cups.pkl
    
    SEGURANÇA:
    - Modelo de ligas (xgboost_1x2.pkl) permanece INTOCADO
    - Zero risco para previsões de ligas
    - Isolamento total entre modelos
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.cup_data_path = self.base_dir / 'ml_training' / 'cup_training_dataset.json'
        self.output_model_path = self.base_dir / 'ml_models' / 'xgboost_1x2_cups.pkl'
        self.output_features_path = self.base_dir / 'ml_models' / 'feature_names_cups.json'
        
        # Criar diretório de output se não existir
        self.output_model_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("🏆 CupModelTrainer inicializado")
        logger.info(f"📁 Cup data: {self.cup_data_path}")
        logger.info(f"💾 Output model: {self.output_model_path}")
    
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
    
    def prepare_training_data(self, matches):
        """
        Prepara dados para treino do XGBoost.
        
        Args:
            matches: Lista de partidas com features
            
        Returns:
            tuple: (X, y, feature_names)
                X: numpy array com features
                y: numpy array com targets (0=Home, 1=Draw, 2=Away)
                feature_names: lista com nomes das features
        """
        logger.info("🔧 Preparando dados para treino...")
        
        X_list = []
        y_list = []
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
            
            # Converter features para array ordenado
            # Filtrar apenas valores numéricos
            feature_vector = []
            for fname in feature_names:
                value = features.get(fname, 0.0)
                
                # Garantir valor numérico
                if isinstance(value, bool):
                    value = float(value)
                elif isinstance(value, str):
                    # String não numérica - pular (não deve acontecer se feature_engineer está correto)
                    value = 0.0
                elif value is None:
                    value = 0.0
                else:
                    value = float(value)
                
                feature_vector.append(value)
            
            X_list.append(feature_vector)
            
            # Target: 0=Home Win, 1=Draw, 2=Away Win
            # Converter dict result para label numérico
            if isinstance(result, dict):
                home_goals = result.get('home_goals', 0)
                away_goals = result.get('away_goals', 0)
                
                if home_goals > away_goals:
                    label = 0  # Home Win
                elif home_goals == away_goals:
                    label = 1  # Draw
                else:
                    label = 2  # Away Win
                
                y_list.append(label)
            else:
                # Já é numérico
                y_list.append(result)
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        # Garantir dtype correto para XGBoost
        X = X.astype(np.float32)
        y = y.astype(np.int32)
        
        logger.info(f"✅ Dataset preparado: {X.shape[0]} amostras, {X.shape[1]} features")
        logger.info(f"📊 Distribuição de classes:")
        unique, counts = np.unique(y, return_counts=True)
        class_names = {0: 'Home Win', 1: 'Draw', 2: 'Away Win'}
        for label, count in zip(unique, counts):
            percentage = (count / len(y)) * 100
            logger.info(f"   {class_names[label]}: {count} ({percentage:.1f}%)")
        
        return X, y, feature_names
    
    def train_model(self, X, y):
        """
        Treina modelo XGBoost com dados de copas.
        
        Args:
            X: Features
            y: Targets
            
        Returns:
            tuple: (model, metrics)
        """
        logger.info("🚀 Iniciando treino do modelo de copas...")
        
        # Split train/test (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"📊 Train: {len(X_train)} | Test: {len(X_test)}")
        
        # Parâmetros XGBoost
        # Ajustados para dataset menor (450 partidas)
        params = {
            'objective': 'multi:softmax',
            'num_class': 3,
            'max_depth': 5,  # Menor que ligas (6) para evitar overfit
            'learning_rate': 0.1,
            'n_estimators': 150,  # Menor que ligas (200)
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'eval_metric': 'mlogloss'
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
        logger.info("\n📊 Classification Report:")
        report = classification_report(
            y_test, y_pred,
            target_names=['Home Win', 'Draw', 'Away Win'],
            zero_division=0
        )
        print(report)
        
        # Confusion Matrix
        logger.info("\n🔍 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        metrics = {
            'accuracy': float(accuracy),
            'train_size': len(X_train),
            'test_size': len(X_test),
            'params': params,
            'timestamp': datetime.now().isoformat()
        }
        
        return model, metrics
    
    def save_model(self, model, feature_names, metrics):
        """
        Salva modelo e metadados.
        
        Args:
            model: Modelo treinado
            feature_names: Lista de nomes das features
            metrics: Métricas de performance
        """
        logger.info("💾 Salvando modelo...")
        
        # Salvar modelo
        with open(self.output_model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"✅ Modelo salvo: {self.output_model_path}")
        
        # Salvar feature names
        with open(self.output_features_path, 'w', encoding='utf-8') as f:
            json.dump(feature_names, f, indent=2)
        logger.info(f"✅ Features salvas: {self.output_features_path}")
        
        # Salvar métricas
        metrics_path = self.output_model_path.parent / 'cup_model_metrics.json'
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"✅ Métricas salvas: {metrics_path}")
        
        # Tamanho do modelo
        size_mb = self.output_model_path.stat().st_size / (1024 * 1024)
        logger.info(f"📦 Tamanho do modelo: {size_mb:.2f} MB")
    
    def run(self):
        """
        Executa pipeline completo de treino.
        """
        logger.info("=" * 70)
        logger.info("🏆 TREINO MODELO DE COPAS - ARQUITETURA DUAL-MODEL")
        logger.info("=" * 70)
        
        try:
            # 1. Carregar dados
            matches = self.load_cup_data()
            
            # 2. Preparar dados
            X, y, feature_names = self.prepare_training_data(matches)
            
            # 3. Treinar
            model, metrics = self.train_model(X, y)
            
            # 4. Salvar
            self.save_model(model, feature_names, metrics)
            
            logger.info("=" * 70)
            logger.info("✅ TREINO CONCLUÍDO COM SUCESSO!")
            logger.info("=" * 70)
            logger.info("")
            logger.info("📊 RESUMO:")
            logger.info(f"   Partidas: {len(matches)}")
            logger.info(f"   Features: {len(feature_names)}")
            logger.info(f"   Acurácia: {metrics['accuracy']*100:.2f}%")
            logger.info(f"   Modelo: {self.output_model_path.name}")
            logger.info("")
            logger.info("🔒 SEGURANÇA:")
            logger.info("   ✅ Modelo de ligas (xgboost_1x2.pkl) INTOCADO")
            logger.info("   ✅ Zero risco para previsões de ligas")
            logger.info("   ✅ Modelos completamente isolados")
            logger.info("")
            logger.info("📝 PRÓXIMOS PASSOS:")
            logger.info("   1. Revisar métricas em cup_model_metrics.json")
            logger.info("   2. Ativar dual-model no ml_integration.py (já configurado)")
            logger.info("   3. Testar com partidas de copa conhecidas")
            logger.info("   4. Monitorar performance separadamente")
            
        except Exception as e:
            logger.error(f"❌ Erro durante treino: {e}", exc_info=True)
            raise


def main():
    """Função principal."""
    trainer = CupModelTrainer()
    trainer.run()


if __name__ == '__main__':
    main()
