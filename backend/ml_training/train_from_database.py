"""
Treina modelo ML usando APENAS dados do banco de dados
SEM fazer chamadas à API
"""

import os
import sys
import json
import django
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class DatabaseFeatureExtractor:
    """Extrai features diretamente do banco de dados SEM usar API"""
    
    def extract_basic_features(self, match):
        """Extrai features básicas da partida"""
        features = {}
        
        # Resultado da partida (label)
        if match.home_score > match.away_score:
            features['label'] = 0  # Casa
        elif match.away_score > match.home_score:
            features['label'] = 2  # Fora
        else:
            features['label'] = 1  # Empate
        
        # Gols
        features['total_goals'] = match.home_score + match.away_score
        features['home_goals'] = match.home_score
        features['away_goals'] = match.away_score
        features['goal_diff'] = match.home_score - match.away_score
        
        # Metadata
        features['fixture_id'] = match.api_football_id
        features['league_id'] = match.league.api_football_id if match.league else 0
        features['home_team_id'] = match.home_team.api_football_id if match.home_team else 0
        features['away_team_id'] = match.away_team.api_football_id if match.away_team else 0
        
        return features
    
    def extract_cached_stats(self, match):
        """Extrai features do stats_cache se disponível"""
        features = {}
        
        if not match.stats_cache:
            return self._default_stats_features()
        
        try:
            stats = match.stats_cache
            
            # Standings (força dos times)
            if 'standings' in stats and stats['standings']:
                home_std = stats['standings'].get('home') if isinstance(stats['standings'], dict) else None
                away_std = stats['standings'].get('away') if isinstance(stats['standings'], dict) else None
                
                features['home_position'] = home_std.get('rank', 10) if home_std else 10
                features['away_position'] = away_std.get('rank', 10) if away_std else 10
                features['home_points'] = home_std.get('points', 0) if home_std else 30
                features['away_points'] = away_std.get('points', 0) if away_std else 30
                features['position_diff'] = features['away_position'] - features['home_position']
                features['points_diff'] = features['home_points'] - features['away_points']
                
                # Força calculada (goals_for/against) - SAFE para None
                home_gf = home_std.get('all', {}).get('goals', {}).get('for', 0) if home_std else 0
                home_ga = home_std.get('all', {}).get('goals', {}).get('against', 1) if home_std else 1
                away_gf = away_std.get('all', {}).get('goals', {}).get('for', 0) if away_std else 0
                away_ga = away_std.get('all', {}).get('goals', {}).get('against', 1) if away_std else 1
                
                features['home_strength'] = home_gf / max(home_ga, 1)
                features['away_strength'] = away_gf / max(away_ga, 1)
                features['strength_diff'] = features['home_strength'] - features['away_strength']
            else:
                # Defaults se não tem standings
                features.update({
                    'home_position': 10, 'away_position': 10,
                    'home_points': 30, 'away_points': 30,
                    'position_diff': 0, 'points_diff': 0,
                    'home_strength': 1.0, 'away_strength': 1.0,
                    'strength_diff': 0.0
                })
            
            # Team Stats (médias de gols) - SAFE para None
            if 'home_stats' in stats and stats['home_stats']:
                home_st = stats['home_stats']
                features['home_goals_avg'] = float(home_st.get('goals_avg', 1.5))
                features['home_goals_against_avg'] = float(home_st.get('goals_against_avg', 1.5))
                if features['home_goals_avg'] != 1.5:  # Debug
                    logger.info(f"   ✅ Home real: {features['home_goals_avg']}")
            else:
                features['home_goals_avg'] = 1.5
                features['home_goals_against_avg'] = 1.5
            
            if 'away_stats' in stats and stats['away_stats']:
                away_st = stats['away_stats']
                features['away_goals_avg'] = float(away_st.get('goals_avg', 1.5))
                features['away_goals_against_avg'] = float(away_st.get('goals_against_avg', 1.5))
            else:
                features['away_goals_avg'] = 1.5
                features['away_goals_against_avg'] = 1.5
            
            # H2H
            if 'h2h' in stats and stats['h2h']:
                h2h = stats['h2h']
                features['h2h_home_wins'] = h2h.get('home_wins', 0)
                features['h2h_draws'] = h2h.get('draws', 0)
                features['h2h_away_wins'] = h2h.get('away_wins', 0)
                features['h2h_total'] = h2h.get('total', 0)
                
                if features['h2h_total'] > 0:
                    features['h2h_home_win_pct'] = features['h2h_home_wins'] / features['h2h_total']
                    features['h2h_draw_pct'] = features['h2h_draws'] / features['h2h_total']
                else:
                    features['h2h_home_win_pct'] = 0.33
                    features['h2h_draw_pct'] = 0.33
            else:
                features.update({
                    'h2h_home_wins': 0, 'h2h_draws': 0, 'h2h_away_wins': 0,
                    'h2h_total': 0, 'h2h_home_win_pct': 0.33, 'h2h_draw_pct': 0.33
                })
            
            # Odds (market prior)
            if 'odds' in stats and stats['odds']:
                odds = stats['odds']
                features['odds_home'] = float(odds.get('home', 2.5))
                features['odds_draw'] = float(odds.get('draw', 3.0))
                features['odds_away'] = float(odds.get('away', 2.5))
                
                # Converter odds em probabilidades implícitas
                total_prob = (1/features['odds_home'] + 1/features['odds_draw'] + 1/features['odds_away'])
                features['market_home_prob'] = (1/features['odds_home']) / total_prob
                features['market_draw_prob'] = (1/features['odds_draw']) / total_prob
                features['market_away_prob'] = (1/features['odds_away']) / total_prob
            else:
                features.update({
                    'odds_home': 2.5, 'odds_draw': 3.0, 'odds_away': 2.5,
                    'market_home_prob': 0.33, 'market_draw_prob': 0.33, 'market_away_prob': 0.33
                })
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair stats_cache: {e}")
            return self._default_stats_features()
        
        return features
    
    def _default_stats_features(self):
        """Features padrão quando não há dados"""
        return {
            'home_position': 10, 'away_position': 10,
            'home_points': 30, 'away_points': 30,
            'position_diff': 0, 'points_diff': 0,
            'home_strength': 1.0, 'away_strength': 1.0, 'strength_diff': 0.0,
            'home_goals_avg': 1.5, 'home_goals_against_avg': 1.5,
            'away_goals_avg': 1.5, 'away_goals_against_avg': 1.5,
            'h2h_home_wins': 0, 'h2h_draws': 0, 'h2h_away_wins': 0,
            'h2h_total': 0, 'h2h_home_win_pct': 0.33, 'h2h_draw_pct': 0.33,
            'odds_home': 2.5, 'odds_draw': 3.0, 'odds_away': 2.5,
            'market_home_prob': 0.33, 'market_draw_prob': 0.33, 'market_away_prob': 0.33
        }
    
    def extract_all_features(self, match):
        """Extrai todas as features de uma partida"""
        features = {}
        features.update(self.extract_basic_features(match))
        features.update(self.extract_cached_stats(match))
        return features


