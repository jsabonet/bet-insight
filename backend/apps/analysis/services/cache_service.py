"""
Cache Service - Sistema de cache inteligente para análises
Reduz recalculos desnecessários e melhora performance
"""
import logging
import hashlib
import json
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

class AnalysisCache:
    """
    Cache em memória para análises de partidas.
    
    - TTL: 5 minutos (dados estatísticos mudam pouco)
    - Key: match_id + strategy + timestamp_bucket
    - Max size: 500 entradas (LRU)
    """
    
    def __init__(self, ttl_minutes=5, max_size=500):
        self._cache = {}
        self._access_times = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, match_id, strategy, include_ai=True):
        """
        Gera chave única para cache.
        
        Formato: {match_id}:{strategy}:{include_ai}:{bucket}
        Bucket: agrupa por janelas de 5 minutos
        """
        now = datetime.now()
        bucket = now.replace(second=0, microsecond=0)
        bucket = bucket - timedelta(minutes=bucket.minute % 5)
        
        key_parts = [
            str(match_id),
            strategy,
            'with_ai' if include_ai else 'no_ai',
            bucket.isoformat()
        ]
        
        return ':'.join(key_parts)
    
    def get(self, match_id, strategy, include_ai=True):
        """
        Busca análise no cache.
        
        Returns:
            dict ou None
        """
        key = self._generate_key(match_id, strategy, include_ai)
        
        if key not in self._cache:
            self.misses += 1
            logger.info(f"🔴 Cache MISS: {key} (hits={self.hits}, misses={self.misses})")
            return None
        
        # Verificar TTL
        cached_data = self._cache[key]
        cached_time = cached_data['timestamp']
        
        if datetime.now() - cached_time > self.ttl:
            # Expirado
            logger.info(f"⏰ Cache EXPIRED: {key}")
            del self._cache[key]
            del self._access_times[key]
            self.misses += 1
            return None
        
        # Hit!
        self._access_times[key] = datetime.now()
        self.hits += 1
        hit_rate = (self.hits / (self.hits + self.misses)) * 100
        logger.info(f"✅ Cache HIT: {key} (hit_rate={hit_rate:.1f}%)")
        
        return cached_data['data']
    
    def set(self, match_id, strategy, data, include_ai=True):
        """
        Salva análise no cache.
        """
        # Evict LRU se necessário
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        key = self._generate_key(match_id, strategy, include_ai)
        
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        self._access_times[key] = datetime.now()
        
        logger.info(f"💾 Cache SET: {key} (size={len(self._cache)})")
    
    def invalidate(self, match_id):
        """
        Invalida todas as entradas de uma partida específica.
        Útil quando odds mudam ou há nova informação.
        """
        keys_to_delete = [
            k for k in self._cache.keys()
            if k.startswith(f"{match_id}:")
        ]
        
        for key in keys_to_delete:
            del self._cache[key]
            if key in self._access_times:
                del self._access_times[key]
        
        logger.info(f"🗑️ Cache INVALIDATED: match {match_id} ({len(keys_to_delete)} entries)")
    
    def _evict_lru(self):
        """Remove entrada menos recentemente usada."""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        
        del self._cache[lru_key]
        del self._access_times[lru_key]
        
        logger.info(f"🗑️ Cache EVICT LRU: {lru_key}")
    
    def clear(self):
        """Limpa todo o cache."""
        count = len(self._cache)
        self._cache.clear()
        self._access_times.clear()
        logger.info(f"🧹 Cache CLEARED: {count} entries")
    
    def stats(self):
        """Retorna estatísticas do cache."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'ttl_minutes': self.ttl.seconds // 60
        }


# Instância global
_cache = AnalysisCache()


def cached_analysis(include_ai_in_key=True):
    """
    Decorator para cachear análises automaticamente.
    
    Usage:
        @cached_analysis()
        def analyze_match(match_id, strategy, include_ai=True):
            # ... análise pesada ...
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extrair parâmetros
            match_id = kwargs.get('match_id') or (args[0] if len(args) > 0 else None)
            strategy = kwargs.get('strategy', 'value')
            include_ai = kwargs.get('include_ai', True)
            
            if not match_id:
                logger.warning("⚠️ cached_analysis: match_id não encontrado, pulando cache")
                return func(*args, **kwargs)
            
            # Tentar cache
            cached_result = _cache.get(match_id, strategy, include_ai if include_ai_in_key else True)
            
            if cached_result is not None:
                return cached_result
            
            # Cache miss: executar função
            result = func(*args, **kwargs)
            
            # Salvar no cache
            if result is not None:
                _cache.set(match_id, strategy, result, include_ai if include_ai_in_key else True)
            
            return result
        
        return wrapper
    return decorator


# Funções de acesso público
def get_cache():
    """Retorna instância do cache."""
    return _cache


def clear_cache():
    """Limpa todo o cache."""
    _cache.clear()


def get_cache_stats():
    """Retorna estatísticas do cache."""
    return _cache.stats()


def invalidate_match_cache(match_id):
    """Invalida cache de uma partida específica."""
    _cache.invalidate(match_id)
