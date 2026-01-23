import logging
from datetime import datetime
from typing import Dict

from apps.matches.models import Match
from .match_enricher import MatchDataEnricher
from .feature_engineer import FeatureEngineer
from .statistical_models import ModelEnsemble
from .decision_engine import DecisionEngine
from .ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)


class HybridAnalysisOrchestrator:
    """Coordena o fluxo híbrido: enriquecimento → features → modelos → decisão → IA (explicação)."""

    def __init__(self):
        self.enricher = MatchDataEnricher()
        self.fe = FeatureEngineer()
        self.ensemble = ModelEnsemble()
        self.decision = DecisionEngine()
        self.ai = AIAnalyzer()

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

        # 3) Modelos estatísticos
        strength = features.get('strength', {})
        weather = features.get('weather', {})
        home_strength = strength.get('home_goals_per_game', 1.2)
        away_strength = strength.get('away_goals_per_game', 1.2)
        weather_impact = weather.get('goal_impact', 0.0)
        
        # Obter league_id para calibração específica
        league_id = match.league.api_football_id if match.league else None

        ensemble_result = self.ensemble.predict(features, home_strength, away_strength, weather_impact, league_id)

        # 4) Decisão + value
        # Preparar market_odds no formato correto para o DecisionEngine
        # O enricher retorna odds em enriched['odds'], não em features['market']
        raw_odds = enriched.get('odds', {})
        if raw_odds and raw_odds.get('home_win'):
            # Converter formato do enricher para formato do DecisionEngine
            market_odds = {
                'home': raw_odds.get('home_win'),
                'draw': raw_odds.get('draw'),
                'away': raw_odds.get('away_win'),
                'over_2_5': raw_odds.get('over_25'),
                'under_2_5': raw_odds.get('under_25'),
                'btts_yes': raw_odds.get('btts_yes'),
                'btts_no': raw_odds.get('btts_no'),
            }
            logger.info(f"💰 [Orchestrator] Market odds preparados: Home={market_odds.get('home')}, Draw={market_odds.get('draw')}, Away={market_odds.get('away')}")
        else:
            # Sem odds da API - DecisionEngine não gerará top_bets
            market_odds = None
            logger.warning(f"⚠️ [Orchestrator] Sem odds disponíveis - top_bets será vazio")
        
        decision_result = self.decision.make_decision(ensemble_result, features, market_odds, strategy=strategy)
        
        # Log para confirmar top_bets
        top_bets = decision_result.get('top_bets', [])
        logger.info(f"✅ [Orchestrator] DecisionEngine retornou {len(top_bets)} top_bets com estratégia {strategy}")
        if top_bets:
            for i, bet in enumerate(top_bets, 1):
                logger.info(f"   #{i}: {bet.get('market_display')} - Prob: {bet.get('probability', 0)*100:.1f}%, EV: {bet.get('ev_pct', 0):+.1f}%")

        # 5) IA explica (opcional)
        ai_result = self.ai.explain_decision(decision_result, enriched)

        # 6) Formatar saída
        consensus = ensemble_result.get('consensus', {})
        poisson = ensemble_result.get('poisson', {})
        fair_odds = decision_result.get('fair_odds', {})
        recommendation = decision_result.get('recommendation', {})
        confidence = decision_result.get('confidence', {})
        risk = decision_result.get('risk', 'medium')

        # Mapear predição para choices
        market_to_prediction = {
            'home_win': 'home',
            'draw': 'draw',
            'away_win': 'away',
        }
        prediction_choice = market_to_prediction.get(recommendation.get('market'), 'home')

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
