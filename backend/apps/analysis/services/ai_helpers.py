"""
Funções auxiliares para AI Analyzer
Parse, validação e formatação de respostas da IA
"""
from typing import Dict, List
import re
import logging

logger = logging.getLogger(__name__)


def parse_and_validate_response(text: str) -> Dict:
    """
    Parse SIMPLIFICADO para formato decisório
    O Gemini já está retornando o formato correto, só precisamos extrair
    """
    try:
        # Detectar formato multi-mercado
        is_multi = ('ANÁLISE COMPLETA DE APOSTAS' in text) or ('ONDE APOSTAR' in text) or ('APOSTA #1' in text)

        # Se é multi-mercado, aceitar diretamente
        if is_multi:
            recommendation = text.strip()
            risk_lines = [line for line in text.split('\n') if 'risco' in line.lower() or 'stake' in line.lower()]
            risk_warning = ' '.join(risk_lines[-2:]) if risk_lines else "Risco conforme análise"
            return {
                'valid': True,
                'recommendation': recommendation,
                'bullets': [],
                'risk_warning': risk_warning[:200]
            }

        # Caso contrário, verificar formato decisório simples
        has_recommendation = '📌' in text and ('Mercado' in text or 'Pick' in text)
        has_decision = 'DECISÃO' in text.upper() and ('APOSTAR' in text.upper() or 'SEM APOSTA' in text.upper())
        
        if not (has_recommendation or has_decision):
            logger.warning(f"⚠️ Formato não detectado no texto")
            return {'valid': False}
        
        # Extrair recomendação (decisório simples): tudo até seção de justificativa
        recommendation = ''
        if '🎯' in text:
            parts = text.split('📊')
            if parts:
                recommendation = parts[0].strip()
        
        # Extrair bullets (linhas com ✓)
        bullets = [line.strip().lstrip('✓').strip() for line in text.split('\n') if line.strip().startswith('✓')]
        if not bullets:
            bullets = [line.strip() for line in text.split('\n') if line.strip().startswith('•')]
        
        # Extrair risco (última seção com Risco ou Stake)
        risk_lines = [line for line in text.split('\n') if 'risco' in line.lower() or 'stake' in line.lower()]
        risk_warning = ' '.join(risk_lines[-2:]) if risk_lines else "Risco conforme análise"
        
        return {
            'valid': True,
            'recommendation': recommendation if recommendation else text[:300],
            'bullets': bullets if bullets else ["Análise baseada em dados estatísticos"],
            'risk_warning': risk_warning[:200]
        }
        
    except Exception as e:
        logger.error(f"Erro ao parsear resposta da IA: {e}")
        return {'valid': False}


def format_analysis_for_frontend(recommendation: str, bullets: List[str], risk_warning: str) -> str:
    """
    Formata análise DECISÓRIA para frontend
    Formato: DECISÃO → JUSTIFICATIVA → RISCO → INVALIDAÇÃO
    """
    # Se já é um texto completo multi-mercado, retornar como está
    if ('ANÁLISE COMPLETA DE APOSTAS' in recommendation) or ('ONDE APOSTAR' in recommendation) or ('APOSTA #1' in recommendation):
        return recommendation

    # Caso contrário, aplicar formatação decisória simples
    bullets_formatted = '\n'.join([f'✓ {b}' for b in bullets])
    formatted = f"""
═══════════════════════════════════════
🎯 RECOMENDAÇÃO DE APOSTA
═══════════════════════════════════════

{recommendation}

═══════════════════════════════════════
📊 JUSTIFICATIVA TÉCNICA
═══════════════════════════════════════

{bullets_formatted}

═══════════════════════════════════════
⚠️ RISCO & GESTÃO DE BANCA
═══════════════════════════════════════

{risk_warning}
"""
    return formatted
