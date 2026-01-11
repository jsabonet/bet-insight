"""
DTO mínimo para explicação da IA
Garante que a IA recebe APENAS o necessário
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ModelSummary:
    """Resumo do modelo estatístico"""
    xg_home: float
    xg_away: float
    likely_score: str
    home_win_prob: float
    draw_prob: float
    away_win_prob: float


@dataclass
class AIExplanationRequest:
    """
    DTO MÍNIMO para IA - APENAS explicação
    
    ⚠️ A IA NÃO DEVE receber:
    - Estatísticas brutas
    - Odds completas
    - Históricos longos
    - Qualquer dado que permita "re-decidir"
    """
    # Identificação
    match: str  # "Team A vs Team B"
    league: str
    
    # Decisão JÁ TOMADA (determinística)
    market: str  # "Match Winner", "Over/Under 2.5", etc
    pick: str  # "Home Win", "Over 2.5", etc
    probability: float  # 0.0 - 1.0
    
    # Value e risco
    market_odd: float
    fair_odd: float
    value_pct: float
    risk: str  # "low", "medium", "high"
    confidence: int  # 1-5 stars
    
    # Contexto mínimo
    key_factors: List[str]  # Máximo 5 fatores principais
    risk_factors: List[str]  # Máximo 3 riscos
    
    # Resumo do modelo (não dados brutos)
    model_summary: ModelSummary
    
    def to_prompt_dict(self) -> dict:
        """Converte para dicionário otimizado para prompt"""
        return {
            'match': self.match,
            'league': self.league,
            'market': self.market,
            'pick': self.pick,
            'probability': f"{self.probability * 100:.1f}%",
            'market_odd': f"{self.market_odd:.2f}",
            'fair_odd': f"{self.fair_odd:.2f}",
            'value': f"{self.value_pct:.1f}%",
            'risk': self.risk.upper(),
            'confidence': '⭐' * self.confidence,
            'key_factors': self.key_factors[:5],  # Máx 5
            'risk_factors': self.risk_factors[:3],  # Máx 3
            'xg_home': f"{self.model_summary.xg_home:.2f}",
            'xg_away': f"{self.model_summary.xg_away:.2f}",
            'likely_score': self.model_summary.likely_score,
            'home_win': f"{self.model_summary.home_win_prob * 100:.1f}%",
            'draw': f"{self.model_summary.draw_prob * 100:.1f}%",
            'away_win': f"{self.model_summary.away_win_prob * 100:.1f}%"
        }


@dataclass
class AIExplanationResponse:
    """Resposta PADRONIZADA da IA"""
    summary: str  # 1 frase (máx 150 chars)
    bullets: List[str]  # 3-5 bullets técnicos
    risk_warning: str  # 1 frase sobre risco
    
    def validate(self) -> bool:
        """Valida formato da resposta"""
        if not self.summary or len(self.summary) > 150:
            return False
        if len(self.bullets) < 3 or len(self.bullets) > 5:
            return False
        if not self.risk_warning or len(self.risk_warning) > 100:
            return False
        return True
    
    def to_html(self) -> str:
        """Converte para HTML formatado"""
        bullets_html = '\n'.join([f'<li>{bullet}</li>' for bullet in self.bullets])
        return f"""
<div class="ai-explanation">
    <p class="summary"><strong>{self.summary}</strong></p>
    <ul class="factors">
        {bullets_html}
    </ul>
    <p class="risk"><strong>⚠️ Risco:</strong> {self.risk_warning}</p>
</div>
"""
