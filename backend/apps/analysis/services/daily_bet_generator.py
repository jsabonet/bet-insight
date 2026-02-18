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
from .api_football_service import APIFootballService
from apps.matches.services.football_api import FootballAPIService

logger = logging.getLogger(__name__)


class DailyBetGenerator:
    """Gera bilhetes múltiplos e value bets diários automaticamente"""
    
    # Configurações de filtros
    MIN_VALUE_EV = 5.0  # EV mínimo para value bets (+5%)
    MIN_VALUE_PROBABILITY = 0.25  # Probabilidade mínima para value bets (25%)
    
    # ✅ CORRIGIDO 17/02/2026: Thresholds ajustados para maior acertividade
    # Probabilidades mínimas individuais por tamanho de bilhete (para 50%+ de acerto)
    MIN_MULTIPLE_PROBABILITY_3X = 0.80  # 3x: cada aposta ≥80% (prob combinada ~51%)
    MIN_MULTIPLE_PROBABILITY_5X = 0.87  # 5x: cada aposta ≥87% (prob combinada ~50%)
    MIN_MULTIPLE_PROBABILITY_7X = 0.91  # 7x: cada aposta ≥91% (prob combinada ~52%)
    
    # Probabilidades combinadas mínimas (todas ajustadas para ≥50%)
    MIN_COMBINED_PROBABILITY_3X = 0.50  # 50% (era 15%)
    MIN_COMBINED_PROBABILITY_5X = 0.50  # 50% (era 8%)
    MIN_COMBINED_PROBABILITY_7X = 0.50  # 50% (era 4%)
    
    # Range de odds para bilhetes (odds baixas = alta probabilidade)
    MIN_ODD_MULTIPLE = 1.10  # Odd mínima individual (prob ~91%)
    MAX_ODD_MULTIPLE = 1.50  # Odd máxima individual (prob ~67%)
    
    MIN_TICKET_ODD = 1.80  # Odd mínima total do bilhete (reduzido de 2.0)
    MAX_TICKET_ODD = 15.0  # Odd máxima total do bilhete (reduzido de 20.0)
    
    # Filtros de qualidade e contexto
    MIN_CONFIDENCE_STARS = 4  # Confiança mínima (4-5 estrelas)
    MAX_DRAW_PROBABILITY = 0.35  # Empate máximo aceitável (35%)
    ALLOWED_RISK_LEVELS = ['low', 'medium']  # Apenas risco baixo/médio
    MIN_ABSOLUTE_FORM = 1.5  # Forma mínima absoluta (50% = 1.5/3.0 pontos) - previne apostas em times com má forma
    
    MAX_VALUE_BETS = 10  # Máximo de value bets por dia
    
    # Configuração do sistema híbrido de busca
    SEARCH_MODE = 'hybrid'  # 'priority', 'all', 'hybrid'
    MIN_MATCHES_THRESHOLD = 15  # Se encontrar menos, expande busca
    MAX_TOTAL_MATCHES = 100  # Limite absoluto de partidas a analisar (aumentado para maior cobertura)
    
    # IDs das ligas prioritárias (alta qualidade)
    PRIORITY_LEAGUES = [
        # Europa - Top 5
        39,   # Premier League (Inglaterra)
        140,  # La Liga (Espanha)
        135,  # Serie A (Itália)
        78,   # Bundesliga (Alemanha)
        61,   # Ligue 1 (França)
        # Europa - Secundárias
        94,   # Primeira Liga (Portugal)
        88,   # Eredivisie (Holanda)
        144,  # Jupiler Pro League (Bélgica)
        203,  # Süper Lig (Turquia)
        179,  # Championship (Inglaterra)
        # Competições Internacionais
        2,    # UEFA Champions League
        3,    # UEFA Europa League
        848,  # UEFA Conference League
        # Copas Nacionais
        45,   # FA Cup (Inglaterra)
        137,  # Copa del Rey (Espanha)
        # América do Sul
        71,   # Brasileirão Série A
        73,   # Brasileirão Série B
        128,  # Liga Profesional (Argentina)
        325,  # Copa Libertadores
        # América do Norte
        253,  # MLS (EUA)
        # África
        317,  # DSTV Premiership (África do Sul)
        # Ásia
        188,  # J1 League (Japão)
    ]
    
    def __init__(self):
        self.orchestrator = HybridAnalysisOrchestrator()
        self.api = APIFootballService()
        self.football_api = FootballAPIService()  # Service para buscar fixtures
        self.api_calls = 0
        self.cache_hits = 0
        self.execution = None  # TaskExecution instance para tracking de progresso
    
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
                log_message=f'Iniciando análise de {max_matches} partidas...'
            )
        
        analyses = []
        
        for idx, fixture in enumerate(fixtures_to_analyze, 1):
            try:
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
            
            # Gerar value bets individuais
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
            'analyzed_matches': analyzed_matches_list
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
            result = analysis['multiple_result']
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
                # 2. Odd na faixa conservadora (1.10 - 1.50)
                # 3. EV não muito negativo (>= -15%)
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
                
                for bet in top_bets:
                    prob = bet.get('probability', 0)
                    odd = bet.get('market_odd', 0)
                    ev_pct = bet.get('ev_pct', 0)
                    
                    # Filtros conservadores para bilhetes múltiplos
                    if (prob >= 0.80 and  # Mínimo base de 80%
                        self.MIN_ODD_MULTIPLE <= odd <= self.MAX_ODD_MULTIPLE and 
                        ev_pct >= -15):  # EV um pouco mais permissivo
                        best_bet = bet
                        break
                
                if not best_bet:
                    logger.debug(f"   ⏩ Pulando {home_team} vs {away_team}: nenhuma aposta atende critérios de bilhete")
                    continue

                logger.info(f"   🎯 Seleção Bilhete: {best_bet['market']} ({best_bet['pick']}) - {best_bet['probability']*100:.0f}% @ {best_bet['market_odd']:.2f}")
                if 'post_reason' in best_bet:
                    logger.info(f"      Razão: {best_bet['post_reason']}")

                all_bets.append({
                    'fixture_id': fixture_id,
                    'match': f"{home_team} vs {away_team}",
                    'league': league_name,
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
            
            # Pegar top N apostas elegíveis
            selections = eligible_bets[:size]
            
            # Calcular odd total e probabilidade combinada
            total_odd = 1.0
            combined_prob = 1.0
            
            for sel in selections:
                total_odd *= sel['odd']
                combined_prob *= sel['probability']
            
            # Filtro: probabilidade combinada
            if combined_prob < min_combined_prob:
                logger.info(f"   ⏩ Bilhete {size}x: prob combinada {combined_prob*100:.2f}% < {min_combined_prob*100:.0f}%")
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
                odd = bet.get('market_odd')
                
                # Pular apostas sem odd disponível
                if odd is None or odd == 0:
                    continue
                
                # Filtros
                if ev_pct < self.MIN_VALUE_EV:
                    continue
                
                if prob < self.MIN_VALUE_PROBABILITY:
                    continue
                
                # match_date pode ser string ou datetime - normalizar
                match_date_str = match.match_date if isinstance(match.match_date, str) else match.match_date.isoformat()
                
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
            
            # Safety check: garantir que odd é válida
            if not vb.get('odd') or vb['odd'] <= 0:
                logger.warning(f"   ⚠️ Pulando value bet sem odd válida: {vb.get('market')}")
                continue
            
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
