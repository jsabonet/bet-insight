"""
Estrategia Hibrida - Usa contexto SÓ quando realmente forte
Caso contrario, usa Poisson puro

Author: AI Assistant  
Date: 2026-02-11
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class HybridStrategy:
    """
    Decide quando usar contextualizacao vs modelo base.
    
    Criterios para USAR contexto:
    1. Confianca do padrao >= 90% (muito forte)
    2. Dados contextuais REAIS (nao genericos)
    3. Padrao com historico comprovado
    
    Caso contrario: usa modelo base (Poisson)
    """
    
    # Padroes com historico validado
    VALIDATED_PATTERNS = {
        # Adicionar padroes conforme validacao
        # 'balanced_tight_game': False,  # Invalidado - 47% low scoring
    }
    
    # Threshold de confianca minima
    MIN_CONFIDENCE_FOR_CONTEXT = 0.90  # 90%
    
    def __init__(self):
        """Inicializa estrategia hibrida."""
        self.decisions_log = []
    
    def should_use_context(self, 
                          context_result: Dict,
                          match_features: Dict) -> Dict:
        """
        Decide se deve usar contextualizacao ou modelo base.
        
        Args:
            context_result: Output do ContextAnalyzer
            match_features: Features do jogo (para validar se sao reais)
            
        Returns:
            Dict: {
                'use_context': bool,
                'reason': str,
                'confidence': float,
                'approved_patterns': List[str]
            }
        """
        patterns = context_result.get('patterns', [])
        
        if not patterns:
            return self._reject_context("Nenhum padrao detectado")
        
        # Verificar se tem dados contextuais REAIS
        has_real_data = self._has_real_contextual_data(match_features)
        
        if not has_real_data:
            return self._reject_context("Contexto generico - sem dados reais")
        
        # Avaliar cada padrao
        approved_patterns = []
        max_confidence = 0
        
        for pattern in patterns:
            pattern_name = pattern['name']
            confidence = pattern['confidence']
            
            max_confidence = max(max_confidence, confidence)
            
            # Verificar se padrao foi validado
            if pattern_name in self.VALIDATED_PATTERNS:
                if not self.VALIDATED_PATTERNS[pattern_name]:
                    logger.info(f"   ❌ {pattern_name}: Padrao invalidado historicamente")
                    continue
            
            # Verificar confianca minima
            if confidence < self.MIN_CONFIDENCE_FOR_CONTEXT:
                logger.info(f"   ⚠️ {pattern_name}: Confianca {confidence:.0%} < {self.MIN_CONFIDENCE_FOR_CONTEXT:.0%}")
                continue
            
            approved_patterns.append(pattern_name)
            logger.info(f"   ✅ {pattern_name}: APROVADO (confianca: {confidence:.0%})")
        
        if approved_patterns:
            decision = {
                'use_context': True,
                'reason': f"Padroes fortes detectados: {', '.join(approved_patterns)}",
                'confidence': max_confidence,
                'approved_patterns': approved_patterns
            }
            logger.info(f"\n🎯 DECISAO: USAR CONTEXTO")
            logger.info(f"   Padroes: {', '.join(approved_patterns)}")
            logger.info(f"   Confianca: {max_confidence:.0%}")
        else:
            decision = self._reject_context(
                f"Nenhum padrao forte (max confianca: {max_confidence:.0%} < {self.MIN_CONFIDENCE_FOR_CONTEXT:.0%})"
            )
        
        self.decisions_log.append(decision)
        return decision
    
    def _reject_context(self, reason: str) -> Dict:
        """Rejeita uso de contexto e retorna decisao."""
        logger.info(f"\n🔄 DECISAO: USAR MODELO BASE (Poisson)")
        logger.info(f"   Razao: {reason}")
        
        return {
            'use_context': False,
            'reason': reason,
            'confidence': 0,
            'approved_patterns': []
        }
    
    def _has_real_contextual_data(self, features: Dict) -> bool:
        """
        Verifica se tem dados contextuais REAIS (nao genericos).
        
        Dados genericos:
        - importance: 'medium'
        - motivation: {'home': 'medium', 'away': 'medium'}
        - standings: {'home_position': 10, 'away_position': 10}
        
        Dados reais tem variacoes significativas.
        """
        if not features:
            return False
        
        # Verificar importance
        importance = features.get('importance')
        if importance and importance != 'medium':
            return True
        
        # Verificar motivation
        motivation = features.get('motivation', {})
        if motivation:
            home_mot = motivation.get('home')
            away_mot = motivation.get('away')
            
            # Se alguma motivacao nao eh 'medium', tem dado real
            if (home_mot and home_mot != 'medium') or (away_mot and away_mot != 'medium'):
                return True
        
        # Verificar standings
        standings = features.get('standings', {})
        if standings:
            home_pos = standings.get('home_position')
            away_pos = standings.get('away_position')
            
            # Se posicoes diferentes de 10 (generico), tem dado real
            if (home_pos and home_pos != 10) or (away_pos and away_pos != 10):
                return True
        
        # Verificar rest_context
        rest_context = features.get('rest_context', {})
        if rest_context:
            advantage = rest_context.get('advantage')
            
            # Se vantagem nao eh 'equal', tem dado real
            if advantage and advantage != 'equal':
                return True
        
        # Verificar weather
        weather = features.get('weather')
        if weather is not None:  # None eh generico
            return True
        
        # Se chegou aqui, sao todos dados genericos
        return False
    
    def get_stats(self) -> Dict:
        """Retorna estatisticas das decisoes."""
        total = len(self.decisions_log)
        if total == 0:
            return {
                'total_decisions': 0,
                'used_context': 0,
                'used_base': 0,
                'context_percentage': 0
            }
        
        used_context = sum(1 for d in self.decisions_log if d['use_context'])
        used_base = total - used_context
        
        return {
            'total_decisions': total,
            'used_context': used_context,
            'used_base': used_base,
            'context_percentage': used_context / total * 100
        }
