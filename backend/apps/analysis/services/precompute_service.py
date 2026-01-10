"""
Fase 4: Sistema de Pré-Cálculo (Cache Warm-up)
Pré-calcula análises das top 50 partidas do dia para resposta instantânea.
"""

import logging
from datetime import datetime, timedelta
from django.core.cache import cache
from apps.matches.models import Match
from .parallel_enricher import ParallelMatchEnricher
from .feature_engineer import FeatureEngineer
from .statistical_models import ModelEnsemble
from .decision_engine import DecisionEngine
from .ai_analyzer import AIAnalyzer
import asyncio

logger = logging.getLogger(__name__)


class PreComputeService:
    """
    Serviço de pré-cálculo de análises.
    
    Estratégia:
    - Pré-calcular top 50 partidas do dia (maiores ligas)
    - Executar de madrugada (3-4 AM) ou on-demand
    - Armazenar no cache com TTL de 6 horas
    - Resultado: 95% das análises em < 500ms
    """
    
    PRIORITY_LEAGUES = [
        39,   # Premier League
        140,  # La Liga
        135,  # Serie A
        78,   # Bundesliga
        61,   # Ligue 1
        94,   # Primeira Liga (Portugal)
        88,   # Eredivisie (Holanda)
        203,  # Süper Lig (Turquia)
        71,   # Brasileirão
    ]
    
    def __init__(self):
        self.enricher = ParallelMatchEnricher()
        self.feature_engineer = FeatureEngineer()
        self.models = ModelEnsemble()
        self.decision_engine = DecisionEngine()
        self.ai_analyzer = AIAnalyzer()
    
    async def precompute_top_matches(self, max_matches=50):
        """
        Pré-calcula análises das top N partidas.
        
        Args:
            max_matches: Número máximo de partidas a pré-calcular
            
        Returns:
            dict: Estatísticas do pré-cálculo
        """
        logger.info("\n" + "="*80)
        logger.info(f"🔥 PRÉ-CÁLCULO: Top {max_matches} partidas")
        logger.info("="*80)
        
        import time
        start_time = time.time()
        
        # Buscar partidas do dia
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        matches = Match.objects.filter(
            match_date__gte=today,
            match_date__lt=tomorrow,
            api_football_id__isnull=False
        ).order_by('match_date')
        
        # Priorizar por liga
        priority_matches = []
        other_matches = []
        
        for match in matches:
            if match.league_id in self.PRIORITY_LEAGUES:
                priority_matches.append(match)
            else:
                other_matches.append(match)
        
        # Combinar: priority primeiro, depois outros até max
        selected_matches = (priority_matches + other_matches)[:max_matches]
        
        logger.info(f"📊 Encontradas {len(selected_matches)} partidas para pré-cálculo")
        logger.info(f"   Priority: {len([m for m in selected_matches if m.league_id in self.PRIORITY_LEAGUES])}")
        logger.info(f"   Others: {len([m for m in selected_matches if m.league_id not in self.PRIORITY_LEAGUES])}")
        
        # Pré-calcular em lotes paralelos (10 por vez para não sobrecarregar)
        batch_size = 10
        total_computed = 0
        total_errors = 0
        
        for i in range(0, len(selected_matches), batch_size):
            batch = selected_matches[i:i+batch_size]
            logger.info(f"\n⚡ Processando lote {i//batch_size + 1}/{(len(selected_matches)-1)//batch_size + 1}...")
            
            tasks = [
                self._precompute_single_match(match)
                for match in batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    total_errors += 1
                    logger.error(f"   ❌ Erro: {result}")
                elif result:
                    total_computed += 1
        
        elapsed = time.time() - start_time
        
        logger.info("\n" + "="*80)
        logger.info(f"✅ PRÉ-CÁLCULO CONCLUÍDO")
        logger.info(f"   Computadas: {total_computed}/{len(selected_matches)}")
        logger.info(f"   Erros: {total_errors}")
        logger.info(f"   Tempo total: {elapsed:.2f}s")
        logger.info(f"   Tempo médio: {elapsed/len(selected_matches):.2f}s/partida")
        logger.info("="*80 + "\n")
        
        return {
            'total_matches': len(selected_matches),
            'computed': total_computed,
            'errors': total_errors,
            'elapsed_seconds': elapsed,
            'avg_seconds_per_match': elapsed / len(selected_matches) if len(selected_matches) > 0 else 0
        }
    
    async def _precompute_single_match(self, match):
        """
        Pré-calcula análise de uma partida e armazena no cache.
        
        Returns:
            bool: True se sucesso, False se erro
        """
        try:
            # Cache key
            cache_key = f"precomputed_analysis:{match.api_football_id}"
            
            # Verificar se já existe
            if cache.get(cache_key):
                logger.info(f"   ⏩ {match.home_team} vs {match.away_team} - Já em cache")
                return True
            
            # Dados da partida
            match_data = {
                'api_id': match.api_football_id,
                'home_team': match.home_team,
                'away_team': match.away_team,
                'date': match.match_date,
                'league': match.league
            }
            
            # 1. Enriquecimento (paralelo)
            enriched = await self.enricher.enrich_async(match_data)
            
            # 2. Feature Engineering
            features = self.feature_engineer.engineer_all_features(enriched)
            
            # 3. Modelos Estatísticos
            predictions = self.models.predict(features, enriched)
            
            # 4. Decision Engine
            decisions = self.decision_engine.analyze(predictions, enriched)
            
            # 5. IA Explainer
            explanation = self.ai_analyzer.explain_decision(decisions, enriched)
            
            # Resultado completo
            analysis = {
                'enriched_data': enriched,
                'features': features,
                'predictions': predictions,
                'decisions': decisions,
                'explanation': explanation,
                'precomputed_at': datetime.now().isoformat(),
                'match': {
                    'home_team': match.home_team,
                    'away_team': match.away_team,
                    'date': str(match.match_date),
                    'league': match.league
                }
            }
            
            # Armazenar no cache (6 horas)
            cache.set(cache_key, analysis, 21600)
            
            logger.info(f"   ✅ {match.home_team} vs {match.away_team} - Pré-calculada")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ {match.home_team} vs {match.away_team} - Erro: {str(e)}")
            return False
    
    def get_precomputed_analysis(self, api_football_id):
        """
        Obtém análise pré-calculada do cache.
        
        Args:
            api_football_id: ID da partida na API-Football
            
        Returns:
            dict: Análise completa ou None se não existe
        """
        cache_key = f"precomputed_analysis:{api_football_id}"
        analysis = cache.get(cache_key)
        
        if analysis:
            logger.info(f"🚀 Análise pré-calculada obtida do cache (instantânea!)")
            return analysis
        
        return None
    
    def get_cache_stats(self):
        """
        Obtém estatísticas de cache.
        
        Returns:
            dict: Estatísticas de uso do cache
        """
        # Django LocMem não expõe estatísticas facilmente
        # Retornar estimativa baseada em hits conhecidos
        return {
            'backend': 'LocMemCache',
            'max_entries': 5000,
            'note': 'Use Redis para estatísticas detalhadas'
        }


# Função helper para executar pré-cálculo via management command
async def run_precompute(max_matches=50):
    """
    Executa pré-cálculo assíncrono.
    Usar em management command ou celery task.
    """
    service = PreComputeService()
    stats = await service.precompute_top_matches(max_matches)
    return stats
