"""
Calibrador de xG - Carrega e aplica modelo de calibração Poisson → xG Real
"""
import pickle
import logging
from pathlib import Path
import json
import numpy as np

logger = logging.getLogger(__name__)


class XGCalibrator:
    """
    Calibra previsões xG do modelo Poisson usando isotonic regression
    treinado com 1,343 partidas reais (2,686 observações)
    
    Melhoria obtida no teste:
    - MAE: -25.1% (0.686 → 0.513)
    - RMSE: -26.0% (0.896 → 0.664)
    - MAPE: -13.6% (63.2% → 54.6%)
    """
    
    _instance = None
    _model = None
    _metadata = None
    
    def __new__(cls):
        """Singleton - reutilizar modelo carregado"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa e carrega modelo se necessário"""
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Carrega modelo e metadados do disco"""
        try:
            # Model dir no backend root (não em apps/analysis)
            backend_dir = Path(__file__).parent.parent.parent.parent
            model_dir = backend_dir / 'ml_models'
            model_path = model_dir / 'xg_calibration_model.pkl'
            metadata_path = model_dir / 'xg_calibration_metadata.json'
            
            if not model_path.exists():
                logger.warning(f"⚠️  Modelo de calibração não encontrado: {model_path}")
                logger.warning("   Execute train_xg_calibration.py para treinar o modelo")
                self._model = None
                return
            
            # Carregar modelo
            with open(model_path, 'rb') as f:
                self._model = pickle.load(f)
            
            # Carregar metadados
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self._metadata = json.load(f)
            
            logger.info("✅ Calibrador xG carregado com sucesso")
            
            if self._metadata:
                logger.info(f"   Treinado em: {self._metadata.get('trained_at', 'N/A')}")
                logger.info(f"   Amostras: {self._metadata.get('n_samples_total', 'N/A')}")
                logger.info(f"   MAE teste: {self._metadata.get('metrics_test', {}).get('mae', 'N/A'):.4f}")
                logger.info(f"   Melhoria MAE: {self._metadata.get('improvement', {}).get('mae_pct', 'N/A'):.1f}%")
        
        except Exception as e:
            logger.error(f"❌ Erro ao carregar calibrador xG: {e}")
            self._model = None
    
    def is_available(self):
        """Verifica se o modelo está disponível"""
        return self._model is not None
    
    def calibrate(self, xg_raw):
        """
        Calibra um valor de xG bruto (Poisson) para xG calibrado
        
        Args:
            xg_raw (float): xG bruto do modelo Poisson
        
        Returns:
            float: xG calibrado
        """
        if not self.is_available():
            logger.debug("⚠️  Calibrador não disponível, retornando xG bruto")
            return xg_raw
        
        try:
            # Garantir que é array numpy
            xg_array = np.array([xg_raw]).reshape(-1, 1)
            
            # Aplicar calibração
            xg_calibrated = self._model.predict(xg_array.ravel())[0]
            
            # Garantir limites razoáveis
            xg_calibrated = max(0.0, min(10.0, xg_calibrated))
            
            return float(xg_calibrated)
        
        except Exception as e:
            logger.error(f"❌ Erro ao calibrar xG: {e}")
            return xg_raw
    
    def calibrate_batch(self, xg_values):
        """
        Calibra múltiplos valores de xG de uma vez
        
        Args:
            xg_values (list): Lista de valores xG brutos
        
        Returns:
            list: Lista de valores xG calibrados
        """
        if not self.is_available():
            logger.debug("⚠️  Calibrador não disponível, retornando xG brutos")
            return xg_values
        
        try:
            xg_array = np.array(xg_values)
            xg_calibrated = self._model.predict(xg_array)
            
            # Garantir limites
            xg_calibrated = np.clip(xg_calibrated, 0.0, 10.0)
            
            return xg_calibrated.tolist()
        
        except Exception as e:
            logger.error(f"❌ Erro ao calibrar múltiplos xG: {e}")
            return xg_values
    
    def get_metadata(self):
        """Retorna metadados do modelo"""
        return self._metadata
    
    def get_improvement_stats(self):
        """Retorna estatísticas de melhoria do modelo"""
        if not self._metadata:
            return None
        
        return {
            'mae_before': self._metadata.get('metrics_before', {}).get('mae'),
            'mae_after': self._metadata.get('metrics_test', {}).get('mae'),
            'mae_improvement_pct': self._metadata.get('improvement', {}).get('mae_pct'),
            'rmse_before': self._metadata.get('metrics_before', {}).get('rmse'),
            'rmse_after': self._metadata.get('metrics_test', {}).get('rmse'),
            'rmse_improvement_pct': self._metadata.get('improvement', {}).get('rmse_pct'),
            'mape_before': self._metadata.get('metrics_before', {}).get('mape'),
            'mape_after': self._metadata.get('metrics_test', {}).get('mape'),
            'mape_improvement_pct': self._metadata.get('improvement', {}).get('mape_pct'),
            'n_samples': self._metadata.get('n_samples_total'),
            'trained_at': self._metadata.get('trained_at')
        }


# Instância global (singleton)
_calibrator = None

def get_xg_calibrator():
    """Retorna instância singleton do calibrador"""
    global _calibrator
    if _calibrator is None:
        _calibrator = XGCalibrator()
    return _calibrator