class SimplifiedMLTrainer:
    """Treina modelo ML de forma simplificada"""
    
    def __init__(self):
        self.extractor = DatabaseFeatureExtractor()
        self.df = None
        self.model = None
    
    def load_dataset_from_db(self, limit=None):
        """Carrega dataset do banco de dados"""
        logger.info("📂 CARREGANDO DATASET DO BANCO DE DADOS (SEM API)")
        
        query = Match.objects.filter(
            status='finished',
            home_score__isnull=False,
            away_score__isnull=False,
            stats_cache__isnull=False  # APENAS partidas COM stats_cache
        ).select_related('league', 'home_team', 'away_team').order_by('-match_date')
        
        if limit:
            query = query[:limit]
        
        matches = list(query)
        logger.info(f"📊 Total de partidas encontradas: {len(matches)}")
        
        rows = []
        for i, match in enumerate(matches):
            try:
                features = self.extractor.extract_all_features(match)
                rows.append(features)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"   Processadas {i+1}/{len(matches)} partidas...")
            
            except Exception as e:
                logger.warning(f"⚠️ Erro na partida {match.api_football_id}: {e}")
                continue
        
        self.df = pd.DataFrame(rows)
        logger.info(f"✅ Dataset criado: {len(self.df)} partidas, {len(self.df.columns)} colunas")
        logger.info(f"📊 Colunas: {list(self.df.columns)}")
        
        # Distribuição de labels
        if 'label' in self.df.columns:
            label_dist = self.df['label'].value_counts()
            logger.info(f"📊 Distribuição labels: Casa={label_dist.get(0, 0)}, Empate={label_dist.get(1, 0)}, Fora={label_dist.get(2, 0)}")
    
    def preprocess(self):
        """Preprocessa dados"""
        logger.info("🔧 PREPROCESSANDO DADOS")
        
        # Separar features e labels
        # REMOVER features que contêm informação do resultado (data leakage!)
        meta_cols = ['fixture_id', 'league_id', 'home_team_id', 'away_team_id', 'label']
        leakage_cols = ['total_goals', 'home_goals', 'away_goals', 'goal_diff']  # Essas features só existem APÓS o jogo!
        
        exclude_cols = meta_cols + leakage_cols
        feature_cols = [c for c in self.df.columns if c not in exclude_cols]
        
        X = self.df[feature_cols].copy()
        y = self.df['label'].copy()
        
        # Tratar valores infinitos/NaN
        X.replace([np.inf, -np.inf], np.nan, inplace=True)
        X.fillna(X.mean(), inplace=True)
        
        logger.info(f"✅ X shape: {X.shape}, y shape: {y.shape}")
        logger.info(f"✅ Features: {list(X.columns)}")
        
        return X, y
    
    def train(self):
        """Treina modelo"""
        logger.info("🎯 TREINANDO MODELO ML")
        
        X, y = self.preprocess()
        
        # Tentar XGBoost, senão LogisticRegression
        try:
            import xgboost as xgb
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            logger.info("   Usando XGBoost")
        except ImportError:
            from sklearn.linear_model import LogisticRegression
            self.model = LogisticRegression(max_iter=1000, random_state=42)
            logger.info("   Usando LogisticRegression (XGBoost não disponível)")
        
        # Train/test split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        logger.info(f"   Train: {X_train.shape}, Test: {X_test.shape}")
        
        # Treinar
        self.model.fit(X_train, y_train)
        
        # Avaliar
        train_acc = self.model.score(X_train, y_train)
        test_acc = self.model.score(X_test, y_test)
        
        logger.info(f"✅ Acurácia Treino: {train_acc:.2%}")
        logger.info(f"✅ Acurácia Teste: {test_acc:.2%}")
        
        # Predictions
        y_pred = self.model.predict(X_test)
        
        from sklearn.metrics import classification_report
        logger.info("\n📊 CLASSIFICATION REPORT:")
        print(classification_report(y_test, y_pred, target_names=['Casa', 'Empate', 'Fora']))
    
    def save_model(self, path='ml_training/trained_models/simple_model.pkl'):
        """Salva modelo treinado"""
        import pickle
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        
        logger.info(f"💾 Modelo salvo em: {path}")
    
    def save_dataset(self, path='ml_training/database_dataset.csv'):
        """Salva dataset para análise"""
        self.df.to_csv(path, index=False)
        logger.info(f"💾 Dataset salvo em: {path}")


def main():
    logger.info("="*80)
    logger.info("🚀 TREINAMENTO ML - SOMENTE BANCO DE DADOS (SEM API)")
    logger.info("="*80)
    
    trainer = SimplifiedMLTrainer()
    
    # Carregar dados (começar com 1000 para testar)
    trainer.load_dataset_from_db(limit=1000)
    
    if len(trainer.df) < 100:
        logger.error("❌ Dataset muito pequeno! Precisa de pelo menos 100 partidas.")
        return
    
    # Salvar dataset
    trainer.save_dataset()
    
    # Treinar
    trainer.train()
    
    # Salvar modelo
    trainer.save_model()
    
    logger.info("="*80)
    logger.info("✅ TREINAMENTO CONCLUÍDO!")
    logger.info("="*80)


if __name__ == '__main__':
    main()
