"""
Script para RETREINAR modelo ML com dados de LIGAS + COPAS

ESTRATÉGIA:
1. Carregar dados atuais do modelo (880 partidas de ligas)
2. Carregar novos dados de copas (800 partidas)
3. Combinar datasets (total: ~1680 partidas)
4. Retreinar XGBoost com dataset balanceado
5. Validar performance em ambos os tipos de competição
"""
import os
import sys
import django
import json
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HybridModelTrainer:
    """Retreina modelo com dados de ligas + copas"""
    
    def __init__(self):
        self.league_data = []
        self.cup_data = []
        self.combined_data = []
        self.model = None
        self.feature_names = None
        
    def load_league_data(self, league_dataset='ml_training/league_training_dataset.json'):
        """Carrega dados de ligas (880 partidas atuais)"""
        logger.info("="*80)
        logger.info("📂 CARREGANDO DADOS DE LIGAS")
        logger.info("="*80)
        
        league_path = Path(__file__).parent / league_dataset
        
        # Se não existir, criar a partir do banco de dados
        if not league_path.exists():
            logger.warning(f"⚠️ Dataset de ligas não encontrado: {league_path}")
            logger.info("📊 Carregando do banco de dados Django...")
            
            from apps.matches.models import Match
            from apps.analysis.services.match_enricher import MatchDataEnricher
            from apps.analysis.services.feature_engineer import FeatureEngineer
            
            enricher = MatchDataEnricher()
            engineer = FeatureEngineer()
            
            # Buscar partidas de LIGAS (excluir copas)
            league_matches = Match.objects.filter(
                status='finished',
                home_score__isnull=False,
                away_score__isnull=False,
                league__isnull=False
            ).exclude(
                league__name__icontains='cup'
            ).exclude(
                league__name__icontains='copa'
            ).exclude(
                league__name__icontains='pokal'
            )[:1000]
            
            logger.info(f"   📋 {league_matches.count()} partidas de ligas encontradas")
            
            for match in league_matches[:880]:  # Limitar a 880 para balancear
                try:
                    # Processar como no script collect_cup_data.py
                    match_data = {'api_id': match.api_football_id}
                    enriched = enricher.enrich(match_data)
                    features = engineer.engineer_all_features(enriched)
                    
                    # Flatten features
                    flat_features = {}
                    for category, feature_dict in features.items():
                        if isinstance(feature_dict, dict):
                            for key, value in feature_dict.items():
                                flat_features[f"{category}.{key}"] = value
                    
                    # Label
                    if match.home_score > match.away_score:
                        label = 0
                    elif match.away_score > match.home_score:
                        label = 2
                    else:
                        label = 1
                    
                    self.league_data.append({
                        'fixture_id': match.api_football_id,
                        'competition_type': 'league',
                        'features': flat_features,
                        'label': label
                    })
                
                except Exception as e:
                    logger.error(f"❌ Erro ao processar match {match.id}: {e}")
                    continue
        
        else:
            # Carregar de arquivo JSON
            with open(league_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.league_data = data.get('matches', [])
        
        logger.info(f"✅ {len(self.league_data)} partidas de LIGAS carregadas")
        logger.info("="*80)
        
    def load_cup_data(self, cup_dataset='ml_training/cup_training_dataset.json'):
        """Carrega dados de copas (800 partidas)"""
        logger.info("\n" + "="*80)
        logger.info("🏆 CARREGANDO DADOS DE COPAS")
        logger.info("="*80)
        
        cup_path = Path(__file__).parent / cup_dataset
        
        if not cup_path.exists():
            raise FileNotFoundError(
                f"❌ Dataset de copas não encontrado: {cup_path}\n"
                "Execute: python collect_cup_data.py"
            )
        
        with open(cup_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.cup_data = data.get('matches', [])
            metadata = data.get('metadata', {})
        
        logger.info(f"✅ {len(self.cup_data)} partidas de COPAS carregadas")
        logger.info(f"   Knockout: {metadata.get('knockout_matches', 'N/A')}")
        logger.info(f"   Group Stage: {metadata.get('group_stage_matches', 'N/A')}")
        logger.info("="*80)
        
    def combine_datasets(self):
        """Combina datasets de ligas + copas"""
        logger.info("\n" + "="*80)
        logger.info("🔀 COMBINANDO DATASETS")
        logger.info("="*80)
        
        self.combined_data = self.league_data + self.cup_data
        
        # Estatísticas
        total = len(self.combined_data)
        leagues = len(self.league_data)
        cups = len(self.cup_data)
        
        logger.info(f"📊 DATASET COMBINADO:")
        logger.info(f"   Total: {total} partidas")
        logger.info(f"   Ligas: {leagues} ({leagues/total*100:.1f}%)")
        logger.info(f"   Copas: {cups} ({cups/total*100:.1f}%)")
        
        # Distribuição de labels
        labels = [m['label'] for m in self.combined_data]
        logger.info(f"\n   Distribuição de Resultados:")
        logger.info(f"      Casa (0): {labels.count(0)} ({labels.count(0)/total*100:.1f}%)")
        logger.info(f"      Empate (1): {labels.count(1)} ({labels.count(1)/total*100:.1f}%)")
        logger.info(f"      Fora (2): {labels.count(2)} ({labels.count(2)/total*100:.1f}%)")
        logger.info("="*80)
        
    def prepare_training_data(self):
        """Converte dados para formato sklearn"""
        logger.info("\n" + "="*80)
        logger.info("🔧 PREPARANDO DADOS PARA TREINO")
        logger.info("="*80)
        
        # Coletar todos os nomes de features
        all_feature_names = set()
        for match in self.combined_data:
            all_feature_names.update(match['features'].keys())
        
        self.feature_names = sorted(list(all_feature_names))
        logger.info(f"   📋 {len(self.feature_names)} features detectadas")
        
        # Criar matriz X e vetor y
        X = []
        y = []
        
        for match in self.combined_data:
            # Criar vetor de features (preencher NaN para features faltantes)
            feature_vector = []
            for fname in self.feature_names:
                value = match['features'].get(fname, np.nan)
                
                # Converter para numérico
                if isinstance(value, (int, float, np.number)):
                    feature_vector.append(float(value))
                elif isinstance(value, bool):
                    feature_vector.append(1.0 if value else 0.0)
                elif value is None or (isinstance(value, float) and np.isnan(value)):
                    feature_vector.append(0.0)  # Imputar 0 para NaN
                else:
                    # String ou outro tipo - tentar converter
                    try:
                        feature_vector.append(float(value))
                    except:
                        feature_vector.append(0.0)
            
            X.append(feature_vector)
            y.append(match['label'])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"   ✅ X shape: {X.shape}")
        logger.info(f"   ✅ y shape: {y.shape}")
        
        # Train/test split (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"\n   📊 Train/Test Split:")
        logger.info(f"      Train: {len(X_train)} partidas")
        logger.info(f"      Test: {len(X_test)} partidas")
        logger.info("="*80)
        
        return X_train, X_test, y_train, y_test
    
    def train_model(self, X_train, y_train):
        """Treina modelo XGBoost"""
        logger.info("\n" + "="*80)
        logger.info("🤖 TREINANDO MODELO XGBOOST")
        logger.info("="*80)
        
        try:
            import xgboost as xgb
            
            self.model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                eval_metric='mlogloss',
                use_label_encoder=False
            )
            
            logger.info("   ⚙️ Hiperparâmetros:")
            logger.info(f"      n_estimators: 200")
            logger.info(f"      max_depth: 6")
            logger.info(f"      learning_rate: 0.1")
            
            self.model.fit(X_train, y_train)
            
            logger.info("   ✅ Modelo treinado com sucesso!")
            logger.info("="*80)
        
        except ImportError:
            logger.error("❌ XGBoost não instalado. Instale com: pip install xgboost")
            raise
    
    def evaluate_model(self, X_test, y_test):
        """Avalia performance do modelo"""
        logger.info("\n" + "="*80)
        logger.info("📊 AVALIANDO MODELO")
        logger.info("="*80)
        
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"   🎯 Acurácia no Test Set: {accuracy*100:.2f}%")
        
        logger.info(f"\n   📋 Classification Report:")
        report = classification_report(y_test, y_pred, target_names=['Casa', 'Empate', 'Fora'])
        for line in report.split('\n'):
            logger.info(f"      {line}")
        
        logger.info(f"\n   🔢 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        logger.info(f"      {cm}")
        logger.info("="*80)
        
        return accuracy
    
    def save_model(self, output_path='ml_training/trained_models/xgboost_1x2_hybrid.pkl'):
        """Salva modelo retreinado"""
        logger.info("\n" + "="*80)
        logger.info("💾 SALVANDO MODELO")
        logger.info("="*80)
        
        model_path = Path(__file__).parent / output_path
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Salvar modelo
        joblib.dump(self.model, model_path)
        logger.info(f"   ✅ Modelo salvo: {model_path}")
        
        # Salvar feature names
        feature_path = model_path.parent / "feature_names_hybrid.json"
        with open(feature_path, 'w') as f:
            json.dump(self.feature_names, f, indent=2)
        logger.info(f"   ✅ Features salvas: {feature_path}")
        
        # Criar relatório
        report_path = Path(__file__).parent / 'retrain_hybrid_report.json'
        report = {
            'model_path': str(model_path),
            'feature_names_path': str(feature_path),
            'total_features': len(self.feature_names),
            'training_data': {
                'total_matches': len(self.combined_data),
                'league_matches': len(self.league_data),
                'cup_matches': len(self.cup_data)
            },
            'retrained_at': datetime.now().isoformat()
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"   ✅ Relatório salvo: {report_path}")
        logger.info("="*80)


if __name__ == '__main__':
    logger.info("\n" + "🎯"*40)
    logger.info("RETREINO DE MODELO ML - LIGAS + COPAS")
    logger.info("🎯"*40 + "\n")
    
    trainer = HybridModelTrainer()
    
    # 1. Carregar dados
    trainer.load_league_data()
    trainer.load_cup_data()
    
    # 2. Combinar
    trainer.combine_datasets()
    
    # 3. Preparar treino
    X_train, X_test, y_train, y_test = trainer.prepare_training_data()
    
    # 4. Treinar
    trainer.train_model(X_train, y_train)
    
    # 5. Avaliar
    accuracy = trainer.evaluate_model(X_test, y_test)
    
    # 6. Salvar
    trainer.save_model()
    
    logger.info("\n" + "="*80)
    logger.info("🎉 RETREINO CONCLUÍDO COM SUCESSO!")
    logger.info("="*80)
    logger.info(f"📊 Acurácia Final: {accuracy*100:.2f}%")
    logger.info(f"💾 Modelo salvo: ml_training/trained_models/xgboost_1x2_hybrid.pkl")
    logger.info("\n📝 PRÓXIMOS PASSOS:")
    logger.info("   1. Validar modelo com partidas de teste")
    logger.info("   2. Atualizar ml_integration.py para usar novo modelo:")
    logger.info("      model_path='ml_training/trained_models/xgboost_1x2_hybrid.pkl'")
    logger.info("="*80)
