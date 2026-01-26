"""
Script de treino de Machine Learning para predição 1X2
Usa XGBoost/LightGBM com dados históricos completos
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import joblib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FootballMLTrainer:
    """Treina modelos ML para predição 1X2"""
    
    def __init__(self, dataset_path='training_dataset.json'):
        self.dataset_path = Path(__file__).parent / dataset_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.results = {}
        
    def load_dataset(self):
        """Carrega dataset JSON e converte para DataFrame"""
        logger.info("="*80)
        logger.info("📂 CARREGANDO DATASET")
        logger.info("="*80)
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        metadata = dataset['metadata']
        data = dataset['data']
        
        logger.info(f"📊 Total de partidas: {metadata['total_matches']}")
        logger.info(f"🏆 Ligas: {', '.join(metadata['leagues'][:3])}...")
        logger.info(f"📅 Temporadas: {metadata['seasons']}")
        
        # Converter para DataFrame
        rows = []
        for match in data:
            row = {
                'fixture_id': match['fixture_id'],
                'league': match['league'],
                'season': match['season'],
                'label': match['label'],
                **match['features']  # Unpack todas as features
            }
            rows.append(row)
        
        self.df = pd.DataFrame(rows)
        
        logger.info(f"✅ DataFrame criado: {self.df.shape[0]} linhas × {self.df.shape[1]} colunas")
        logger.info(f"📊 Features disponíveis: {self.df.shape[1] - 4}")  # -4 = (fixture_id, league, season, label)
        
        # Verificar distribuição de labels
        label_counts = self.df['label'].value_counts().sort_index()
        logger.info(f"\n📈 Distribuição de resultados:")
        logger.info(f"   Casa (0): {label_counts.get(0, 0)} ({label_counts.get(0, 0)/len(self.df)*100:.1f}%)")
        logger.info(f"   Empate (1): {label_counts.get(1, 0)} ({label_counts.get(1, 0)/len(self.df)*100:.1f}%)")
        logger.info(f"   Fora (2): {label_counts.get(2, 0)} ({label_counts.get(2, 0)/len(self.df)*100:.1f}%)")
        
        return self.df
    
    def preprocess(self, test_size=0.2, random_state=42):
        """Preprocessa dados: limpeza, split, normalização"""
        logger.info("\n" + "="*80)
        logger.info("🔧 PREPROCESSAMENTO")
        logger.info("="*80)
        
        # Separar features e labels
        feature_cols = [col for col in self.df.columns 
                       if col not in ['fixture_id', 'league', 'season', 'label']]
        
        X = self.df[feature_cols].copy()
        y = self.df['label'].copy()
        
        logger.info(f"📊 Features selecionadas: {len(feature_cols)}")
        
        # Converter todas as features para numeric (NaN para não-conversíveis)
        X = X.apply(pd.to_numeric, errors='coerce')
        
        # Tratar valores faltantes
        missing = X.isnull().sum()
        missing_cols = missing[missing > 0]
        
        if len(missing_cols) > 0:
            logger.warning(f"⚠️ Colunas com valores faltantes: {len(missing_cols)}")
            for col in missing_cols.index[:5]:  # Log top 5
                logger.warning(f"   {col}: {missing[col]} missing ({missing[col]/len(X)*100:.1f}%)")
            
            # Preencher com mediana
            X = X.fillna(X.median())
            logger.info(f"✅ Valores faltantes preenchidos com mediana")
        
        # Remover features com variância zero (constantes)
        zero_var_cols = X.columns[X.var() == 0].tolist()
        if zero_var_cols:
            logger.warning(f"⚠️ Removendo {len(zero_var_cols)} features com variância zero")
            X = X.drop(columns=zero_var_cols)
        
        # Train/Test split
        from sklearn.model_selection import train_test_split
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        logger.info(f"✅ Split realizado:")
        logger.info(f"   Treino: {len(self.X_train)} partidas ({(1-test_size)*100:.0f}%)")
        logger.info(f"   Teste: {len(self.X_test)} partidas ({test_size*100:.0f}%)")
        
        # Log feature importance (correlação simples)
        logger.info(f"\n📊 Top 10 features mais correlacionadas com resultado:")
        correlations = X.corrwith(y).abs().sort_values(ascending=False)
        for i, (feature, corr) in enumerate(correlations.head(10).items(), 1):
            logger.info(f"   {i}. {feature}: {corr:.3f}")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def train_xgboost(self):
        """Treina modelo XGBoost"""
        logger.info("\n" + "="*80)
        logger.info("🚀 TREINANDO XGBOOST")
        logger.info("="*80)
        
        from xgboost import XGBClassifier
        from sklearn.model_selection import cross_val_score
        
        # Configuração otimizada para futebol
        model = XGBClassifier(
            max_depth=6,                # Profundidade moderada (evita overfit)
            n_estimators=300,           # Número de árvores
            learning_rate=0.05,         # Taxa de aprendizado conservadora
            subsample=0.8,              # 80% dos dados por árvore (robustez)
            colsample_bytree=0.8,       # 80% das features por árvore
            objective='multi:softmax',  # Classificação multi-classe
            num_class=3,                # 0=Casa, 1=Empate, 2=Fora
            eval_metric='mlogloss',     # Métrica de avaliação
            random_state=42,
            n_jobs=-1                   # Usar todos os cores
        )
        
        logger.info(f"⚙️ Hiperparâmetros:")
        logger.info(f"   max_depth: {model.max_depth}")
        logger.info(f"   n_estimators: {model.n_estimators}")
        logger.info(f"   learning_rate: {model.learning_rate}")
        
        # Cross-validation (k-fold)
        logger.info(f"\n🔄 Cross-validation (5-fold)...")
        cv_scores = cross_val_score(model, self.X_train, self.y_train, 
                                    cv=5, scoring='accuracy', n_jobs=-1)
        
        logger.info(f"✅ CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        logger.info(f"   Folds: {[f'{s:.3f}' for s in cv_scores]}")
        
        # Treinar modelo final
        logger.info(f"\n🎯 Treinando modelo final...")
        model.fit(
            self.X_train, self.y_train,
            eval_set=[(self.X_test, self.y_test)],
            verbose=False
        )
        
        self.models['xgboost'] = model
        
        # Avaliar
        train_acc = model.score(self.X_train, self.y_train)
        test_acc = model.score(self.X_test, self.y_test)
        
        logger.info(f"✅ Treino finalizado!")
        logger.info(f"   Acurácia Treino: {train_acc:.4f} ({train_acc*100:.2f}%)")
        logger.info(f"   Acurácia Teste: {test_acc:.4f} ({test_acc*100:.2f}%)")
        
        # Feature importance
        logger.info(f"\n📊 Top 15 features mais importantes:")
        feature_importance = pd.DataFrame({
            'feature': self.X_train.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for i, row in feature_importance.head(15).iterrows():
            logger.info(f"   {i+1}. {row['feature']}: {row['importance']:.4f}")
        
        return model
    
    def train_lightgbm(self):
        """Treina modelo LightGBM (alternativa ao XGBoost)"""
        logger.info("\n" + "="*80)
        logger.info("🚀 TREINANDO LIGHTGBM")
        logger.info("="*80)
        
        try:
            from lightgbm import LGBMClassifier
        except ImportError:
            logger.warning("⚠️ LightGBM não instalado. Execute: pip install lightgbm")
            return None
        
        from sklearn.model_selection import cross_val_score
        
        model = LGBMClassifier(
            max_depth=6,
            n_estimators=300,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multiclass',
            num_class=3,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        
        # Cross-validation
        logger.info(f"🔄 Cross-validation (5-fold)...")
        cv_scores = cross_val_score(model, self.X_train, self.y_train, 
                                    cv=5, scoring='accuracy', n_jobs=-1)
        
        logger.info(f"✅ CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Treinar
        model.fit(self.X_train, self.y_train)
        
        self.models['lightgbm'] = model
        
        test_acc = model.score(self.X_test, self.y_test)
        logger.info(f"✅ Acurácia Teste: {test_acc:.4f} ({test_acc*100:.2f}%)")
        
        return model
    
    def evaluate_all(self):
        """Avalia todos os modelos treinados"""
        logger.info("\n" + "="*80)
        logger.info("📊 AVALIAÇÃO DETALHADA")
        logger.info("="*80)
        
        from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
        
        for model_name, model in self.models.items():
            logger.info(f"\n{'='*80}")
            logger.info(f"📈 {model_name.upper()}")
            logger.info(f"{'='*80}")
            
            # Predições
            y_pred = model.predict(self.X_test)
            
            # Acurácia
            acc = accuracy_score(self.y_test, y_pred)
            logger.info(f"🎯 Acurácia: {acc:.4f} ({acc*100:.2f}%)")
            
            # Classification report
            logger.info(f"\n📊 Métricas por classe:")
            report = classification_report(self.y_test, y_pred, 
                                          target_names=['Casa', 'Empate', 'Fora'],
                                          digits=3)
            logger.info(f"\n{report}")
            
            # Confusion matrix
            logger.info(f"📊 Matriz de Confusão:")
            cm = confusion_matrix(self.y_test, y_pred)
            logger.info(f"\n           Pred Casa  Pred Empate  Pred Fora")
            logger.info(f"Real Casa      {cm[0][0]:4d}        {cm[0][1]:4d}        {cm[0][2]:4d}")
            logger.info(f"Real Empate    {cm[1][0]:4d}        {cm[1][1]:4d}        {cm[1][2]:4d}")
            logger.info(f"Real Fora      {cm[2][0]:4d}        {cm[2][1]:4d}        {cm[2][2]:4d}")
            
            # Salvar resultados
            self.results[model_name] = {
                'accuracy': float(acc),
                'confusion_matrix': cm.tolist(),
                'predictions': y_pred.tolist()
            }
    
    def save_models(self, output_dir='trained_models'):
        """Salva modelos treinados"""
        logger.info("\n" + "="*80)
        logger.info("💾 SALVANDO MODELOS")
        logger.info("="*80)
        
        output_path = Path(__file__).parent / output_dir
        output_path.mkdir(exist_ok=True)
        
        for model_name, model in self.models.items():
            model_file = output_path / f"{model_name}_1x2.pkl"
            joblib.dump(model, model_file)
            logger.info(f"✅ {model_name}: {model_file}")
        
        # Salvar feature names
        feature_file = output_path / "feature_names.json"
        with open(feature_file, 'w') as f:
            json.dump(self.X_train.columns.tolist(), f, indent=2)
        logger.info(f"✅ Feature names: {feature_file}")
        
        # Salvar metadata
        metadata_file = output_path / "training_metadata.json"
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'n_train': len(self.X_train),
            'n_test': len(self.X_test),
            'n_features': len(self.X_train.columns),
            'results': self.results
        }
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✅ Metadata: {metadata_file}")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Treinar modelos ML para predição 1X2')
    parser.add_argument('--dataset', type=str, default='training_dataset.json',
                       help='Arquivo do dataset (default: training_dataset.json)')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Proporção de teste (default: 0.2 = 20%)')
    parser.add_argument('--models', type=str, nargs='+', 
                       default=['xgboost', 'lightgbm'],
                       help='Modelos a treinar (default: xgboost lightgbm)')
    
    args = parser.parse_args()
    
    # Inicializar trainer
    trainer = FootballMLTrainer(dataset_path=args.dataset)
    
    # Pipeline completo
    trainer.load_dataset()
    trainer.preprocess(test_size=args.test_size)
    
    # Treinar modelos selecionados
    if 'xgboost' in args.models:
        trainer.train_xgboost()
    
    if 'lightgbm' in args.models:
        trainer.train_lightgbm()
    
    # Avaliar
    trainer.evaluate_all()
    
    # Salvar
    trainer.save_models()
    
    logger.info("\n" + "="*80)
    logger.info("✅ TREINO FINALIZADO COM SUCESSO!")
    logger.info("="*80)


if __name__ == '__main__':
    main()
