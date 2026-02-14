"""
ML Predictor - Integração do modelo XGBoost treinado
"""
import os
import json
import numpy as np
import xgboost as xgb
from pathlib import Path
from calculate_real_features import TeamStatsCalculator, extract_features_from_match


class MLPredictor:
    """Preditor usando modelo XGBoost treinado"""
    
    def __init__(self, model_path=None):
        """
        Inicializa o preditor
        
        Args:
            model_path: Caminho para o modelo .json (se None, usa o mais recente)
        """
        self.model = None
        self.metadata = None
        self.feature_names = None
        self.calculator = TeamStatsCalculator()
        
        if model_path is None:
            # Encontrar modelo mais recente
            model_path = self._find_latest_model()
        
        self.load_model(model_path)
    
    def _find_latest_model(self):
        """Encontra o modelo mais recente na pasta ml_training"""
        ml_dir = Path(__file__).parent / 'ml_training'
        
        # Procurar modelos balanceados primeiro
        balanced_models = list(ml_dir.glob('xgboost_balanced_*.json'))
        if balanced_models:
            # Ordenar por data (timestamp no nome)
            latest = sorted(balanced_models, reverse=True)[0]
            return str(latest)
        
        # Se não encontrar balanceado, procurar otimizado
        optimized_models = list(ml_dir.glob('xgboost_optimized_*.json'))
        if optimized_models:
            latest = sorted(optimized_models, reverse=True)[0]
            return str(latest)
        
        # Fallback: procurar qualquer modelo XGBoost
        all_models = list(ml_dir.glob('xgboost_*.json'))
        if all_models:
            latest = sorted(all_models, reverse=True)[0]
            return str(latest)
        
        raise FileNotFoundError("Nenhum modelo XGBoost encontrado em ml_training/")
    
    def load_model(self, model_path):
        """Carrega modelo e metadados"""
        self.model = xgb.XGBClassifier()
        self.model.load_model(model_path)
        
        # Carregar metadados
        metadata_path = model_path.replace('.json', '').replace('xgboost_', 'model_metadata_')
        metadata_path = f"{metadata_path}.json"
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
                self.feature_names = self.metadata.get('feature_names', [])
        else:
            print(f"Aviso: Metadados não encontrados em {metadata_path}")
            self.feature_names = []
    
    def predict(self, match):
        """
        Faz predição para uma partida
        
        Args:
            match: Objeto Match do Django
        
        Returns:
            dict com:
                - prediction: 'Empate', 'Casa' ou 'Fora'
                - probabilities: dict com probabilidades para cada resultado
                - confidence: confiança da predição (0-1)
        """
        # Extrair features da partida
        features = extract_features_from_match(match, self.calculator)
        
        # Converter para array na ordem correta
        feature_vector = []
        for feature_name in self.feature_names:
            value = features.get(feature_name, 0)
            
            # Converter booleanos e strings para numérico
            if isinstance(value, bool):
                value = 1 if value else 0
            elif isinstance(value, str):
                value = hash(value) % 100 / 100.0
            
            feature_vector.append(float(value))
        
        X = np.array([feature_vector])
        
        # Predição
        prediction_numeric = self.model.predict(X)[0]
        probabilities_array = self.model.predict_proba(X)[0]
        
        # Mapear numérico para texto
        label_map = {0: 'Empate', 1: 'Casa', 2: 'Fora'}
        prediction = label_map[prediction_numeric]
        
        # Probabilidades por resultado
        probabilities = {
            'Empate': float(probabilities_array[0]),
            'Casa': float(probabilities_array[1]),
            'Fora': float(probabilities_array[2])
        }
        
        # Confiança = probabilidade da predição escolhida
        confidence = probabilities[prediction]
        
        return {
            'prediction': prediction,
            'probabilities': probabilities,
            'confidence': confidence,
            'features_used': len(feature_vector)
        }
    
    def get_model_info(self):
        """Retorna informações sobre o modelo carregado"""
        if self.metadata:
            return {
                'timestamp': self.metadata.get('timestamp'),
                'total_matches': self.metadata.get('total_matches'),
                'test_accuracy': self.metadata.get('test_accuracy'),
                'features_count': self.metadata.get('features_count'),
                'top_features': [f['feature'] for f in self.metadata.get('top_20_features', [])[:5]]
            }
        return {}


# Singleton global para reusar o modelo
_ml_predictor_instance = None


def get_ml_predictor():
    """
    Retorna instância singleton do MLPredictor
    Reutiliza a mesma instância para evitar carregar o modelo múltiplas vezes
    """
    global _ml_predictor_instance
    
    if _ml_predictor_instance is None:
        try:
            _ml_predictor_instance = MLPredictor()
            print(f"ML Predictor carregado: {_ml_predictor_instance.get_model_info()}")
        except Exception as e:
            print(f"Erro ao carregar ML Predictor: {e}")
            return None
    
    return _ml_predictor_instance


# Teste
if __name__ == '__main__':
    import django
    import os
    import sys
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    from apps.matches.models import Match
    
    print("="*80)
    print("TESTE: ML PREDICTOR")
    print("="*80)
    print()
    
    # Carregar preditor
    predictor = get_ml_predictor()
    
    if predictor:
        print("Modelo carregado com sucesso!")
        print(f"Info: {predictor.get_model_info()}")
        print()
        
        # Pegar uma partida de teste
        test_match = Match.objects.filter(
            status='finished',
            home_score__isnull=False,
            away_score__isnull=False
        ).select_related('home_team', 'away_team', 'league').first()
        
        if test_match:
            print(f"Partida de teste:")
            print(f"  {test_match.home_team.name} vs {test_match.away_team.name}")
            print(f"  Resultado real: {test_match.home_score}-{test_match.away_score}")
            
            if test_match.home_score > test_match.away_score:
                real_result = 'Casa'
            elif test_match.home_score < test_match.away_score:
                real_result = 'Fora'
            else:
                real_result = 'Empate'
            
            print(f"  Label real: {real_result}")
            print()
            
            # Fazer predição
            result = predictor.predict(test_match)
            
            print("Predição ML:")
            print(f"  Resultado previsto: {result['prediction']}")
            print(f"  Confiança: {result['confidence']*100:.1f}%")
            print()
            print("  Probabilidades:")
            for outcome, prob in result['probabilities'].items():
                bar = '=' * int(prob * 50)
                correct = '  <-- CORRETO' if outcome == real_result else ''
                print(f"    {outcome:10s}: {prob*100:5.1f}% {bar}{correct}")
            print()
            print(f"  Features usadas: {result['features_used']}")
            print()
            
            if result['prediction'] == real_result:
                print("  ✓ PREDIÇÃO CORRETA!")
            else:
                print(f"  ✗ Predição incorreta (previu {result['prediction']}, real foi {real_result})")
            
            print()
            print("="*80)
