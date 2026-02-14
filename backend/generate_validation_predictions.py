"""
Gera predições dos 3 modelos (Poisson, ML, Market) para calibração.

Este script prepara os dados necessários para calibrate_ensemble_weights.py

Uso:
    python generate_validation_predictions.py

Resultado:
    ml_training/validation_predictions.pkl com estrutura:
    {
        'poisson': array([[p_home, p_draw, p_away], ...]),
        'ml': array([[p_home, p_draw, p_away], ...]),
        'market': array([[p_home, p_draw, p_away], ...]),
        'labels': array([0, 2, 1, ...]),
        'context_confidences': array([0.5, 0.8, 0.3, ...])
    }
"""

import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from datetime import datetime
import sys

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

from apps.analysis.services.statistical_models import StatisticalModels
from apps.analysis.services.ml_integration import MLModel
from apps.analysis.services.context_analyzer import ContextAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationDataGenerator:
    """
    Gera predições dos 3 modelos para calibração.
    """
    
    def __init__(self):
        self.poisson_model = StatisticalModels()
        self.ml_model = MLModel()
        self.context_analyzer = ContextAnalyzer()
        
        logger.info("✅ Modelos carregados")
    
    def load_historical_matches(self, data_path='ml_training/processed_880_liga.pkl'):
        """
        Carrega partidas históricas processadas.
        
        Usamos conjunto de validação (últimos 20% dos dados).
        """
        if not Path(data_path).exists():
            logger.error(f"❌ Arquivo não encontrado: {data_path}")
            return None
        
        data = pd.read_pickle(data_path)
        logger.info(f"✅ Carregados {len(data)} jogos históricos")
        
        # Dividir em treino (80%) e validação (20%)
        split_idx = int(len(data) * 0.8)
        validation_data = data.iloc[split_idx:].copy()
        
        logger.info(f"📊 Usando {len(validation_data)} jogos para validação")
        
        return validation_data
    
    def generate_predictions(self, matches_df):
        """
        Gera predições dos 3 modelos para cada partida.
        
        Returns:
            dict com arrays de predições
        """
        logger.info("\n🔮 Gerando predições...")
        
        poisson_preds = []
        ml_preds = []
        market_preds = []
        labels = []
        context_confs = []
        
        for idx, row in matches_df.iterrows():
            if idx % 20 == 0:
                logger.info(f"   Processando {idx+1}/{len(matches_df)}...")
            
            try:
                # 1. Poisson prediction
                poisson_result = self.poisson_model.predict_match(
                    home_strength=row.get('home_attack_strength', 1.5),
                    away_strength=row.get('away_attack_strength', 1.5),
                    home_defense=row.get('home_defense_strength', 1.0),
                    away_defense=row.get('away_defense_strength', 1.0)
                )
                
                poisson_prob = [
                    poisson_result['probabilities']['home_win'],
                    poisson_result['probabilities']['draw'],
                    poisson_result['probabilities']['away_win']
                ]
                
                # 2. ML prediction
                # Preparar features (109 features esperadas)
                features = self._prepare_features(row)
                
                ml_result = self.ml_model.predict_1x2(
                    features=features,
                    league_id=row.get('league_id', 39),
                    is_cup=row.get('is_cup', False)
                )
                
                ml_prob = [
                    ml_result.get('home_win', 0.33),
                    ml_result.get('draw', 0.33),
                    ml_result.get('away_win', 0.33)
                ]
                
                # 3. Market prior (simulado se não disponível)
                if 'market_home_prob' in row and pd.notna(row['market_home_prob']):
                    market_prob = [
                        row['market_home_prob'],
                        row['market_draw_prob'],
                        row['market_away_prob']
                    ]
                else:
                    # Usar distribuição uniforme como fallback
                    market_prob = [0.33, 0.33, 0.33]
                
                # 4. Context confidence (se disponível)
                context_conf = row.get('context_confidence', 0.0)
                
                # 5. Label real
                label = int(row['result'])  # 0=home, 1=draw, 2=away
                
                # Adicionar às listas
                poisson_preds.append(poisson_prob)
                ml_preds.append(ml_prob)
                market_preds.append(market_prob)
                labels.append(label)
                context_confs.append(context_conf)
                
            except Exception as e:
                logger.warning(f"   ⚠️ Erro no jogo {idx}: {e}")
                continue
        
        logger.info(f"✅ Geradas {len(labels)} predições")
        
        return {
            'poisson': np.array(poisson_preds),
            'ml': np.array(ml_preds),
            'market': np.array(market_preds),
            'labels': np.array(labels),
            'context_confidences': np.array(context_confs)
        }
    
    def _prepare_features(self, row):
        """
        Prepara dicionário de features esperado pelo ML model.
        """
        # Mapear colunas do dataframe para estrutura de features
        features = {
            'strength': {
                'home_attack_strength': row.get('home_attack_strength', 1.5),
                'away_attack_strength': row.get('away_attack_strength', 1.5),
                'home_defense_strength': row.get('home_defense_strength', 1.0),
                'away_defense_strength': row.get('away_defense_strength', 1.0),
                'strength_differential': row.get('strength_differential', 0.0)
            },
            'form': {
                'home_form_l5': row.get('home_form_l5', 0.5),
                'away_form_l5': row.get('away_form_l5', 0.5),
                'form_differential': row.get('form_differential', 0.0)
            },
            'h2h': {
                'h2h_games': row.get('h2h_games', 0),
                'h2h_home_wins': row.get('h2h_home_wins', 0),
                'h2h_draws': row.get('h2h_draws', 0),
                'h2h_away_wins': row.get('h2h_away_wins', 0)
            },
            'context': {
                'is_derby': row.get('is_derby', False),
                'home_motivation': row.get('home_motivation', 0.5),
                'away_motivation': row.get('away_motivation', 0.5)
            }
        }
        
        return features
    
    def save_predictions(self, predictions, output_path='ml_training/validation_predictions.pkl'):
        """
        Salva predições para uso posterior.
        """
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(predictions, output_path)
        logger.info(f"\n💾 Predições salvas em: {output_path}")
        
        # Estatísticas
        logger.info(f"\n📊 ESTATÍSTICAS:")
        logger.info(f"   Total de jogos: {len(predictions['labels'])}")
        logger.info(f"   Distribuição real:")
        labels_dist = np.bincount(predictions['labels'], minlength=3)
        logger.info(f"      Home: {labels_dist[0]} ({labels_dist[0]/len(predictions['labels'])*100:.1f}%)")
        logger.info(f"      Draw: {labels_dist[1]} ({labels_dist[1]/len(predictions['labels'])*100:.1f}%)")
        logger.info(f"      Away: {labels_dist[2]} ({labels_dist[2]/len(predictions['labels'])*100:.1f}%)")


def main():
    """
    Executa geração completa.
    """
    logger.info("="*80)
    logger.info("🔮 GERAÇÃO DE PREDIÇÕES PARA CALIBRAÇÃO")
    logger.info("="*80)
    
    generator = ValidationDataGenerator()
    
    # 1. Carregar dados históricos
    matches_df = generator.load_historical_matches()
    
    if matches_df is None or len(matches_df) == 0:
        logger.error("\n❌ Sem dados para processar")
        logger.info("\n💡 Certifique-se que existe: ml_training/processed_880_liga.pkl")
        logger.info("   Gerado por: python prepare_training_data.py")
        return
    
    # 2. Gerar predições
    predictions = generator.generate_predictions(matches_df)
    
    if len(predictions['labels']) < 50:
        logger.error(f"\n❌ Poucas predições geradas ({len(predictions['labels'])})")
        logger.info("   Necessário mínimo de 50 para calibração confiável")
        return
    
    # 3. Salvar
    generator.save_predictions(predictions)
    
    logger.info("\n✅ CONCLUÍDO!")
    logger.info(f"\n💡 PRÓXIMO PASSO:")
    logger.info(f"   python calibrate_ensemble_weights.py")
    logger.info("="*80)


if __name__ == '__main__':
    main()
