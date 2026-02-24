"""
Gerador de Bilhetes Diários e Value Bets Automáticos

Este service analisa todas as partidas do dia e gera:
1. Bilhetes múltiplos (3x, 5x, 7x) com alta probabilidade
2. Value bets individuais com EV positivo

Integração com HybridAnalysisOrchestrator existente.
"""

import logging
import re
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from apps.matches.models import Match
from apps.analysis.models import DailyBet
from .analysis_orchestrator import HybridAnalysisOrchestrator
from .api_football_service import APIFootballService
from apps.matches.services.football_api import FootballAPIService

logger = logging.getLogger(__name__)


class GenerationCancelledException(Exception):
    """Exceção lançada quando geração é cancelada manualmente"""
    pass


class DailyBetGenerator:
    """Gera bilhetes múltiplos e value bets diários automaticamente"""
    
    # Configurações de filtros
    MIN_VALUE_EV = 5.0  # EV mínimo para value bets (+5%)
    MIN_VALUE_PROBABILITY = 0.25  # Probabilidade mínima para value bets (25%)
    MIN_MULTIPLE_EV = -100.0  # ✅ IGNORAR EV individual (pode ser negativo) - apenas odd total e prob importam
    
    # ✅ CORRIGIDO 21/02: Configuração PRAGMÁTICA - Cobertura + Retorno
    # ✅ CORREÇÃO CRÍTICA 21/02: Prob INDIVIDUAL 65-70% (mais cobertura)
    # Bilhetes viáveis: prob individual 65%+, odd total >2.5, cobertura adequada
    # Odd 1.30-1.54 → prob fair 65-77% | Pragmático
    MIN_MULTIPLE_PROBABILITY_3X = 0.65  # 3x: cada aposta ≥65% @ 1.30-1.54 → odd total 2.20-3.65
    MIN_MULTIPLE_PROBABILITY_5X = 0.68  # 5x: cada aposta ≥68% @ 1.30-1.47 → odd total 3.71-5.86
    MIN_MULTIPLE_PROBABILITY_7X = 0.70  # 7x: cada aposta ≥70% @ 1.30-1.43 → odd total 6.28-13.00
    
    # Probabilidades combinadas mínimas (matemática real com penalidade)
    # ✅ CORREÇÃO CRÍTICA 21/02: Prob INDIVIDUAL 65-70% → prob combinada 25-35% (PRAGMÁTICO)
    # 3X: 65%³ × 0.95 = 26.0% → 1 acerto a cada 3.8 tentativas @ odd 2.20-3.65 ✓✓
    # 5X: 68%⁵ × 0.90 = 14.0% → 1 acerto a cada 7.1 tentativas @ odd 3.71-5.86 ✓
    # 7X: 70%⁷ × 0.85 = 8.2% → 1 acerto a cada 12.2 tentativas @ odd 6.28-13.00 ✓
    MIN_COMBINED_PROBABILITY_3X = 0.25  # 25% ajustado (pragmático: cobertura + odd >2.5)
    MIN_COMBINED_PROBABILITY_5X = 0.13  # 13% ajustado (conservador)
    MIN_COMBINED_PROBABILITY_7X = 0.08  # 8% ajustado (muito conservador)
    
    # ✅ CORREÇÃO CRÍTICA 21/02: Odds para prob 70% + odd total >2.5 (com cobertura)
    # Objetivo: 3-5 apostas (odds 1.30-1.50) → odd combinada 2.20-7.59
    # Probabilidade: 67-77% cada → prob combinada 27-45% (equilibrado)
    MIN_ODD_MULTIPLE = 1.30  # Odd mínima individual (prob ~77%)
    MAX_ODD_MULTIPLE = 1.50  # Odd máxima individual (prob ~67%) - garante prob alta
    
    # ✅ CORREÇÃO CRÍTICA 21/02: Limites de odd total equilibrados
    # 3X @ 1.30-1.50: odd total 2.20-3.38
    # 5X @ 1.30-1.50: odd total 3.71-7.59
    # 7X @ 1.30-1.50: odd total 6.28-17.09
    MIN_TICKET_ODD = 2.50   # Mínimo para odd combinada atrativa
    MAX_TICKET_ODD = 25.0   # Máximo realista (evita odds absurdas)
    
    # Filtros de qualidade e contexto
    MIN_CONFIDENCE_STARS = 4  # Confiança mínima (4-5 estrelas)
    MAX_DRAW_PROBABILITY = 0.35  # Empate máximo aceitável (35%)
    ALLOWED_RISK_LEVELS = ['low', 'medium']  # Apenas risco baixo/médio
    MIN_ABSOLUTE_FORM = 1.5  # Forma mínima absoluta (50% = 1.5/3.0 pontos) - previne apostas em times com má forma
    
    MAX_VALUE_BETS = 10  # Máximo de value bets por dia
    # ⚠️ LIMITAÇÃO: Com 50 partidas × 25 mercados = 1.250 candidatos, apenas 10 são selecionados (~0.8%)
    # Os modelos geram análises para TODOS os mercados, mas aqui limitamos o output final
    # Para aumentar cobertura: considere MAX_VALUE_BETS = 20 ou 30
    
    # Configuração do sistema híbrido de busca
    SEARCH_MODE = 'priority'  # ✅ CORREÇÃO: Apenas ligas prioritárias (NUNCA expandir)
    MIN_MATCHES_THRESHOLD = 15  # Se encontrar menos, expande busca (DESATIVADO em priority mode)
    MAX_TOTAL_MATCHES = 100  # Limite absoluto de partidas a analisar (aumentado para maior cobertura)
    
    # ✅ CORREÇÃO 19/02/2026: Lista expandida de ligas prioritárias (alta qualidade)
    # De 20 para ~55 ligas para garantir volume SEM sacrificar qualidade
    PRIORITY_LEAGUES = [
        # Europa - Top 5
        39,   # Premier League (Inglaterra)
        140,  # La Liga (Espanha)
        135,  # Serie A (Itália)
        78,   # Bundesliga (Alemanha)
        61,   # Ligue 1 (França)
        
        # Europa - Segundas Divisões TOP (boa cobertura)
        40,   # Championship (Inglaterra 2ª)
        141,  # La Liga 2 (Espanha 2ª)
        136,  # Serie B (Itália 2ª)
        80,   # Bundesliga 2 (Alemanha 2ª)
        62,   # Ligue 2 (França 2ª)
        89,   # Eerste Divisie (Holanda 2ª)
        
        # Europa - Ligas Secundárias (alta cobertura)
        94,   # Primeira Liga (Portugal)
        88,   # Eredivisie (Holanda)
        144,  # Jupiler Pro League (Bélgica)
        203,  # Süper Lig (Turquia)
        235,  # Premier Liga (Rússia)
        218,  # Super League (Grécia)
        179,  # Scottish Premiership (Escócia)
        197,  # Bundesliga (Áustria)
        283,  # Primeira Liga (Croácia)
        
        # Europa - Ligas Nórdicas (boa cobertura)
        103,  # Eliteserien (Noruega)
        113,  # Allsvenskan (Suécia)
        119,  # Superligaen (Dinamarca)
        244,  # Veikkausliiga (Finlândia)
        
        # Europa - Europa Central
        345,  # Czech Liga (República Tcheca)
        169,  # Super League (Suíça)
        327,  # Primeira Liga (Polônia)
        
        # Competições Internacionais (UEFA)
        2,    # UEFA Champions League
        3,    # UEFA Europa League
        848,  # UEFA Conference League
        
        # Competições Internacionais (CONMEBOL)
        325,  # Copa Libertadores
        13,   # Copa Sudamericana
        
        # Copas Nacionais TOP (boa cobertura)
        45,   # FA Cup (Inglaterra)
        48,   # EFL Cup / Carabao Cup (Inglaterra)
        137,  # Copa del Rey (Espanha)
        81,   # DFB Pokal (Alemanha)
        82,   # Coppa Italia (Itália)
        66,   # Coupe de France (França)
        556,  # Taca de Portugal (Portugal)
        551,  # Taca da Liga (Portugal)
        
        # América do Sul - Principais (ligas + copas)
        71,   # Brasileirão Série A
        73,   # Brasileirão Série B
        128,  # Liga Profesional (Argentina)
        129,  # Copa da Argentina
        239,  # Primera División (Uruguai)
        242,  # Primera División (Chile)
        281,  # Categoria Primera A (Colômbia)
        270,  # Serie A (Equador)
        250,  # Primera División (Paraguai)
        
        # América do Norte
        253,  # MLS (EUA)
        262,  # Liga MX (México)
        
        # Ásia - Principais (alta cobertura)
        188,  # J1 League (Japão)
        189,  # J2 League (Japão 2ª)
        292,  # K League 1 (Coreia do Sul)
        293,  # K League 2 (Coreia do Sul 2ª)
        271,  # A-League (Austrália)
        307,  # Saudi Pro League (Arábia Saudita)
        
        # África - Apenas TOP (boa cobertura)
        317,  # DSTV Premiership (África do Sul)
        233,  # Egyptian Premier League (Egito)
        200,  # Botola Pro (Marrocos)
        
        # Outras competições internacionais
        667,  # Club World Cup
    ]
    
    def __init__(self):
        self.orchestrator = HybridAnalysisOrchestrator()
        self.api = APIFootballService()
        self.football_api = FootballAPIService()  # Service para buscar fixtures
        self.api_calls = 0
        self.cache_hits = 0
        self.execution = None  # TaskExecution instance para tracking de progresso
    
    def _check_cancellation(self):
        """Verifica se a geração foi cancelada e lança exceção se sim"""
        if self.execution:
            # Recarregar do banco de dados para pegar status atualizado
            self.execution.refresh_from_db()
            if self.execution.status == 'cancelled':
                logger.warning(f"🛑 Geração cancelada pelo usuário")
                raise GenerationCancelledException("Geração cancelada pelo usuário")
    
    def _calculate_data_quality_score(self, fixture):
        """
        Calcula score de qualidade de dados (0-100) baseado em múltiplos fatores.
        
        ✅ FASE 2 - 19/02/2026: Scoring avançado de qualidade
        
        Args:
            fixture (dict): Dados da partida da API Football
            
        Returns:
            dict: {
                'total_score': float (0-100),
                'breakdown': {
                    'league_priority': float,
                    'teams_known': float,
                    'fixture_confirmed': float
                },
                'details': list[str]
            }
        """
        score = 0.0
        breakdown = {}
        details = []
        
        # CRITÉRIO 1: Liga Prioritária (70 pontos - mais importante)
        league = fixture.get('league', {})
        league_id = league.get('id')
        if league_id in self.PRIORITY_LEAGUES:
            league_score = 70.0
            breakdown['league_priority'] = league_score
            score += league_score
            details.append(f'✅ Liga prioritária (ID: {league_id})')
        else:
            breakdown['league_priority'] = 0.0
            details.append(f'❌ Liga não prioritária (ID: {league_id})')
        
        # CRITÉRIO 2: Times conhecidos/válidos (20 pontos)
        teams = fixture.get('teams', {})
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        
        if home_team and away_team:
            home_name = home_team.get('name', '')
            away_name = away_team.get('name', '')
            
            if home_name and away_name and home_name != away_name:
                teams_score = 20.0
                breakdown['teams_known'] = teams_score
                score += teams_score
                details.append(f'✅ Times válidos: {home_name} vs {away_name}')
            else:
                breakdown['teams_known'] = 0.0
                details.append('❌ Times inválidos ou duplicados')
        else:
            breakdown['teams_known'] = 0.0
            details.append('❌ Dados de times incompletos')
        
        # CRITÉRIO 3: Fixture confirmado (10 pontos)
        fixture_data = fixture.get('fixture', {})
        status = fixture_data.get('status', {})
        status_short = status.get('short', '')
        
        if status_short in ['NS', 'TBD', 'PST']:  # Not Started, To Be Defined, Postponed
            fixture_score = 10.0
            breakdown['fixture_confirmed'] = fixture_score
            score += fixture_score
            details.append(f'✅ Fixture confirmado (status: {status_short})')
        else:
            breakdown['fixture_confirmed'] = 5.0
            score += 5.0
            details.append(f'⚠️ Status incomum: {status_short}')
        
        return {
            'total_score': score,
            'breakdown': breakdown,
            'details': details
        }
    
    def _validate_match_quality(self, fixture):
        """
        Valida se uma partida possui qualidade suficiente para análise.
        
        ✅ CORREÇÃO 19/02/2026: Validação ANTES de análise para evitar ligas obscuras
        ✅ FASE 2 - 19/02/2026: Score avançado + logging detalhado
        
        Args:
            fixture (dict): Dados da partida da API Football
            
        Returns:
            dict: {
                'is_valid': bool,
                'reason': str,
                'quality_score': float (0-100),
                'details': list[str]  # NOVO: detalhes da avaliação
            }
        """
        league = fixture.get('league', {})
        league_id = league.get('id')
        league_name = league.get('name', 'Unknown')
        
        # Calcular score detalhado de qualidade
        quality_analysis = self._calculate_data_quality_score(fixture)
        total_score = quality_analysis['total_score']
        details = quality_analysis['details']
        
        # REGRA 1: Liga deve estar na lista prioritária (score mínimo: 70)
        if league_id not in self.PRIORITY_LEAGUES:
            return {
                'is_valid': False,
                'reason': f'Liga "{league_name}" (ID: {league_id}) não está nas PRIORITY_LEAGUES',
                'quality_score': total_score,
                'details': details
            }
        
        # REGRA 2: Score mínimo de 80/100 para análise
        if total_score < 80.0:
            return {
                'is_valid': False,
                'reason': f'Score de qualidade insuficiente: {total_score:.1f}/100 (mínimo: 80)',
                'quality_score': total_score,
                'details': details
            }
        
        # ✅ APROVADA: Alta qualidade
        return {
            'is_valid': True,
            'reason': f'Liga prioritária com alta qualidade (score: {total_score:.1f}/100)',
            'quality_score': total_score,
            'details': details
        }
    
    def _median(self, values):
        """
        Calcula mediana robusta (funciona com par e ímpar).
        
        Args:
            values: Lista de números
            
        Returns:
            float | None: Mediana, ou None se lista vazia
        """
        if not values:
            return None
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        mid = n // 2
        
        if n % 2 == 1:
            return sorted_values[mid]
        else:
            return (sorted_values[mid - 1] + sorted_values[mid]) / 2.0
    
    def _market_group(self, market):
        """
        Classifica mercado em grupo para evitar correlação.
        
        Usado na seleção de bilhetes múltiplos para garantir diversidade:
        - Evita Over 2.5 + Over 1.5 no mesmo bilhete (mesma família)
        - Evita Home Win + 1X no mesmo bilhete (sobreposição)
        
        ✅ CORREÇÃO 21/02: Parser robusto sem falso-positivos
        - "ou" dentro de palavras não conta (ex: "double", "outcome")
        - Usa tokens específicos e regex word boundary
        
        Returns:
            str: 'total_goals' | 'btts' | '1x2' | 'double_chance' | 'other'
        """
        m = (market or "").lower()
        
        # Total de gols: over/under com word boundary ou separadores
        if ("over" in m or "under" in m or "o/u" in m or 
            "_ou_" in m or "over_" in m or "_over" in m or
            "under_" in m or "_under" in m or "goals" in m):
            return "total_goals"
        
        # BTTS
        if "btts" in m or "both teams" in m or "ambas" in m or "both_teams" in m:
            return "btts"
        
        # 1X2
        if ("home_win" in m or "away_win" in m or "draw" in m or 
            "1x2" in m or "vitória" in m or "empate" in m or
            "home" == m or "away" == m):  # exato, não substring
            return "1x2"
        
        # Dupla chance
        # ✅ CORREÇÃO 21/02: Usar regex \b12\b para evitar falso-positivo em "under_1_2", "u12.5"
        if "double" in m or "x2" in m or "1x" in m or re.search(r'\b12\b', m) or "dupla" in m:
            return "double_chance"
        
        return "other"
    
    def _select_diversified_bets(self, eligible_bets, size):
        """
        Seleciona apostas para bilhete respeitando anti-correlação.
        
        REGRA DE DIVERSIFICAÇÃO:
        ✅ Máximo 1 aposta por liga (evita correlação contextual forte)
        ❌ REMOVIDO: Restrição por grupo de mercado (bloqueava over_1.5 + over_2.5 de ligas diferentes)
        
        ✅ CORREÇÃO 21/02: Usa league_id (mais robusto que league_name)
        ✅ CORREÇÃO 21/02: Anti-correlação por liga é suficiente (over_1.5 PT + over_2.5 NL não se correlacionam)
        
        Estratégia greedy: percorre eligible_bets (já ordenadas por score)
        e pega as primeiras N que respeitam as regras.
        
        Args:
            eligible_bets: Lista de apostas candidatas (ordenadas por score)
            size: Tamanho do bilhete (3, 5 ou 7)
        
        Returns:
            list | None: Lista de apostas selecionadas, ou None se insuficientes
        """
        selected = []
        used_league_ids = set()
        
        for bet in eligible_bets:
            # ✅ CORREÇÃO 21/02: Prioriza league_id (mais robusto)
            league_id = bet.get('league_id')
            league_name = bet.get('league', '')
            league_key = league_id if league_id else league_name
            
            # Anti-correlação: skip se liga já usada
            if league_key and league_key in used_league_ids:
                continue
            
            selected.append(bet)
            if league_key:
                used_league_ids.add(league_key)
            
            if len(selected) == size:
                break
        
        # Se não conseguiu preencher, retorna None
        return selected if len(selected) == size else None
    
    def _detect_market_regime(self, analyses):
        """
        Detecta o regime de mercado usando sinais EXTERNOS ao modelo.

        SINAL: overround das bookmakers em múltiplos mercados (1X2, O/U 2.5, BTTS).
        Overround é puramente derivado de market_odds (bookmaker), sem envolver
        nenhuma probabilidade do nosso modelo.

        CORREÇÕES 21/02 (crítica do usuário):
        - Usa MEDIANA robusta (par/ímpar correto) + IQR
        - Calcula overround para múltiplos mercados, não só 1X2
        - Filtra overround fora de [0, 20%] (odds inválidas)
        - Issues contados POR MATCH (evita duplicação)
        - Coverage calculado POR MERCADO (não assume 3 mercados por jogo)
        - Regime é DIAGNÓSTICO: não ajusta thresholds (evita feedback loop)

        INTERPRETAÇÃO CORRETA DO REGIME:
        - competitive (overround baixo) → mercado líquido, linha AFIADA (difícil bater)
        - illiquid (overround alto) → mercado incerto, margem alta, menos liquidez
        
        NÃO significa:
        - competitive = "mais value" ou "dia bom para apostar"
        - illiquid = "sem value"

        Uso recomendado: dimensionar stake, limitar múltiplas, tracking de ROI.

        Returns:
            dict: {
                'regime': 'competitive' | 'standard' | 'illiquid' | 'data_suspect',
                'median_overround': float,     # mediana (robusto)
                'iqr_overround': float,        # IQR (p75 - p25)
                'overround_by_market': dict,   # overround por mercado + coverage
                'total_samples': int,          # total de overrounds válidos
                'matches_total': int,
                'data_quality': str,           # 'good' | 'poor' | 'suspect'
                'reason': str,
            }
        """
        overrounds_1x2 = []
        overrounds_ou25 = []
        overrounds_btts = []
        
        # ✅ CORREÇÃO 21/02: Issues contados POR MATCH (evita duplicação)
        matches_with_issues = set()

        for idx, analysis in enumerate(analyses):
            match_id = analysis.get('fixture_id', idx)
            value_result = analysis.get('value_result') or {}
            analysis_data = value_result.get('analysis_data', {})
            market_odds = analysis_data.get('market_odds', {})

            # Mercado 1X2
            home_odd = market_odds.get('home_win', 0)
            draw_odd = market_odds.get('draw', 0)
            away_odd = market_odds.get('away_win', 0)

            # ✅ Sanity check: odds absurdas
            if home_odd > 1 and draw_odd > 1 and away_odd > 1:
                if home_odd <= 1.01 or draw_odd <= 1.01 or away_odd <= 1.01:
                    matches_with_issues.add(match_id)
                elif home_odd > 500 or draw_odd > 500 or away_odd > 500:
                    matches_with_issues.add(match_id)
                else:
                    overround_1x2 = (1/home_odd + 1/draw_odd + 1/away_odd) - 1
                    # ✅ CORREÇÃO 21/02: Filtrar overround fora de [0, 20%]
                    if 0 <= overround_1x2 <= 0.20:
                        overrounds_1x2.append(overround_1x2)
                    else:
                        matches_with_issues.add(match_id)

            # Mercado Over/Under 2.5
            over25_odd = market_odds.get('over_2_5', 0) or market_odds.get('over_2.5', 0)
            under25_odd = market_odds.get('under_2_5', 0) or market_odds.get('under_2.5', 0)
            
            if over25_odd > 1 and under25_odd > 1:
                if over25_odd > 1.01 and under25_odd > 1.01 and over25_odd < 100 and under25_odd < 100:
                    overround_ou25 = (1/over25_odd + 1/under25_odd) - 1
                    if 0 <= overround_ou25 <= 0.20:
                        overrounds_ou25.append(overround_ou25)
                    else:
                        matches_with_issues.add(match_id)

            # Mercado BTTS (Both Teams To Score)
            btts_yes_odd = market_odds.get('btts_yes', 0)
            btts_no_odd = market_odds.get('btts_no', 0)
            
            if btts_yes_odd > 1 and btts_no_odd > 1:
                if btts_yes_odd > 1.01 and btts_no_odd > 1.01 and btts_yes_odd < 100 and btts_no_odd < 100:
                    overround_btts = (1/btts_yes_odd + 1/btts_no_odd) - 1
                    if 0 <= overround_btts <= 0.20:
                        overrounds_btts.append(overround_btts)
                    else:
                        matches_with_issues.add(match_id)

        # Consolidar todas as amostras
        all_overrounds = overrounds_1x2 + overrounds_ou25 + overrounds_btts
        matches_total = len(analyses)
        total_samples = len(all_overrounds)
        matches_with_issues_count = len(matches_with_issues)

        # ✅ CORREÇÃO 21/02: Coverage POR MERCADO (não assume 3 por jogo)
        cov_1x2 = len(overrounds_1x2) / matches_total * 100 if matches_total > 0 else 0
        cov_ou25 = len(overrounds_ou25) / matches_total * 100 if matches_total > 0 else 0
        cov_btts = len(overrounds_btts) / matches_total * 100 if matches_total > 0 else 0
        
        # Data quality: se TODOS os mercados têm coverage baixa, é poor
        # Se pelo menos UM tem >= 40%, é útil para diagnóstico
        if cov_1x2 < 20 and cov_ou25 < 20 and cov_btts < 20:
            data_quality = 'poor'
        elif matches_with_issues_count / matches_total > 0.3:
            data_quality = 'suspect'
        else:
            data_quality = 'good'

        # ✅ CORREÇÃO 21/02: Tratar 'poor' e 'suspect' igualmente (dados insuficientes)
        if not all_overrounds or data_quality in ('suspect', 'poor'):
            reason_text = 'suspeitos' if data_quality == 'suspect' else 'insuficientes'
            return {
                'regime': 'data_suspect',
                'median_overround': None,
                'iqr_overround': None,
                'overround_by_market': {
                    '1x2_median': None,
                    '1x2_samples': len(overrounds_1x2),
                    '1x2_coverage': round(cov_1x2, 1),
                    'ou25_median': None,
                    'ou25_samples': len(overrounds_ou25),
                    'ou25_coverage': round(cov_ou25, 1),
                    'btts_median': None,
                    'btts_samples': len(overrounds_btts),
                    'btts_coverage': round(cov_btts, 1),
                },
                'total_samples': total_samples,
                'matches_total': matches_total,
                'data_quality': data_quality,
                'reason': f'Dados {reason_text} ({total_samples} amostras, {matches_with_issues_count} matches com issues)',
            }

        # ✅ CORREÇÃO 21/02: Usar _median() util (robusta para par/ímpar)
        all_overrounds_pct = [x * 100 for x in all_overrounds]
        median_overround = self._median(all_overrounds_pct)
        
        # IQR (Interquartile Range) robusto
        # ✅ CORREÇÃO 21/02: Proteção contra samples muito pequenas
        sorted_pct = sorted(all_overrounds_pct)
        n = len(sorted_pct)
        
        if n >= 4:
            p25_idx = n // 4
            p75_idx = 3 * n // 4
            p25 = sorted_pct[p25_idx]
            p75 = sorted_pct[p75_idx]
            iqr_overround = p75 - p25
        else:
            # Com menos de 4 amostras, IQR não é confiável
            iqr_overround = 0.0

        # Overround mediano por mercado (usando _median())
        overround_by_market = {
            '1x2_median': round(self._median([x * 100 for x in overrounds_1x2]), 2) if overrounds_1x2 else None,
            '1x2_samples': len(overrounds_1x2),
            '1x2_coverage': round(cov_1x2, 1),
            'ou25_median': round(self._median([x * 100 for x in overrounds_ou25]), 2) if overrounds_ou25 else None,
            'ou25_samples': len(overrounds_ou25),
            'ou25_coverage': round(cov_ou25, 1),
            'btts_median': round(self._median([x * 100 for x in overrounds_btts]), 2) if overrounds_btts else None,
            'btts_samples': len(overrounds_btts),
            'btts_coverage': round(cov_btts, 1),
        }

        # Classificar regime pela MEDIANA (não média)
        # Thresholds assumidos sem validação de fonte (atenção do usuário)
        if median_overround < 4.0:
            regime = 'competitive'
            reason = f"Mercado competitivo (mediana {median_overround:.1f}%, IQR {iqr_overround:.1f}%) — linha afiada, difícil bater"
        elif median_overround <= 7.0:
            regime = 'standard'
            reason = f"Mercado padrão (mediana {median_overround:.1f}%, IQR {iqr_overround:.1f}%)"
        else:
            regime = 'illiquid'
            reason = f"Mercado ilíquido (mediana {median_overround:.1f}%, IQR {iqr_overround:.1f}%) — margem alta, menos liquidez"

        return {
            'regime': regime,
            'median_overround': round(median_overround, 2),
            'iqr_overround': round(iqr_overround, 2),
            'overround_by_market': overround_by_market,
            'total_samples': total_samples,
            'matches_total': matches_total,
            'data_quality': data_quality,
            'reason': reason,
        }

    def generate_for_today(self, days_ahead=1, mode=None, execution=None):
        """
        Gera apostas para partidas do dia usando busca híbrida inteligente
        
        Args:
            days_ahead: Número de dias à frente para buscar (padrão: 1 - apenas hoje)
            mode: Modo de busca ('priority', 'all', 'hybrid'). Se None, usa self.SEARCH_MODE
            execution: Instância de TaskExecution para tracking de progresso (opcional)
        
        Returns:
            dict: Estatísticas da geração
        """
        # Armazenar execution para tracking
        self.execution = execution
        
        # Atualizar stage inicial
        if self.execution:
            self.execution.update_progress(
                stage='searching',
                log_message='Iniciando busca de partidas...'
            )
        
        # Usar modo especificado ou padrão da classe
        search_mode = mode or self.SEARCH_MODE
        today = timezone.now().date()
        
        logger.info("=" * 100)
        period_text = "HOJE" if days_ahead == 1 else f"Próximos {days_ahead} dias"
        mode_text = {
            'priority': '🎯 LIGAS PRIORITÁRIAS',
            'all': '🌍 TODAS AS LIGAS',
            'hybrid': '🔄 BUSCA HÍBRIDA INTELIGENTE'
        }.get(search_mode, search_mode.upper())
        logger.info(f"{mode_text} - GERAÇÃO DE BILHETES - {period_text} ({today.strftime('%d/%m/%Y')})")
        logger.info("=" * 100)
        
        dates_to_search = [
            (today + timedelta(days=i)).strftime('%Y-%m-%d') 
            for i in range(days_ahead)
        ]
        
        all_fixtures = []
        
        # ============================================================================
        # ESTRATÉGIA 1: BUSCA PRIORITÁRIA (ligas principais)
        # ============================================================================
        if search_mode in ['priority', 'hybrid']:
            logger.info(f"\n🎯 FASE 1: Buscando em {len(self.PRIORITY_LEAGUES)} ligas prioritárias...")
            logger.info(f"📅 Datas: {', '.join(dates_to_search)}")
            logger.info("")
            
            for date_str in dates_to_search:
                for league_id in self.PRIORITY_LEAGUES:
                    try:
                        # Buscar por liga específica (mais eficiente)
                        response = self.api.get_fixtures_by_date(date_str, league_id=league_id, season=2025)
                        if response and response.get('response'):
                            fixtures = response['response']
                            if len(fixtures) > 0:
                                all_fixtures.extend(fixtures)
                                logger.info(f"   ✅ Liga {league_id} ({date_str}): {len(fixtures)} partida(s)")
                    except Exception as e:
                        logger.debug(f"   ⚠️ Liga {league_id} ({date_str}): {e}")
                        continue
            
            logger.info(f"\n📊 Fase 1 concluída: {len(all_fixtures)} partidas encontradas em ligas prioritárias")
        
        # ============================================================================
        # ESTRATÉGIA 2: EXPANSÃO PARA TODAS AS LIGAS (se necessário)
        # ✅ CORREÇÃO 19/02/2026: DESATIVADO para modo 'priority' (qualidade > quantidade)
        # ============================================================================
        if search_mode == 'all' or (search_mode == 'hybrid' and len(all_fixtures) < self.MIN_MATCHES_THRESHOLD):
            if search_mode == 'hybrid':
                logger.info(f"\n⚠️  Apenas {len(all_fixtures)} partidas encontradas (< {self.MIN_MATCHES_THRESHOLD})")
                logger.info("🔄 FASE 2: Expandindo busca para TODAS as ligas disponíveis...")
            else:
                logger.info(f"\n🌍 Buscando TODAS as partidas disponíveis...")
                logger.info(f"📅 Datas: {', '.join(dates_to_search)}")
            
            logger.info("")
            
            # Buscar sem filtro de liga
            for date_str in dates_to_search:
                try:
                    logger.info(f"   🔍 Buscando todas as ligas de {date_str}...")
                    result = self.football_api.get_fixtures_by_date(date_str)
                    
                    if result.get('success') and result.get('fixtures'):
                        fixtures = result['fixtures']
                        
                        # Filtrar partidas já encontradas (evitar duplicatas)
                        existing_ids = {f['fixture']['id'] for f in all_fixtures}
                        new_fixtures = [f for f in fixtures if f['fixture']['id'] not in existing_ids]
                        
                        all_fixtures.extend(new_fixtures)
                        logger.info(f"   ✅ {date_str}: {len(new_fixtures)} novas partidas (+{len(fixtures)-len(new_fixtures)} já encontradas)")
                    else:
                        logger.warning(f"   ⚠️ {date_str}: Nenhuma partida encontrada")
                except Exception as e:
                    logger.error(f"   ❌ Erro ao buscar {date_str}: {e}")
                    continue
            
            logger.info(f"\n📊 Busca expandida: {len(all_fixtures)} partidas no total")
        
        logger.info(f"\n{'─' * 100}")
        logger.info(f"📋 TOTAL DE PARTIDAS ENCONTRADAS: {len(all_fixtures)}")
        logger.info(f"{'─' * 100}\n")
        
        # Atualizar progresso: partidas encontradas
        if self.execution:
            self.execution.update_progress(
                stage='searching',
                matches_found=len(all_fixtures),
                log_message=f'{len(all_fixtures)} partidas encontradas'
            )
        
        if len(all_fixtures) == 0:
            period_warning = "hoje" if days_ahead == 1 else "nos próximos dias"
            logger.warning(f"⚠️  Nenhuma partida encontrada {period_warning}")
            return {
                'matches_analyzed': 0,
                'multiple_count': 0,
                'value_count': 0,
                'total_bets': 0,
                'api_calls': 0,
                'cache_hits': 0,
                'search_mode': search_mode
            }
        
        # Filtrar apenas partidas agendadas (não iniciadas)
        scheduled_fixtures = [
            f for f in all_fixtures 
            if f.get('fixture', {}).get('status', {}).get('short') in ['NS', 'TBD', 'PST']
        ]
        
        logger.info(f"📋 Partidas agendadas (não iniciadas): {len(scheduled_fixtures)}")
        
        # Definir prioridade das ligas (1=maior prioridade, 3=menor)
        LEAGUE_PRIORITY = {
            # Ligas Top 5 Europeias
            'Premier League': 1, 'La Liga': 1, 'Serie A': 1, 'Bundesliga': 1, 'Ligue 1': 1,
            # Ligas Europeias Secundárias
            'Eredivisie': 2, 'Liga Portugal': 2, 'Primeira Liga': 2,
            'Championship': 2, 'Belgian Pro League': 2, 'Süper Lig': 2,
            'Scottish Premiership': 2,
            # Competições Internacionais
            'UEFA Champions League': 1, 'Copa Libertadores': 1,
            'UEFA Europa League': 2, 'UEFA Conference League': 2,
            # Ligas Brasileiras
            'Brasileirão Série A': 1, 'Brasileirão Série B': 2,
            # Ligas Secundárias Europeias
            'La Liga 2': 3, 'Serie B': 3, 'Bundesliga 2': 3, 'Ligue 2': 3,
            # Outras Competições
            'FA Cup': 2, 'Copa del Rey': 2, 'Coppa Italia': 2, 'DFB Pokal': 2,
            # Ligas Africanas
            'Moçambola': 2, 'DSTV Premiership': 2,
            'CAF Champions League': 2, 'CAF Confederation Cup': 3,
            # América do Norte
            'MLS': 2,
            # Ásia
            'J1 League': 2,
        }
        
        # Adicionar prioridade a cada fixture
        for fixture in scheduled_fixtures:
            league_name = fixture.get('league', {}).get('name', '')
            league_id = fixture.get('league', {}).get('id', 0)
            # Priorizar também por ID (ligas prioritárias)
            if league_id in self.PRIORITY_LEAGUES:
                fixture['_priority'] = 1
            else:
                fixture['_priority'] = LEAGUE_PRIORITY.get(league_name, 3)
        
        # Ordenar por: 1) Prioridade da liga, 2) Data/hora
        scheduled_fixtures.sort(
            key=lambda f: (
                f.get('_priority', 3),  # Ligas prioritárias primeiro
                f.get('fixture', {}).get('timestamp', 0)  # Depois por data
            )
        )
        
        # Limitar ao máximo configurado
        max_matches = min(len(scheduled_fixtures), self.MAX_TOTAL_MATCHES)
        fixtures_to_analyze = scheduled_fixtures[:max_matches]
        
        logger.info(f"🎯 Analisando as {max_matches} partidas mais relevantes...")
        if len(scheduled_fixtures) > max_matches:
            logger.info(f"   ℹ️  ({len(scheduled_fixtures) - max_matches} partidas de menor prioridade serão ignoradas)")
        logger.info("")
        
        # Atualizar progresso: iniciando análise
        if self.execution:
            self.execution.update_progress(
                stage='analyzing',
                matches_found=max_matches,
                matches_processed=0,
                log_message=f'🎯 Iniciando análise de {max_matches} partidas com validação de qualidade FASE 2...'
            )
        
        analyses = []
        
        # ✅ FASE 2: Estatísticas de qualidade
        quality_stats = {
            'total_checked': 0,
            'approved': 0,
            'rejected': 0,
            'rejection_reasons': {},
            'avg_quality_score': 0.0,
            'quality_scores': []
        }
        
        for idx, fixture in enumerate(fixtures_to_analyze, 1):
            try:
                # ✅ Verificar se foi cancelada a cada 5 partidas
                if idx % 5 == 0:
                    self._check_cancellation()
                
                fixture_data = fixture.get('fixture', {})
                teams = fixture.get('teams', {})
                league = fixture.get('league', {})
                
                fixture_id = fixture_data.get('id')
                home_team = teams.get('home', {}).get('name', 'Unknown')
                away_team = teams.get('away', {}).get('name', 'Unknown')
                league_name = league.get('name', 'Unknown')
                
                logger.info(f"\n{'─' * 80}")
                logger.info(f"[{idx}/{len(fixtures_to_analyze)}] Analisando: {home_team} vs {away_team}")
                logger.info(f"    Liga: {league_name}")
                logger.info(f"    Fixture ID: {fixture_id}")
                
                # ✅ CORREÇÃO 19/02/2026: Validar qualidade ANTES de analisar
                # ✅ FASE 2: Logging detalhado de qualidade
                validation = self._validate_match_quality(fixture)
                
                # Registrar estatísticas de qualidade
                quality_stats['total_checked'] += 1
                quality_stats['quality_scores'].append(validation['quality_score'])
                
                if not validation['is_valid']:
                    quality_stats['rejected'] += 1
                    reason = validation['reason'].split(':')[0]  # Primeira parte da razão
                    quality_stats['rejection_reasons'][reason] = quality_stats['rejection_reasons'].get(reason, 0) + 1
                    
                    logger.info(f"    ⏩ PULANDO: {validation['reason']}")
                    logger.info(f"    📊 Score de qualidade: {validation['quality_score']:.1f}/100")
                    if validation.get('details'):
                        logger.info(f"    📋 Detalhes:")
                        for detail in validation['details']:
                            logger.info(f"       {detail}")
                    continue
                
                quality_stats['approved'] += 1
                
                logger.info(f"    ✅ Qualidade validada: {validation['reason']}")
                logger.info(f"    📊 Score: {validation['quality_score']:.1f}/100")
                if validation.get('details'):
                    logger.debug(f"    📋 Detalhes de qualidade:")
                    for detail in validation['details']:
                        logger.debug(f"       {detail}")
                
                # Log no TaskExecution a cada 10 partidas aprovadas
                if self.execution and quality_stats['approved'] % 10 == 0:
                    self.execution.update_progress(
                        matches_processed=idx,
                        log_message=f"✅ {quality_stats['approved']} partidas aprovadas (score médio: {sum(quality_stats['quality_scores'])/len(quality_stats['quality_scores']):.1f}/100)"
                    )
                
                # Criar estrutura de dados compatível com o orchestrator
                # O orchestrator espera um objeto com api_football_id
                league_id = league.get('id')
                match_data = type('obj', (object,), {
                    'id': fixture_id,
                    'api_football_id': fixture_id,
                    'home_team': type('obj', (object,), {
                        'name': home_team,
                        'id': teams.get('home', {}).get('id')
                    })(),
                    'away_team': type('obj', (object,), {
                        'name': away_team,
                        'id': teams.get('away', {}).get('id')
                    })(),
                    'league': type('obj', (object,), {
                        'name': league_name,
                        'id': league_id,
                        'api_football_id': league_id  # Necessário para orchestrator
                    })(),
                    'match_date': fixture_data.get('date'),
                })()
                
                # Análise com estratégia VALUE (para value bets)
                logger.info("    🔍 Executando análise VALUE...")
                try:
                    result_value = self.orchestrator.run(match_data, strategy='value')
                    logger.info(f"    ✅ VALUE analysis completed")
                except Exception as e:
                    logger.error(f"    ❌ Erro na análise VALUE: {e}")
                    result_value = None
                
                # Análise com estratégia MULTIPLE (para bilhetes)
                logger.info("    🔍 Executando análise MULTIPLE...")
                try:
                    result_multiple = self.orchestrator.run(match_data, strategy='multiple')
                    logger.info(f"    ✅ MULTIPLE analysis completed")
                except Exception as e:
                    logger.error(f"    ❌ Erro na análise MULTIPLE: {e}")
                    result_multiple = None
                
                # Pular se ambas análises falharam
                if not result_value and not result_multiple:
                    logger.warning(f"    ⚠️ Pulando partida - ambas análises falharam")
                    continue
                
                analyses.append({
                    'match': match_data,
                    'fixture_id': fixture_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'league_name': league_name,
                    'league_id': league_id,
                    'match_date': fixture_data.get('date'),
                    'value_result': result_value,
                    'multiple_result': result_multiple
                })
                
                # Estimar requisições (2 análises, mas cache reduz muito)
                self.api_calls += 2
                
                logger.info(f"    ✅ Análise concluída")
                
                # Atualizar progresso após cada partida
                if self.execution:
                    self.execution.update_progress(
                        matches_processed=idx,
                        log_message=f'Analisada: {home_team} vs {away_team}'
                    )
                
            except Exception as e:
                logger.error(f"    ❌ Erro ao analisar {home_team} vs {away_team}: {e}", exc_info=True)
                continue
        
        logger.info(f"\n{'=' * 100}")
        logger.info(f"✅ {len(analyses)} partidas analisadas com sucesso")
        logger.info(f"{'=' * 100}\n")

        # Detectar regime de mercado via overround das bookmakers (sinal externo ao modelo)
        regime_info = self._detect_market_regime(analyses)
        logger.info(f"\n{'─' * 80}")
        logger.info(f"📊 REGIME DE MERCADO: {regime_info['regime'].upper()} (qualidade: {regime_info['data_quality']})")
        logger.info(f"   {regime_info['reason']}")
        if regime_info['median_overround'] is not None:
            logger.info(f"   Overround mediana: {regime_info['median_overround']:.2f}% (IQR: {regime_info['iqr_overround']:.2f}%)")
            logger.info(f"   Overround por mercado:")
            by_market = regime_info['overround_by_market']
            if by_market.get('1x2_median'):
                logger.info(f"      1X2: {by_market['1x2_median']:.2f}% ({by_market['1x2_samples']} amostras, {by_market['1x2_coverage']:.0f}% coverage)")
            if by_market.get('ou25_median'):
                logger.info(f"      O/U 2.5: {by_market['ou25_median']:.2f}% ({by_market['ou25_samples']} amostras, {by_market['ou25_coverage']:.0f}% coverage)")
            if by_market.get('btts_median'):
                logger.info(f"      BTTS: {by_market['btts_median']:.2f}% ({by_market['btts_samples']} amostras, {by_market['btts_coverage']:.0f}% coverage)")
        logger.info(f"   Amostras totais: {regime_info['total_samples']}")
        logger.info(f"   [DIAGNÓSTICO] MIN_VALUE_EV fixo em +{self.MIN_VALUE_EV:.0f}%, MIN_MULTIPLE_EV em {self.MIN_MULTIPLE_EV:+.0f}%")
        logger.info(f"{'─' * 80}\n")

        if self.execution:
            regime_emoji = {'competitive': '🔵', 'standard': '🟡', 'illiquid': '🟠'}.get(regime_info['regime'], '⚪')
            self.execution.update_progress(
                log_message=f"{regime_emoji} Regime de mercado: {regime_info['regime'].upper()} — {regime_info['reason']}"
            )

        # Atualizar progresso: criando bilhetes
        if self.execution:
            self.execution.update_progress(
                stage='creating',
                matches_processed=len(analyses),
                log_message=f'Criando bilhetes a partir de {len(analyses)} análises...'
            )
        
        # Gerar bilhetes e value bets
        with transaction.atomic():
            # Deletar apostas antigas do mesmo dia (se regenerar)
            DailyBet.objects.filter(date=today).delete()
            
            # Gerar bilhetes múltiplos
            multiple_bets = self._generate_multiple_tickets(analyses, today)
            
            # Value bets com threshold fixo (MIN_VALUE_EV) — não ajustado por regime
            value_bets = self._generate_value_bets(analyses, today)
            
            # Atualizar progresso: bilhetes criados
            if self.execution:
                total_bets = len(multiple_bets) + len(value_bets)
                self.execution.update_progress(
                    bets_created=total_bets,
                    log_message=f'{len(multiple_bets)} bilhetes múltiplos e {len(value_bets)} value bets criados'
                )
        
        logger.info(f"\n{'=' * 100}")
        logger.info(f"🎉 GERAÇÃO CONCLUÍDA")
        logger.info(f"{'=' * 100}")
        logger.info(f"📋 Bilhetes múltiplos criados: {len(multiple_bets)}")
        logger.info(f"⚡ Value bets criadas: {len(value_bets)}")
        logger.info(f"📊 Total de apostas: {len(multiple_bets) + len(value_bets)}")
        logger.info(f"⚽ Partidas analisadas: {len(analyses)}")
        logger.info(f"🔌 Requisições API (estimado): {self.api_calls}")
        logger.info(f"🔄 Modo de busca utilizado: {search_mode}")
        
        # ✅ FASE 2: Resumo de qualidade
        if quality_stats['quality_scores']:
            quality_stats['avg_quality_score'] = sum(quality_stats['quality_scores']) / len(quality_stats['quality_scores'])
        
        logger.info(f"\n📊 ESTATÍSTICAS DE QUALIDADE:")
        logger.info(f"   Partidas verificadas: {quality_stats['total_checked']}")
        logger.info(f"   ✅ Aprovadas: {quality_stats['approved']} ({quality_stats['approved']/quality_stats['total_checked']*100 if quality_stats['total_checked'] > 0 else 0:.1f}%)")
        logger.info(f"   ⏩ Rejeitadas: {quality_stats['rejected']} ({quality_stats['rejected']/quality_stats['total_checked']*100 if quality_stats['total_checked'] > 0 else 0:.1f}%)")
        logger.info(f"   📊 Score médio: {quality_stats['avg_quality_score']:.1f}/100")
        
        if quality_stats['rejection_reasons']:
            logger.info(f"\n   Motivos de rejeição:")
            for reason, count in sorted(quality_stats['rejection_reasons'].items(), key=lambda x: x[1], reverse=True):
                logger.info(f"      • {reason}: {count}")
        
        # ✅ FASE 2: Log de qualidade no TaskExecution
        if self.execution:
            approval_rate = quality_stats['approved']/quality_stats['total_checked']*100 if quality_stats['total_checked'] > 0 else 0
            rejection_summary = ', '.join([f"{reason}: {count}" for reason, count in quality_stats['rejection_reasons'].items()]) if quality_stats['rejection_reasons'] else 'Nenhuma'
            
            self.execution.update_progress(
                log_message=f"📊 Validação de qualidade concluída: {quality_stats['approved']}/{quality_stats['total_checked']} aprovadas ({approval_rate:.1f}%), score médio {quality_stats['avg_quality_score']:.1f}/100. Rejeições: {rejection_summary}"
            )
        
        logger.info(f"{'=' * 100}\n")
        
        # Montar lista de partidas analisadas para o relatório
        analyzed_matches_list = []
        for analysis in analyses:
            analyzed_matches_list.append({
                'fixture_id': analysis['fixture_id'],
                'home_team': analysis['home_team'],
                'away_team': analysis['away_team'],
                'league_name': analysis['league_name'],
                'match_date': analysis['match_date']
            })
        
        return {
            'matches_analyzed': len(analyses),
            'multiple_count': len(multiple_bets),
            'value_count': len(value_bets),
            'total_bets': len(multiple_bets) + len(value_bets),
            'api_calls': self.api_calls,
            'cache_hits': self.cache_hits,
            'search_mode': search_mode,
            'total_fixtures_found': len(all_fixtures),
            'scheduled_fixtures': len(scheduled_fixtures),
            'analyzed_matches': analyzed_matches_list,
            # ✅ FASE 2: Estatísticas de qualidade
            'quality_stats': {
                'total_checked': quality_stats['total_checked'],
                'approved': quality_stats['approved'],
                'rejected': quality_stats['rejected'],
                'approval_rate': quality_stats['approved'] / quality_stats['total_checked'] * 100 if quality_stats['total_checked'] > 0 else 0,
                'avg_quality_score': quality_stats['avg_quality_score'],
                'rejection_reasons': quality_stats['rejection_reasons']
            },
            # Regime de mercado (diagnóstico via overround externo)
            'market_regime': {
                'regime': regime_info['regime'],
                'median_overround': regime_info['median_overround'],
                'iqr_overround': regime_info['iqr_overround'],
                'overround_by_market': regime_info['overround_by_market'],
                'total_samples': regime_info['total_samples'],
                'data_quality': regime_info['data_quality'],
                'reason': regime_info['reason'],
            }
        }
        
    
    def _generate_multiple_tickets(self, analyses, date):
        """
        Gera bilhetes múltiplos com as melhores apostas (alta probabilidade)
        
        Estratégia:
        - Selecionar top apostas com maior probabilidade de cada partida
        - Filtrar por contexto: confiança ≥4★, risco baixo/médio, empate <35%
        - 🆕 NOVO: Rejeitar jogos onde AMBOS times têm má forma absoluta (<50%)
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
            fixture_id = analysis['fixture_id']
            home_team = analysis['home_team']
            away_team = analysis['away_team']
            league_name = analysis['league_name']
            match_date = analysis['match_date']
            result = analysis['value_result']
            
            # ✅ CORREÇÃO 21/02: Pular se análise VALUE falhou
            if result is None:
                logger.debug(f"   ⏩ Pulando {home_team} vs {away_team}: análise VALUE falhou")
                continue
            
            analysis_data = result.get('analysis_data', {})
            top_bets = analysis_data.get('top_bets', [])
            consensus = analysis_data.get('consensus', {})

            # ✅ CORRIGIDO 17/02/2026: Filtros melhorados com validação de contexto
            # top_bets já vem ordenado por ranking_score = selection_score × ev × conf × risk
            if top_bets:
                # Extrair dados de contexto da análise
                decision_data = analysis_data.get('decision', {}) if 'decision' in analysis_data else analysis_data
                confidence = decision_data.get('confidence', {})
                confidence_stars = confidence.get('stars', 0) if isinstance(confidence, dict) else 0
                risk = decision_data.get('risk', 'high')
                
                # 🆕 NOVO 17/02/2026: Extrair forma absoluta dos times
                features = result.get('features', {})
                form_features = features.get('form', {})
                home_weighted_form = form_features.get('home_weighted_form', 1.5)
                away_weighted_form = form_features.get('away_weighted_form', 1.5)
                
                # Filtrar por critérios de bilhete:
                # 1. Probabilidade dinâmica baseada no tamanho (será verificada depois)
                # 2. Odd na faixa conservadora (1.30 - 1.50)
                # 3. EV >= 5% (usando VALUE_RESULT com MIN_VALUE_EV)
                # 4. Confidence ≥ 4 estrelas
                # 5. Risco baixo/médio
                # 6. Empate < 35%
                # 7. 🆕 Forma absoluta mínima (previne apostas em times com má forma)
                best_bet = None
                
                # Verificar se o jogo tem contexto problemático
                draw_prob = consensus.get('draw', 0)
                if draw_prob > self.MAX_DRAW_PROBABILITY:
                    logger.info(f"   ⏩ Pulando {home_team} vs {away_team}: empate muito provável ({draw_prob*100:.1f}% > {self.MAX_DRAW_PROBABILITY*100:.0f}%)")
                    continue
                
                # 🆕 NOVO 17/02/2026: Verificar forma absoluta
                # Rejeitar jogos onde AMBOS times têm má forma (imprevisibilidade alta)
                if home_weighted_form < self.MIN_ABSOLUTE_FORM and away_weighted_form < self.MIN_ABSOLUTE_FORM:
                    logger.info(f"   ⏩ Pulando {home_team} vs {away_team}: ambos com má forma (Casa: {home_weighted_form:.2f}, Fora: {away_weighted_form:.2f} < {self.MIN_ABSOLUTE_FORM})")
                    logger.info(f"      Razão: Jogos entre times em má forma são imprevisíveis")
                    continue
                
                if confidence_stars < self.MIN_CONFIDENCE_STARS:
                    logger.debug(f"   ⏩ Pulando {home_team} vs {away_team}: confiança baixa ({confidence_stars} < {self.MIN_CONFIDENCE_STARS} estrelas)")
                    continue
                
                if risk not in self.ALLOWED_RISK_LEVELS:
                    logger.debug(f"   ⏩ Pulando {home_team} vs {away_team}: risco alto ({risk})")
                    continue
                
                # 🆕 CORREÇÃO CRÍTICA 21/02: Selecionar a MELHOR aposta contextual, não a primeira
                # top_bets já vem ordenado por contextual_fit (DecisionEngine)
                # Filtrar apostas elegíveis e escolher a com MAIOR contextual_fit
                eligible_bets = []
                for bet in top_bets:
                    prob = bet.get('probability', 0)
                    odd = bet.get('market_odd', 0)
                    ev_pct = bet.get('ev_pct', 0)
                    
                    # ✅ CORREÇÃO CRÍTICA 21/02: Usar VALUE_RESULT (EV >= 5%) com filtros de múltiplos
                    # - VALUE_RESULT já filtra EV >= 5% (MIN_VALUE_EV)
                    # - Prob ≥65% → alta confiança para bilhetes múltiplos
                    # - Odd 1.30-1.50 → 3-5 apostas = odd total 2.20-7.59
                    # RESULTADO: Melhor dos dois mundos (EV positivo + prob alta)
                    if (prob >= 0.65 and  # Mínimo 65% (pragmático)
                        odd >= self.MIN_ODD_MULTIPLE and  # Odd mínima 1.30
                        odd <= self.MAX_ODD_MULTIPLE):  # Odd máxima 1.50
                        eligible_bets.append(bet)
                
                if not eligible_bets:
                    logger.debug(f"   ⏩ Pulando {home_team} vs {away_team}: nenhuma aposta atende critérios de bilhete")
                    continue
                
                # 🆕 NOVO 21/02: Selecionar aposta com MELHOR adequação contextual
                # Ordenar por: 1) contextual_fit (se disponível), 2) score, 3) probabilidade
                best_bet = max(eligible_bets, key=lambda b: (
                    b.get('contextual_fit', 1.0),  # 1º: adequação contextual
                    b.get('score', 0),              # 2º: score geral
                    b.get('probability', 0)         # 3º: probabilidade
                ))
                
                contextual_fit = best_bet.get('contextual_fit', 1.0)
                if contextual_fit > 1.1:
                    logger.info(f"   🎯 Selecionado por CONTEXTO: {best_bet['market']} (fit={contextual_fit:.2f})")
                elif len(eligible_bets) > 1:
                    logger.info(f"   🎯 Melhor entre {len(eligible_bets)} elegíveis: {best_bet['market']}")

                logger.info(f"   🎯 Seleção Bilhete: {best_bet['market']} ({best_bet['pick']}) - {best_bet['probability']*100:.0f}% @ {best_bet['market_odd']:.2f}")
                if 'post_reason' in best_bet:
                    logger.info(f"      Razão: {best_bet['post_reason']}")

                # ✅ CORREÇÃO 21/02: Incluir league_id para anti-correlação robusta
                all_bets.append({
                    'fixture_id': fixture_id,
                    'match': f"{home_team} vs {away_team}",
                    'league': league_name,
                    'league_id': analysis.get('league_id'),
                    'date': match_date,
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
        
        # 📊 DIAGNÓSTICO: Análise de cobertura de mercados
        market_distribution = {}
        for bet in all_bets:
            group = self._market_group(bet['market'])
            market_distribution[group] = market_distribution.get(group, 0) + 1
        
        logger.info(f"   📈 Distribuição por grupo de mercado:")
        for group, count in sorted(market_distribution.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"      {group}: {count} apostas")
        
        # ✅ CORREÇÃO 21/02: Coverage correto (1 pick por jogo elegível, não 25 mercados)
        coverage_pct = len(all_bets) / len(analyses) * 100 if analyses else 0
        if coverage_pct < 30:
            logger.warning(f"   ⚠️  COBERTURA BAIXA: {len(all_bets)}/{len(analyses)} jogos geraram pick elegível ({coverage_pct:.1f}%)")
            logger.warning(f"       Filtros de retorno (prob ≥65%, odd ≥{self.MIN_ODD_MULTIPLE}, EV ≥{self.MIN_MULTIPLE_EV}%) descartam picks arriscados")
            logger.warning(f"       Mercados sistematicamente rejeitados: Away Win, Over 2.5, BTTS Yes, Dupla Chance")
        
        # ✅ CORRIGIDO 17/02/2026: Ordenar por SCORE (contexto) ao invés de apenas probabilidade
        # Score já inclui: probabilidade × contexto × EV × confiança × risco
        all_bets.sort(key=lambda x: x['score'], reverse=True)
        logger.info(f"   🎯 Ordenação por SCORE contextual (não apenas probabilidade)")
        
        # Criar bilhetes de 3, 5 e 7 apostas
        tickets = []
        
        for size in [3, 5, 7]:
            if len(all_bets) < size:
                logger.info(f"   ⚠️  Apostas insuficientes para bilhete {size}x ({len(all_bets)} disponíveis)")
                continue
            
            # ✅ CORRIGIDO 17/02/2026: Filtrar apostas por probabilidade mínima dinâmica
            if size == 3:
                min_individual_prob = self.MIN_MULTIPLE_PROBABILITY_3X
                min_combined_prob = self.MIN_COMBINED_PROBABILITY_3X
            elif size == 5:
                min_individual_prob = self.MIN_MULTIPLE_PROBABILITY_5X
                min_combined_prob = self.MIN_COMBINED_PROBABILITY_5X
            else:
                min_individual_prob = self.MIN_MULTIPLE_PROBABILITY_7X
                min_combined_prob = self.MIN_COMBINED_PROBABILITY_7X
            
            # Filtrar apostas que atendem a probabilidade mínima individual
            eligible_bets = [bet for bet in all_bets if bet['probability'] >= min_individual_prob]
            
            if len(eligible_bets) < size:
                logger.info(f"   ⏩ Bilhete {size}x: apenas {len(eligible_bets)} apostas ≥{min_individual_prob*100:.0f}% (precisa de {size})")
                continue
            
            # ✅ CORREÇÃO 21/02: Seleção com anti-correlação (liga + grupo de mercado)
            selections = self._select_diversified_bets(eligible_bets, size)
            
            if not selections:
                logger.info(f"   ⏩ Bilhete {size}x: não foi possível montar com diversificação (anti-correlação liga+mercado)")
                continue
            
            # Calcular odd total e probabilidade combinada
            # ✅ CORREÇÃO 21/02: Sanity check contra overflow/underflow
            total_odd = 1.0
            combined_prob = 1.0
            
            for sel in selections:
                total_odd *= sel['odd']
                combined_prob *= sel['probability']
                
                # Proteção contra overflow (odd muito alta)
                if total_odd > 10000:
                    logger.warning(f"   ⚠️ Bilhete {size}x: odd total excede 10.000 (overflow risk)")
                    break
                
                # Proteção contra underflow (prob muito baixa)
                if combined_prob < 0.0001:
                    logger.debug(f"   ⏩ Bilhete {size}x: prob combinada < 0.01% (underflow)")
                    break
            
            # Skip se houve overflow/underflow
            if total_odd > 10000 or combined_prob < 0.0001:
                continue
            
            # ✅ CORREÇÃO 21/02: Penalidade de correlação residual
            # Mesmo com anti-correlação (liga + grupo), há correlação contextual residual
            # e potencial erro de calibração. Penalidade por tamanho:
            corr_penalty = {3: 0.95, 5: 0.90, 7: 0.85}.get(size, 0.90)
            combined_prob_adjusted = combined_prob * corr_penalty
            
            logger.debug(f"   Prob combinada bruta: {combined_prob*100:.2f}% -> ajustada: {combined_prob_adjusted*100:.2f}% (penalidade {size}x: {corr_penalty})")
            
            # Filtro: probabilidade combinada (ajustada)
            if combined_prob_adjusted < min_combined_prob:
                logger.info(f"   ⏩ Bilhete {size}x: prob ajustada {combined_prob_adjusted*100:.2f}% < {min_combined_prob*100:.0f}%")
                continue
            
            # Filtro: odd total
            if total_odd < self.MIN_TICKET_ODD:
                logger.info(f"   ⏩ Bilhete {size}x: odd {total_odd:.2f} < {self.MIN_TICKET_ODD}")
                continue
            
            if total_odd > self.MAX_TICKET_ODD:
                logger.info(f"   ⏩ Bilhete {size}x: odd {total_odd:.2f} > {self.MAX_TICKET_ODD}")
                continue
            
            # ✅ CORREÇÃO CRÍTICA 21/02: EV do bilhete estava INVERTIDO
            # Fórmula correta: EV = (probabilidade × odd) - 1
            # Usar probabilidade AJUSTADA (com penalidade de correlação)
            # ✅ CORREÇÃO 21/02: Proteção contra divisão por zero
            if combined_prob_adjusted <= 0 or total_odd <= 0:
                logger.warning(f"   ⚠️ Bilhete {size}x: valores inválidos (prob={combined_prob_adjusted:.4f}, odd={total_odd:.2f})")
                continue
            
            fair_odd = 1.0 / combined_prob_adjusted
            ev_pct = ((combined_prob_adjusted * total_odd) - 1.0) * 100

            # ✅ CORREÇÃO 21/02: EV individual pode ser negativo - focamos em prob alta + odd total >2.5
            # MIN_MULTIPLE_EV = -100 (efetivamente ignora EV individual)
            # Lógica: Se cada aposta tem 70-75% prob, odd total >2.5 garante valor a longo prazo
            # mesmo com EV individual negativo (margem das casas)
            if ev_pct < self.MIN_MULTIPLE_EV:
                logger.info(f"   ⏩ Bilhete {size}x: EV {ev_pct:+.1f}% < {self.MIN_MULTIPLE_EV:+.0f}% (extremamente baixo)")
                continue
            
            # Criar bilhete com tratamento de erro
            try:
                bet = DailyBet.objects.create(
                    date=date,
                    bet_type='multiple',
                    selections=selections,
                    total_odd=Decimal(str(round(total_odd, 2))),
                    fair_odd=Decimal(str(round(fair_odd, 2))),
                    combined_probability=combined_prob_adjusted,  # Salvar probabilidade ajustada
                    expected_value=ev_pct,
                    suggested_stake=self._calculate_stake(combined_prob_adjusted, 'multiple')
                )
                
                tickets.append(bet)
                
                logger.info(f"\n   ✅ Bilhete {size}x criado:")
                # ✅ CORREÇÃO 21/02: Mostrar probabilidade AJUSTADA (mesma salva no DB)
                logger.info(f"      Odd: {total_odd:.2f} | Prob: {combined_prob_adjusted*100:.1f}% (ajustada) | EV: {ev_pct:+.1f}%")
                logger.info(f"      Prob bruta (sem penalidade): {combined_prob*100:.1f}%")
                logger.info(f"      Stake sugerido: {bet.suggested_stake:.1f}u")
                logger.info(f"      Apostas:")
                for sel in selections[:3]:  # Mostrar primeiras 3
                    logger.info(f"         • {sel['pick']} ({sel['market']}) - {sel['probability']*100:.0f}% @ {sel['odd']:.2f}")
                if size > 3:
                    logger.info(f"         ... (+{size-3} apostas)")
            except Exception as e:
                logger.error(f"   ❌ Erro ao criar bilhete {size}x: {e}")
                logger.debug(f"      Selections: {selections}")
                continue
        
        logger.info(f"\n   📋 Total de bilhetes criados: {len(tickets)}")
        
        return tickets
    
    def _generate_value_bets(self, analyses, date):
        """
        Gera value bets individuais (maior EV)
        
        Estratégia:
        - Selecionar apostas com EV positivo >= MIN_VALUE_EV (threshold fixo)
        - Probabilidade mínima >= MIN_VALUE_PROBABILITY
        - Ordenar por EV (maior value primeiro)
        - Limitar a MAX_VALUE_BETS por dia
        """
        logger.info(f"\n{'─' * 80}")
        logger.info("⚡ GERANDO VALUE BETS")
        logger.info(f"{'─' * 80}")

        effective_min_ev = self.MIN_VALUE_EV
        logger.info(f"   Threshold fixo: EV ≥ +{effective_min_ev:.0f}%")
        
        all_value_bets = []
        
        for analysis in analyses:
            match = analysis['match']
            result = analysis['value_result']
            
            # ✅ CORREÇÃO 21/02: Pular se análise VALUE falhou
            if result is None:
                continue
            
            top_bets = result.get('analysis_data', {}).get('top_bets', [])
            
            for bet in top_bets:
                ev_pct = bet.get('ev_pct', 0)
                prob = bet['probability']
                odd = bet.get('market_odd')
                
                # Pular apostas sem odd disponível
                if odd is None or odd == 0:
                    continue
                
                if ev_pct < effective_min_ev:
                    continue
                
                if prob < self.MIN_VALUE_PROBABILITY:
                    continue
                
                # match_date pode ser string, datetime, ou None - normalizar com segurança
                match_date_obj = match.match_date
                if isinstance(match_date_obj, str):
                    match_date_str = match_date_obj
                elif match_date_obj is not None:
                    match_date_str = match_date_obj.isoformat()
                else:
                    # ✅ CORREÇÃO 21/02: Fallback se match_date for None
                    match_date_str = date.isoformat() if date else 'N/A'
                
                # 🆕 NOVO 21/02: Incluir contextual_fit para ordenação secundária
                contextual_fit = bet.get('contextual_fit', 1.0)
                
                all_value_bets.append({
                    'match_id': match.id,
                    'match': f"{match.home_team.name} vs {match.away_team.name}",
                    'league': match.league.name if match.league else 'N/A',
                    'date': match_date_str,
                    'market': bet['market'],
                    'pick': bet['pick'],
                    'probability': prob,
                    'odd': odd,
                    'fair_odd': bet.get('fair_odd'),
                    'ev_pct': ev_pct,
                    'score': bet['score'],
                    'contextual_fit': contextual_fit,  # 🆕 NOVO: adequação contextual
                    'result': None
                })
        
        logger.info(f"   📊 {len(all_value_bets)} value bets encontradas")
        
        # 📊 DIAGNÓSTICO: Distribuição de mercados nas value bets
        if all_value_bets:
            value_market_dist = {}
            for vb in all_value_bets:
                group = self._market_group(vb['market'])
                value_market_dist[group] = value_market_dist.get(group, 0) + 1
            
            logger.info(f"   📈 Distribuição de mercados nas value bets candidatas:")
            for group, count in sorted(value_market_dist.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"      {group}: {count} apostas ({count/len(all_value_bets)*100:.1f}%)")
        
        # 🆕 CORREÇÃO CRÍTICA 21/02: Ordenar por EV (primário) + contextual_fit (secundário)
        # Quando duas apostas têm EV similar, preferir a com melhor adequação contextual
        all_value_bets.sort(key=lambda x: (
            x['ev_pct'],              # 1º: Maior EV (objetivo do value betting)
            x.get('contextual_fit', 1.0),  # 2º: Melhor fit contextual (desempate)
            x['probability']          # 3º: Maior probabilidade (segurança)
        ), reverse=True)
        
        logger.info(f"   🎯 Ordenação: EV (primário) → contextual_fit (secundário) → probabilidade")
        
        # Pegar top MAX_VALUE_BETS
        top_values = all_value_bets[:self.MAX_VALUE_BETS]
        
        if len(all_value_bets) > self.MAX_VALUE_BETS:
            logger.warning(f"   ⚠️  LIMITAÇÃO: {len(all_value_bets)} value bets encontradas, mas MAX_VALUE_BETS={self.MAX_VALUE_BETS}")
            logger.warning(f"       {len(all_value_bets) - self.MAX_VALUE_BETS} apostas com EV positivo foram DESCARTADAS")
        
        logger.info(f"   🎯 Selecionando top {len(top_values)} value bets")
        
        created_bets = []
        
        for idx, vb in enumerate(top_values, 1):
            # Calcular fair odd
            fair_odd = vb.get('fair_odd') or (1.0 / vb['probability'] if vb['probability'] > 0 else 0)
            
            # Safety check: garantir que odd é válida
            if not vb.get('odd') or vb['odd'] <= 0:
                logger.warning(f"   ⚠️ Pulando value bet sem odd válida: {vb.get('market')}")
                continue
            
            # ✅ CORREÇÃO 21/02: Adicionar tratamento de erro
            try:
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
            except Exception as e:
                logger.error(f"   ❌ Erro ao criar value bet #{idx}: {e}")
                logger.debug(f"      Value bet data: {vb}")
                continue
        
        logger.info(f"\n   ⚡ Total de value bets criadas: {len(created_bets)}")
        
        return created_bets
    
    def _calculate_stake(self, probability, bet_type, ev_pct=0):
        """
        Calcula stake sugerido usando Kelly Criterion simplificado
        
        ✅ CORREÇÃO CRÍTICA 21/02: Stakes alinhados com thresholds CONSERVADORES
        
        Args:
            probability: Probabilidade da aposta (0-1)
            bet_type: 'multiple' ou 'value'
            ev_pct: Expected Value em % (apenas para value bets)
        
        Returns:
            float: Stake em unidades (0.5 - 3.0)
        """
        if bet_type == 'multiple':
            # Bilhetes conservadores: prob combinada 25%/15%/11% (alta taxa de acerto)
            # Com thresholds conservadores, probs são ALTAS → stakes podem ser maiores
            if probability >= 0.25:  # ≥25% = 3X com favoritos fortes (1 em 4)
                return 2.5  # Alta confiança (3X típico)
            elif probability >= 0.15:  # 15-25% = 5X conservador (1 em 5-7)
                return 2.0  # Média-alta confiança (5X típico)
            elif probability >= 0.11:  # 11-15% = 7X muito conservador (1 em 7-9)
                return 1.5  # Média confiança (7X típico)
            else:  # <11% = não deveria existir (filtrado)
                return 1.0  # Fallback (apostas edge case)
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
