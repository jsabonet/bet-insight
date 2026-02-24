import logging
from datetime import datetime
from typing import Dict

from apps.matches.models import Match
from .match_enricher import MatchDataEnricher
from .feature_engineer import FeatureEngineer
from .ml_integration import ModelEnsembleML
from .decision_engine import DecisionEngine
from .ai_analyzer import AIAnalyzer
from .context_analyzer import ContextAnalyzer  # NOVO
from .market_selector import MarketSelector    # NOVO
from .hybrid_strategy import HybridStrategy    # ESTRATEGIA ADAPTATIVA

logger = logging.getLogger(__name__)


class HybridAnalysisOrchestrator:
    """Coordena o fluxo híbrido: enriquecimento → features → contexto → modelos ML → seleção contextual → decisão → IA."""

    def __init__(self, enable_cup_adjustment: bool = True):
        self.enricher = MatchDataEnricher()
        self.fe = FeatureEngineer()
        self.context_analyzer = ContextAnalyzer()  # NOVO
        self.ensemble = ModelEnsembleML()  # 🤖 USANDO ML TREINADO
        self.market_selector = MarketSelector()    # NOVO
        self.hybrid_strategy = HybridStrategy()    # ESTRATEGIA HIBRIDA
        self.decision = DecisionEngine()
        self.ai = AIAnalyzer()
        self.enable_cup_adjustment = enable_cup_adjustment  # Flag global para ativar/desativar ajuste de copas

    def run(self, match: Match, strategy: str = 'value') -> Dict:
        """Executa a análise híbrida e retorna payload pronto para persistir/exibir.
        
        Args:
            match: Match object do banco de dados
            strategy: 'value' (apostas simples, EV máximo) ou 'multiple' (bilhetes, probabilidade alta)
        """
        if not match.api_football_id:
            raise ValueError("Partida sem API Football ID para enriquecimento.")

        logger.info(f"🎯 [Orchestrator] Executando análise com estratégia: {strategy.upper()}")

        # 1) Enriquecer dados
        match_data = {
            'api_id': match.api_football_id,
        }
        enriched = self.enricher.enrich(match_data)

        # 2) Feature engineering
        features = self.fe.engineer_all_features(enriched)
        
        # LOG: Features geradas
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 [Orchestrator] FEATURES GERADAS - Resumo por Categoria")
        logger.info(f"{'='*80}")
        total_features = 0
        for category, category_features in features.items():
            count = len(category_features)
            total_features += count
            logger.info(f"   {category.upper()}: {count} features")
            # Log primeiras 3 features de cada categoria
            for i, (key, value) in enumerate(list(category_features.items())[:3]):
                logger.info(f"      - {key}: {value}")
            if count > 3:
                logger.info(f"      ... (+{count-3} features)")
        logger.info(f"\n   TOTAL: {total_features} features geradas")
        logger.info(f"{'='*80}\n")

        # 2.5) NOVO: Análise contextual
        context_analysis = self.context_analyzer.analyze(features)
        logger.info(f"🔍 [Orchestrator] Padrões contextuais detectados: {len(context_analysis.get('patterns', []))}")
        for pattern in context_analysis.get('patterns', []):
            logger.info(f"   - {pattern['name']}: {pattern['confidence']:.0%}")
        
        # 2.6) ESTRATÉGIA HÍBRIDA: Decidir se usa contexto ou não
        context_decision = self.hybrid_strategy.should_use_context(context_analysis, features)
        
        if not context_decision['use_context']:
            # Contexto rejeitado - limpar para não influenciar modelos
            logger.info(f"⚠️ [Orchestrator] Contexto REJEITADO - usando modelo base")
            context_analysis = {'patterns': [], 'top_markets': []}
        else:
            logger.info(f"✅ [Orchestrator] Contexto APROVADO - padrões: {', '.join(context_decision['approved_patterns'])}")

        # 3) Modelos estatísticos
        strength = features.get('strength', {})
        weather = features.get('weather', {})
        competition = features.get('competition', {})  # NOVO: features de competição
        home_strength = strength.get('home_goals_per_game', 1.2)
        away_strength = strength.get('away_goals_per_game', 1.2)
        weather_impact = weather.get('goal_impact', 0.0)
        
        # PROTEÇÃO: Garantir que ligas NUNCA sejam afetadas
        is_cup = competition.get('is_cup_competition', False)
        knockout_adjustment_raw = competition.get('knockout_adjustment_factor', 1.0)
        
        # VALIDAÇÃO TRIPLA DE SEGURANÇA:
        # 1. Flag global do orchestrator
        # 2. Competição deve ser copa
        # 3. Fator deve ser menor que 1.0
        if self.enable_cup_adjustment and is_cup and knockout_adjustment_raw < 1.0:
            knockout_adjustment = knockout_adjustment_raw
            logger.info(f"✅ [Orchestrator] AJUSTE DE COPA ATIVO")
        else:
            knockout_adjustment = 1.0  # FORÇAR 1.0 para ligas (SEM ALTERAÇÃO)
            if is_cup and not self.enable_cup_adjustment:
                logger.info(f"⚠️ [Orchestrator] Copa detectada mas ajuste DESATIVADO por configuração")
        
        # LOG: Features críticas para modelos
        logger.info(f"🔧 [Orchestrator] FEATURES CRÍTICAS PARA ENSEMBLE:")
        logger.info(f"   Home Strength: {home_strength:.2f} gols/jogo")
        logger.info(f"   Away Strength: {away_strength:.2f} gols/jogo")
        logger.info(f"   Weather Impact: {weather_impact:.2f}")
        logger.info(f"   League ID: {match.league.api_football_id if match.league else 'N/A'}")
        logger.info(f"   Tipo Competição: {'COPA' if is_cup else 'LIGA'}")
        logger.info(f"   Knockout Adjustment: {knockout_adjustment:.2f} {'(ATIVO)' if knockout_adjustment < 1.0 else '(INATIVO - Liga ou desabilitado)'}")
        if knockout_adjustment < 1.0:
            logger.info(f"      🏆 Fase: {competition.get('round_stage', 'N/A')}")
            logger.info(f"      📉 Redução xG: {(1.0 - knockout_adjustment) * 100:.0f}%")
        
        # Obter league_id para calibração específica
        league_id = match.league.api_football_id if match.league else None

        ensemble_result = self.ensemble.predict(features, home_strength, away_strength, weather_impact, league_id,
                                               knockout_adjustment=knockout_adjustment,
                                               context_analysis=context_analysis)  # NOVO: passar contexto
        
        # LOG: Resultado do Ensemble
        logger.info(f"\n{'='*80}")
        logger.info(f"🎲 [Orchestrator] RESULTADO DO ENSEMBLE")
        logger.info(f"{'='*80}")
        consensus = ensemble_result.get('consensus', {})
        logger.info(f"   Consensus:")
        logger.info(f"      Home: {consensus.get('home_win', 0)*100:.1f}%")
        logger.info(f"      Draw: {consensus.get('draw', 0)*100:.1f}%")
        logger.info(f"      Away: {consensus.get('away_win', 0)*100:.1f}%")
        
        poisson_probs = ensemble_result.get('poisson', {}).get('probabilities', {})
        logger.info(f"   Poisson 1X2:")
        logger.info(f"      Home: {poisson_probs.get('home_win', 0)*100:.1f}%")
        logger.info(f"      Draw: {poisson_probs.get('draw', 0)*100:.1f}%")
        logger.info(f"      Away: {poisson_probs.get('away_win', 0)*100:.1f}%")
        
        logistic_probs = ensemble_result.get('logistic', {})
        if logistic_probs:
            logger.info(f"   Logística 1X2:")
            logger.info(f"      Home: {logistic_probs.get('home_win', 0)*100:.1f}%")
            logger.info(f"      Draw: {logistic_probs.get('draw', 0)*100:.1f}%")
            logger.info(f"      Away: {logistic_probs.get('away_win', 0)*100:.1f}%")
        
        market_probs = ensemble_result.get('market', {})
        if market_probs:
            logger.info(f"   Market Prior:")
            logger.info(f"      Home: {market_probs.get('home_win', 0)*100:.1f}%")
            logger.info(f"      Draw: {market_probs.get('draw', 0)*100:.1f}%")
            logger.info(f"      Away: {market_probs.get('away_win', 0)*100:.1f}%")
        logger.info(f"{'='*80}\n")

        # 4) Decisão + value
        # ✅ CORREÇÃO 15/02/2026: Passar TODAS as odds extraídas (44 mercados)
        # Antes: Passava apenas 7 mercados básicos (home, draw, away, over/under 2.5, btts)
        # Agora: Passa todos os 44 mercados da expansão de odds
        raw_odds = enriched.get('odds', {})
        if raw_odds and raw_odds.get('home_win'):
            # Passar TODAS as odds extraídas (não apenas subset)
            market_odds = raw_odds.copy()  # Usar todas as odds do enricher
            logger.info(f"💰 [Orchestrator] Market odds preparados: {len(market_odds)} mercados")
            logger.info(f"   Principais: Home={market_odds.get('home_win')}, Draw={market_odds.get('draw')}, Away={market_odds.get('away_win')}")
        else:
            # Sem odds da API - DecisionEngine não gerará top_bets
            market_odds = None
            logger.warning(f"⚠️ [Orchestrator] Sem odds disponíveis - top_bets será vazio")
        
        # NOVO: Passar context_analysis para DecisionEngine
        decision_result = self.decision.make_decision(
            ensemble_result, 
            features, 
            market_odds, 
            strategy=strategy,
            context_analysis=context_analysis  # NOVO
        )
        
        # LOG: Resultado do Decision Engine
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 [Orchestrator] DECISION ENGINE - Top Bets Geradas")
        logger.info(f"{'='*80}")
        top_bets = decision_result.get('top_bets', [])
        logger.info(f"   Total de apostas: {len(top_bets)}")
        for i, bet in enumerate(top_bets[:5], 1):
            logger.info(f"   #{i}: {bet.get('market_display', 'N/A')}")
            logger.info(f"      Probability: {bet.get('probability', 0)*100:.1f}%")
            market_odd = bet.get('market_odd', 0) or 0  # Tratar None como 0
            logger.info(f"      Market Odd: {market_odd:.2f}")
            logger.info(f"      Fair Odd: {bet.get('fair_odd', 0):.2f}")
            logger.info(f"      EV: {bet.get('ev_pct', 0):+.1f}%")
            logger.info(f"      Stake: {bet.get('stake', 0):.1f}u")
        
        recommendation = decision_result.get('recommendation', {})
        logger.info(f"\n   Recomendação Principal: {recommendation.get('market_display', 'N/A')}")
        logger.info(f"      Probability: {recommendation.get('probability', 0)*100:.1f}%")
        logger.info(f"      Fair Odd: {recommendation.get('fair_odd', 0):.2f}")
        
        publish_filter = decision_result.get('publish_filter', {})
        logger.info(f"\n   Filtro de Publicação:")
        logger.info(f"      Should Publish: {publish_filter.get('should_publish', True)}")
        logger.info(f"      Reason: {publish_filter.get('reason', 'N/A')}")
        logger.info(f"{'='*80}\n")
        
        # Log para confirmar top_bets
        top_bets = decision_result.get('top_bets', [])
        logger.info(f"✅ [Orchestrator] DecisionEngine retornou {len(top_bets)} top_bets com estratégia {strategy}")
        # LOG para confirmar top_bets (remover duplicado abaixo)
        if top_bets:
            for i, bet in enumerate(top_bets, 1):
                logger.info(f"   #{i}: {bet.get('market_display')} - Prob: {bet.get('probability', 0)*100:.1f}%, EV: {bet.get('ev_pct', 0):+.1f}%")

        # 5) ENRIQUECER enriched com features e context para AI Analyzer
        # O AI Analyzer precisa ter acesso a TODAS as features para seleção contextual precisa
        enriched['features_summary'] = features  # Adicionar todas as features (form, injuries, motivation, etc)
        enriched['context_analysis'] = context_analysis  # Adicionar padrões contextuais detectados
        logger.info(f"📦 [Orchestrator] Enriched data preparado para AI com {len(features)} categorias de features")
        
        # 6) IA explica (opcional) - agora com features completas
        ai_result = self.ai.explain_decision(decision_result, enriched, strategy=strategy)
        
        # LOG: AI Analysis
        logger.info(f"\n{'='*80}")
        logger.info(f"🤖 [Orchestrator] AI ANALYSIS")
        logger.info(f"{'='*80}")
        if ai_result.get('success'):
            logger.info(f"   Status: ✅ Sucesso")
            logger.info(f"   Análise gerada: {len(ai_result.get('analysis', ''))} caracteres")
        else:
            logger.info(f"   Status: ❌ Falha")
            logger.info(f"   Erro: {ai_result.get('error', 'N/A')}")
        logger.info(f"{'='*80}\n")

        # 7) Formatar saída
        consensus = ensemble_result.get('consensus', {})
        poisson = ensemble_result.get('poisson', {})
        fair_odds = decision_result.get('fair_odds', {})
        recommendation = decision_result.get('recommendation', {})
        confidence = decision_result.get('confidence', {})
        risk = decision_result.get('risk', 'medium')

        # Determinar predição 1X2 baseada no CONSENSO (não na recomendação)
        if consensus:
            max_outcome = max(consensus.items(), key=lambda x: x[1])
            logger.info(f"🎯 [DEBUG] Consensus max: {max_outcome[0]} = {max_outcome[1]*100:.1f}%")
            market_to_prediction = {
                'home_win': 'home',
                'draw': 'draw',
                'away_win': 'away',
            }
            prediction_choice = market_to_prediction.get(max_outcome[0], 'home')
            logger.info(f"🎯 [DEBUG] Prediction choice: {prediction_choice}")
        else:
            logger.warning(f"⚠️ [DEBUG] Consensus vazio! Usando fallback 'home'")
            prediction_choice = 'home'  # fallback seguro

        # Confiança int (1-5)
        confidence_int = int(confidence.get('stars', 3))

        # Texto de raciocínio
        if ai_result.get('success'):
            reasoning_text = ai_result.get('analysis')
        else:
            reasoning_text = (
                "1️⃣ CONSENSO DOS MODELOS: Probabilidades combinadas indicam "
                f"{recommendation.get('market_display', 'resultado')} com {recommendation.get('probability', 0)*100:.1f}%.\n"
                "2️⃣ EXPECTED GOALS (xG): Jogo com xG baixo, favorecendo mercados conservadores.\n"
                "3️⃣ ODDS: Sem value bets significativos; mercado alinhado às probabilidades.\n"
                f"4️⃣ RISCO: {risk.upper()} — gestão de banca recomendada."
            )

        key_factors = [
            f"Consenso: H {consensus.get('home_win', 0)*100:.1f}% / D {consensus.get('draw', 0)*100:.1f}% / A {consensus.get('away_win', 0)*100:.1f}%",
            f"xG: Casa {poisson.get('expected_goals', {}).get('home', 0):.2f} / Fora {poisson.get('expected_goals', {}).get('away', 0):.2f}",
            f"Odds Justas: H {fair_odds.get('home_win', 0):.2f} / D {fair_odds.get('draw', 0):.2f} / A {fair_odds.get('away_win', 0):.2f}",
        ]

        analysis_data = {
            'consensus': consensus,
            'poisson': poisson,
            'fair_odds': fair_odds,
            'recommendation': recommendation,
            'confidence': confidence,
            'risk': risk,
            'value_bets': decision_result.get('value_bets', []),  # DEPRECATED: Mantido para compatibilidade
            'top_bets': decision_result.get('top_bets', []),  # NOVO: Top bets com estrutura completa
            'market_odds': market_odds,
            'publish_filter': decision_result.get('publish_filter', {}),  # NOVO: Filtro de confiança
            'features_summary': {
                'strength': strength,
                'weather': weather,
            },
        }
        
        # Flag para indicar se a previsão deve ser exibida (alta qualidade)
        publish_filter = decision_result.get('publish_filter', {})
        should_publish = publish_filter.get('should_publish', True)

        return {
            'prediction': prediction_choice,
            'confidence': confidence_int,
            'home_probability': round(consensus.get('home_win', 0) * 100, 1),
            'draw_probability': round(consensus.get('draw', 0) * 100, 1),
            'away_probability': round(consensus.get('away_win', 0) * 100, 1),
            'home_xg': round(poisson.get('expected_goals', {}).get('home', 0), 2),
            'away_xg': round(poisson.get('expected_goals', {}).get('away', 0), 2),
            'reasoning': reasoning_text,
            'key_factors': key_factors,
            'analysis_data': analysis_data,
            'should_publish': should_publish,  # NOVO: Flag de qualidade
        }
