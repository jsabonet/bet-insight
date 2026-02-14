"""
Gerador de Bilhetes Diários e Value Bets Automáticos

Este service analisa todas as partidas do dia e gera:
1. Bilhetes múltiplos (3x, 5x, 7x) com alta probabilidade
2. Value bets individuais com EV positivo

Integração com HybridAnalysisOrchestrator existente.
"""

import logging
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from apps.matches.models import Match
from apps.analysis.models import DailyBet
from .analysis_orchestrator import HybridAnalysisOrchestrator

logger = logging.getLogger(__name__)


class DailyBetGenerator:
    """Gera bilhetes múltiplos e value bets diários automaticamente"""
    
    # Configurações de filtros
    MIN_VALUE_EV = 5.0  # EV mínimo para value bets (+5%)
    MIN_VALUE_PROBABILITY = 0.25  # Probabilidade mínima para value bets (25%)
    
    MIN_MULTIPLE_PROBABILITY = 0.50  # Probabilidade mínima para cada aposta de bilhete (50%)
    MIN_COMBINED_PROBABILITY_3X = 0.15  # Prob. combinada mínima para bilhete 3x (15%)
    MIN_COMBINED_PROBABILITY_5X = 0.08  # Prob. combinada mínima para bilhete 5x (8%)
    MIN_COMBINED_PROBABILITY_7X = 0.04  # Prob. combinada mínima para bilhete 7x (4%)
    
    MIN_TICKET_ODD = 2.0  # Odd mínima para bilhetes
    MAX_TICKET_ODD = 20.0  # Odd máxima para bilhetes (evitar super apostas)
    
    MAX_VALUE_BETS = 10  # Máximo de value bets por dia
    
    def __init__(self):
        self.orchestrator = HybridAnalysisOrchestrator()
        self.api_calls = 0
        self.cache_hits = 0
    
    def generate_for_today(self):
        """
        Gera apostas para partidas do dia
        
        Returns:
            dict: Estatísticas da geração
        """
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        logger.info("=" * 100)
        logger.info(f"🎯 GERAÇÃO DE BILHETES DIÁRIOS - {today.strftime('%d/%m/%Y')}")
        logger.info("=" * 100)
        
        # Buscar partidas do dia (próximas 24h)
        matches = Match.objects.filter(
            match_date__gte=timezone.now(),
            match_date__lt=timezone.now() + timedelta(days=1),
            status__in=['not_started', 'scheduled', 'NS', 'TBD'],
            api_football_id__isnull=False
        ).select_related('league', 'home_team', 'away_team').order_by('match_date')
        
        logger.info(f"\n📅 Partidas encontradas para análise: {matches.count()}")
        
        if matches.count() == 0:
            logger.warning("⚠️  Nenhuma partida encontrada para hoje")
            return {
                'matches_analyzed': 0,
                'multiple_count': 0,
                'value_count': 0,
                'api_calls': 0,
                'cache_hits': 0
            }
        
        # Analisar todas partidas
        analyses = []
        
        for idx, match in enumerate(matches, 1):
            try:
                logger.info(f"\n{'─' * 80}")
                logger.info(f"[{idx}/{matches.count()}] Analisando: {match.home_team.name} vs {match.away_team.name}")
                logger.info(f"    Liga: {match.league.name if match.league else 'N/A'}")
                logger.info(f"    Data: {match.match_date.strftime('%d/%m/%Y %H:%M')}")
                
                # Análise com estratégia VALUE (para value bets)
                logger.info("    🔍 Executando análise VALUE...")
                result_value = self.orchestrator.run(match, strategy='value')
                
                # Análise com estratégia MULTIPLE (para bilhetes)
                logger.info("    🔍 Executando análise MULTIPLE...")
                result_multiple = self.orchestrator.run(match, strategy='multiple')
                
                analyses.append({
                    'match': match,
                    'value_result': result_value,
                    'multiple_result': result_multiple
                })
                
                # Estimar requisições (2 análises, mas cache reduz muito)
                self.api_calls += 2
                
                logger.info(f"    ✅ Análise concluída")
                
            except Exception as e:
                logger.error(f"    ❌ Erro ao analisar {match}: {e}", exc_info=True)
                continue
        
        logger.info(f"\n{'=' * 100}")
        logger.info(f"✅ {len(analyses)} partidas analisadas com sucesso")
        logger.info(f"{'=' * 100}\n")
        
        # Gerar bilhetes e value bets
        with transaction.atomic():
            # Deletar apostas antigas do mesmo dia (se regenerar)
            DailyBet.objects.filter(date=today).delete()
            
            # Gerar bilhetes múltiplos
            multiple_bets = self._generate_multiple_tickets(analyses, today)
            
            # Gerar value bets individuais
            value_bets = self._generate_value_bets(analyses, today)
        
        logger.info(f"\n{'=' * 100}")
        logger.info(f"🎉 GERAÇÃO CONCLUÍDA")
        logger.info(f"{'=' * 100}")
        logger.info(f"📋 Bilhetes múltiplos criados: {len(multiple_bets)}")
        logger.info(f"⚡ Value bets criadas: {len(value_bets)}")
        logger.info(f"⚽ Partidas analisadas: {len(analyses)}")
        logger.info(f"🔌 Requisições API (estimado): {self.api_calls}")
        logger.info(f"{'=' * 100}\n")
        
        return {
            'matches_analyzed': len(analyses),
            'multiple_count': len(multiple_bets),
            'value_count': len(value_bets),
            'api_calls': self.api_calls,
            'cache_hits': self.cache_hits
        }
    
    def _generate_multiple_tickets(self, analyses, date):
        """
        Gera bilhetes múltiplos com as melhores apostas (alta probabilidade)
        
        Estratégia:
        - Selecionar top apostas com maior probabilidade de cada partida
        - Criar bilhetes de 3, 5 e 7 apostas
        - Filtrar por probabilidade combinada mínima
        - Odd total entre MIN_TICKET_ODD e MAX_TICKET_ODD
        """
        logger.info(f"\n{'─' * 80}")
        logger.info("📋 GERANDO BILHETES MÚLTIPLOS")
        logger.info(f"{'─' * 80}")
        
        # Extrair todas as top_bets de MULTIPLE
        all_bets = []
        
        for analysis in analyses:
            match = analysis['match']
            result = analysis['multiple_result']
            analysis_data = result.get('analysis_data', {})
            top_bets = analysis_data.get('top_bets', [])
            consensus = analysis_data.get('consensus', {})

            # CORREÇÃO (14/02/2026): Usar ranking_score diretamente do DecisionEngine
            # top_bets já vem ordenado por ranking_score = selection_score × ev × conf × risk
            # Não precisamos recalcular (evita multiplicação prob^2.5)
            if top_bets:
                # Filtrar por critérios de bilhete:
                # 1. Probabilidade >= 50%
                # 2. Odd na faixa ideal (1.30 - 2.10)
                # 3. EV não muito negativo (>= -10%)
                best_bet = None
                for bet in top_bets:
                    prob = bet.get('probability', 0)
                    odd = bet.get('market_odd', 0)
                    ev_pct = bet.get('ev_pct', 0)
                    
                    # Filtros conservadores para bilhetes múltiplos
                    if prob >= self.MIN_MULTIPLE_PROBABILITY and 1.30 <= odd <= 2.10 and ev_pct >= -10:
                        best_bet = bet
                        break
                
                if not best_bet:
                    logger.debug(f"   ⏩ Pulando {match}: nenhuma aposta atende critérios de bilhete")
                    continue

                # Já passou pelo filtro acima, mas manter check de probabilidade
                if best_bet['probability'] < self.MIN_MULTIPLE_PROBABILITY:
                    logger.debug(f"   ⏩ Pulando {match}: prob {best_bet['probability']*100:.1f}% < {self.MIN_MULTIPLE_PROBABILITY*100:.0f}%")
                    continue

                logger.info(f"   🎯 Seleção Bilhete: {best_bet['market']} ({best_bet['pick']}) - {best_bet['probability']*100:.0f}% @ {best_bet['market_odd']:.2f}")
                if 'post_reason' in best_bet:
                    logger.info(f"      Razão: {best_bet['post_reason']}")

                all_bets.append({
                    'match_id': match.id,
                    'match': f"{match.home_team.name} vs {match.away_team.name}",
                    'league': match.league.name if match.league else 'N/A',
                    'date': match.match_date.isoformat(),
                    'market': best_bet['market'],
                    'pick': best_bet['pick'],
                    'probability': best_bet['probability'],
                    'odd': best_bet['market_odd'],
                    'fair_odd': best_bet.get('fair_odd'),
                    'ev_pct': best_bet.get('ev_pct', 0),
                    'score': best_bet.get('post_score', best_bet['score']),
                    'result': None  # Será preenchido após validação
                })
        
        logger.info(f"   📊 {len(all_bets)} apostas elegíveis para bilhetes")
        
        # Ordenar por probabilidade (mais seguro para bilhetes)
        all_bets.sort(key=lambda x: x['probability'], reverse=True)
        
        # Criar bilhetes de 3, 5 e 7 apostas
        tickets = []
        
        for size in [3, 5, 7]:
            if len(all_bets) < size:
                logger.info(f"   ⚠️  Apostas insuficientes para bilhete {size}x ({len(all_bets)} disponíveis)")
                continue
            
            # Pegar top N apostas
            selections = all_bets[:size]
            
            # Calcular odd total e probabilidade combinada
            total_odd = 1.0
            combined_prob = 1.0
            
            for sel in selections:
                total_odd *= sel['odd']
                combined_prob *= sel['probability']
            
            # Determinar probabilidade mínima baseado no tamanho
            if size == 3:
                min_prob = self.MIN_COMBINED_PROBABILITY_3X
            elif size == 5:
                min_prob = self.MIN_COMBINED_PROBABILITY_5X
            else:
                min_prob = self.MIN_COMBINED_PROBABILITY_7X
            
            # Filtro: probabilidade combinada
            if combined_prob < min_prob:
                logger.info(f"   ⏩ Bilhete {size}x: prob combinada {combined_prob*100:.2f}% < {min_prob*100:.0f}%")
                continue
            
            # Filtro: odd total
            if total_odd < self.MIN_TICKET_ODD:
                logger.info(f"   ⏩ Bilhete {size}x: odd {total_odd:.2f} < {self.MIN_TICKET_ODD}")
                continue
            
            if total_odd > self.MAX_TICKET_ODD:
                logger.info(f"   ⏩ Bilhete {size}x: odd {total_odd:.2f} > {self.MAX_TICKET_ODD}")
                continue
            
            # Calcular fair odd e EV do bilhete
            fair_odd = 1.0 / combined_prob if combined_prob > 0 else 0
            ev_pct = ((fair_odd / total_odd) - 1) * 100 if total_odd > 0 else 0
            
            # Criar bilhete
            bet = DailyBet.objects.create(
                date=date,
                bet_type='multiple',
                selections=selections,
                total_odd=Decimal(str(round(total_odd, 2))),
                fair_odd=Decimal(str(round(fair_odd, 2))),
                combined_probability=combined_prob,
                expected_value=ev_pct,
                suggested_stake=self._calculate_stake(combined_prob, 'multiple')
            )
            
            tickets.append(bet)
            
            logger.info(f"\n   ✅ Bilhete {size}x criado:")
            logger.info(f"      Odd: {total_odd:.2f} | Prob: {combined_prob*100:.1f}% | EV: {ev_pct:+.1f}%")
            logger.info(f"      Stake sugerido: {bet.suggested_stake:.1f}u")
            logger.info(f"      Apostas:")
            for sel in selections[:3]:  # Mostrar primeiras 3
                logger.info(f"         • {sel['pick']} ({sel['market']}) - {sel['probability']*100:.0f}% @ {sel['odd']:.2f}")
            if size > 3:
                logger.info(f"         ... (+{size-3} apostas)")
        
        logger.info(f"\n   📋 Total de bilhetes criados: {len(tickets)}")
        
        return tickets
    
    def _generate_value_bets(self, analyses, date):
        """
        Gera value bets individuais (maior EV)
        
        Estratégia:
        - Selecionar apostas com EV positivo >= MIN_VALUE_EV
        - Probabilidade mínima >= MIN_VALUE_PROBABILITY
        - Ordenar por EV (maior value primeiro)
        - Limitar a MAX_VALUE_BETS por dia
        """
        logger.info(f"\n{'─' * 80}")
        logger.info("⚡ GERANDO VALUE BETS")
        logger.info(f"{'─' * 80}")
        
        all_value_bets = []
        
        for analysis in analyses:
            match = analysis['match']
            result = analysis['value_result']
            top_bets = result.get('analysis_data', {}).get('top_bets', [])
            
            for bet in top_bets:
                ev_pct = bet.get('ev_pct', 0)
                prob = bet['probability']
                
                # Filtros
                if ev_pct < self.MIN_VALUE_EV:
                    continue
                
                if prob < self.MIN_VALUE_PROBABILITY:
                    continue
                
                all_value_bets.append({
                    'match_id': match.id,
                    'match': f"{match.home_team.name} vs {match.away_team.name}",
                    'league': match.league.name if match.league else 'N/A',
                    'date': match.match_date.isoformat(),
                    'market': bet['market'],
                    'pick': bet['pick'],
                    'probability': prob,
                    'odd': bet['market_odd'],
                    'fair_odd': bet.get('fair_odd'),
                    'ev_pct': ev_pct,
                    'score': bet['score'],
                    'result': None
                })
        
        logger.info(f"   📊 {len(all_value_bets)} value bets encontradas")
        
        # Ordenar por EV (maior value primeiro)
        all_value_bets.sort(key=lambda x: x['ev_pct'], reverse=True)
        
        # Pegar top MAX_VALUE_BETS
        top_values = all_value_bets[:self.MAX_VALUE_BETS]
        
        logger.info(f"   🎯 Selecionando top {len(top_values)} value bets")
        
        created_bets = []
        
        for idx, vb in enumerate(top_values, 1):
            # Calcular fair odd
            fair_odd = vb.get('fair_odd') or (1.0 / vb['probability'] if vb['probability'] > 0 else 0)
            
            bet = DailyBet.objects.create(
                date=date,
                bet_type='value',
                selections=[vb],  # Aposta única
                total_odd=Decimal(str(round(vb['odd'], 2))),
                fair_odd=Decimal(str(round(fair_odd, 2))),
                combined_probability=vb['probability'],
                expected_value=vb['ev_pct'],
                suggested_stake=self._calculate_stake(vb['probability'], 'value', vb['ev_pct'])
            )
            
            created_bets.append(bet)
            
            logger.info(f"\n   ✅ Value Bet #{idx}:")
            logger.info(f"      {vb['match']}")
            logger.info(f"      Aposta: {vb['pick']} ({vb['market']})")
            logger.info(f"      Odd: {vb['odd']:.2f} | Fair: {fair_odd:.2f} | Prob: {vb['probability']*100:.0f}%")
            logger.info(f"      EV: +{vb['ev_pct']:.1f}% | Stake: {bet.suggested_stake:.1f}u")
        
        logger.info(f"\n   ⚡ Total de value bets criadas: {len(created_bets)}")
        
        return created_bets
    
    def _calculate_stake(self, probability, bet_type, ev_pct=0):
        """
        Calcula stake sugerido usando Kelly Criterion simplificado
        
        Args:
            probability: Probabilidade da aposta (0-1)
            bet_type: 'multiple' ou 'value'
            ev_pct: Expected Value em % (apenas para value bets)
        
        Returns:
            float: Stake em unidades (0.5 - 3.0)
        """
        if bet_type == 'multiple':
            # Bilhetes: stake conservador baseado em probabilidade combinada
            if probability >= 0.30:
                return 2.0  # Alta confiança
            elif probability >= 0.20:
                return 1.5  # Média confiança
            elif probability >= 0.15:
                return 1.0  # Baixa confiança
            else:
                return 0.5  # Muito baixa confiança
        else:
            # Value bets: stake baseado em EV (Kelly fracionário 1/4)
            if ev_pct >= 20:
                return 3.0  # EV muito alto
            elif ev_pct >= 15:
                return 2.5  # EV alto
            elif ev_pct >= 10:
                return 2.0  # EV médio-alto
            elif ev_pct >= 5:
                return 1.5  # EV médio
            else:
                return 1.0  # EV baixo
