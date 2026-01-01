"""
Teste de extração de probabilidades
"""
import re

def test_extraction(analysis_text, home_name, away_name):
    """Testa a extração de probabilidades"""
    
    # Extrair nomes dos times
    home_prob = None
    draw_prob = None
    away_prob = None
    
    # Tentar extrair probabilidades de forma mais inteligente
    text_lower = analysis_text.lower()
    
    # Padrão 1: Nome do time seguido de probabilidade (ignora emojis e símbolos)
    home_pattern = rf'[^\w]*{re.escape(home_name.lower())}[:\s]*(\d+)%'
    away_pattern = rf'[^\w]*{re.escape(away_name.lower())}[:\s]*(\d+)%'
    
    home_match = re.search(home_pattern, text_lower)
    away_match = re.search(away_pattern, text_lower)
    
    if home_match:
        home_prob = int(home_match.group(1))
        print(f"✅ {home_name}: {home_prob}% (Padrão 1)")
    if away_match:
        away_prob = int(away_match.group(1))
        print(f"✅ {away_name}: {away_prob}% (Padrão 1)")
    
    # Procurar por "Empate" com probabilidade (ignora emojis)
    draw_match = re.search(r'[^\w]*empate[:\s]*(\d+)%', text_lower)
    if draw_match:
        draw_prob = int(draw_match.group(1))
        print(f"✅ Empate: {draw_prob}% (Padrão 1)")
    
    # Se não encontrou, procurar BLOCO 3
    if home_prob is None or draw_prob is None or away_prob is None:
        prob_block = re.search(r'BLOCO 3.*?PROBABILIDADES.*?(?:BLOCO 4|💡|═════|$)', analysis_text, re.DOTALL | re.IGNORECASE)
        
        if prob_block:
            prob_text = prob_block.group(0)
            print(f"\n📊 Encontrou BLOCO 3")
            print(f"Texto do bloco (primeiras 200 chars): {prob_text[:200]}")
            
            # Extrair as probabilidades por nome do time
            lines = prob_text.split('\n')
            for line in lines:
                line_lower = line.lower().strip()
                
                if home_prob is None and home_name.lower() in line_lower:
                    match = re.search(rf'{re.escape(home_name.lower())}[^\d]*(\d+)%', line_lower)
                    if match:
                        home_prob = int(match.group(1))
                        print(f"✅ {home_name}: {home_prob}% (BLOCO 3)")
                        print(f"   Linha: {line[:100]}")
                
                if draw_prob is None and 'empate' in line_lower:
                    match = re.search(r'empate[^\d]*(\d+)%', line_lower)
                    if match:
                        draw_prob = int(match.group(1))
                        print(f"✅ Empate: {draw_prob}% (BLOCO 3)")
                        print(f"   Linha: {line[:100]}")
                
                if away_prob is None and away_name.lower() in line_lower:
                    match = re.search(rf'{re.escape(away_name.lower())}[^\d]*(\d+)%', line_lower)
                    if match:
                        away_prob = int(match.group(1))
                        print(f"✅ {away_name}: {away_prob}% (BLOCO 3)")
                        print(f"   Linha: {line[:100]}")
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   {home_name}: {home_prob}%")
    print(f"   Empate: {draw_prob}%")
    print(f"   {away_name}: {away_prob}%")
    
    return home_prob, draw_prob, away_prob


# Texto de teste do Gabon vs Ivory Coast
test_text = """
═══════════════════════════════════════
📊 BLOCO 3 — PROBABILIDADES VISUAIS
═══════════════════════════════════════
📊 PROBABILIDADES
🏟️ Gabon: 10%
🤝 Empate: 21%
✈️ Ivory Coast: 69%
💡 Interpretação rápida: Ivory Coast é o favorito disparado para vencer
"""

print("="*60)
print("TESTE: Gabon vs Ivory Coast")
print("="*60)
test_extraction(test_text, "Gabon", "Ivory Coast")
