import re


def extract_from_prob_block(full_text: str, h_name: str, a_name: str):
    block_match = re.search(r'BLOCO\s*3[\s\S]*?PROBABILIDADES', full_text, re.IGNORECASE)
    start_idx = None
    if block_match:
        start_idx = block_match.end()
        print("📌 BLOCO 3 localizado")
    else:
        alt_match = re.search(r'📊\s*PROBABILIDADES', full_text, re.IGNORECASE)
        if alt_match:
            start_idx = alt_match.end()
            print("📌 Cabeçalho '📊 PROBABILIDADES' localizado")
    if start_idx is None:
        print("❌ PROBABILIDADES não localizado")
        return None, None, None
    tail = full_text[start_idx:]
    sep = re.search(r'(BLOCO\s*4|════|💡)', tail, re.IGNORECASE)
    if sep:
        tail = tail[:sep.start()]
    print(f"📄 Janela PROBABILIDADES capturada com {len(tail)} chars")
    print(tail[:200].replace('\n',' | '))
    lines = [ln.strip() for ln in tail.split('\n')]
    def find_pct_after_index(idx):
        for j in range(idx, min(idx+3, len(lines))):
            m = re.search(r'(\d+)%', lines[j])
            if m:
                return int(m.group(1)), j
        return None, None
    h = d = a = None
    for i, ln in enumerate(lines):
        ll = ln.lower()
        if h is None and h_name.lower() in ll:
            val, src = find_pct_after_index(i)
            if val is not None:
                h = val
                print(f"✅ {h_name}: {h}% (linha {src})")
        if d is None and 'empate' in ll:
            val, src = find_pct_after_index(i)
            if val is not None:
                d = val
                print(f"✅ Empate: {d}% (linha {src})")
        if a is None and a_name.lower() in ll:
            val, src = find_pct_after_index(i)
            if val is not None:
                a = val
                print(f"✅ {a_name}: {a}% (linha {src})")
    return h, d, a

text = """
═══════════════════════════════════════
📊 BLOCO 3 — PROBABILIDADES VISUAIS
═══════════════════════════════════════
📊 PROBABILIDADES
🏠
Auckland:
56%
🤝
Empate:
23%
✈️
Newcastle Jets:
21%
💡
Interpretação rápida:
Auckland é o favorito
"""

h, d, a = extract_from_prob_block(text, "Auckland", "Newcastle Jets")
print("RESULT:", h, d, a)
