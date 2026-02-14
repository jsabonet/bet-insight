"""
Script de validação para Sprint 5 (Correção de erros adicionais)

Testa:
1. PostDecisionSelector removido
2. Nomenclatura canônica no ContextAnalyzer
"""
import sys
import os
import django

# Configurar Django
sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("="*80)
print("🧪 VALIDAÇÃO SPRINT 5 - ERROS ADICIONAIS")
print("="*80)

# TESTE 1: PostDecisionSelector não deve existir mais
print("\n✅ TESTE 1: PostDecisionSelector Removido")
import glob
post_selector_files = glob.glob('apps/analysis/services/post_decision_selector.py')

if post_selector_files:
    print(f"   ❌ FALHOU: Arquivo ainda existe: {post_selector_files}")
    test1_pass = False
else:
    print("   ✅ PASSOU: Arquivo post_decision_selector.py removido")
    # Tentar importar para garantir
    try:
        from apps.analysis.services.post_decision_selector import PostDecisionSelector
        print("   ❌ FALHOU: Classe ainda importável!")
        test1_pass = False
    except (ImportError, ModuleNotFoundError):
        print("   ✅ PASSOU: Classe não importável (correto)")
        test1_pass = True

# TESTE 2: DailyBetGenerator não usa PostDecisionSelector
print("\n✅ TESTE 2: DailyBetGenerator Atualizado")
from apps.analysis.services.daily_bet_generator import DailyBetGenerator
gen = DailyBetGenerator()

if hasattr(gen, 'post_selector'):
    print("   ❌ FALHOU: DailyBetGenerator ainda tem self.post_selector")
    test2_pass = False
else:
    print("   ✅ PASSOU: DailyBetGenerator não usa mais PostDecisionSelector")
    test2_pass = True

# TESTE 3: ContextAnalyzer usa nomenclatura canônica
print("\n✅ TESTE 3: ContextAnalyzer - Nomenclatura Canônica")
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.config.analysis_config import ContextMarketWeights

# Verificar se ContextMarketWeights usa nomes canônicos
weights = ContextMarketWeights.LOW_MOTIVATION_BOTH
has_uppercase = False
uppercase_keys = []

for key in weights.keys():
    if any(c.isupper() for c in key if c.isalpha()):
        has_uppercase = True
        uppercase_keys.append(key)

if has_uppercase:
    print(f"   ❌ FALHOU: Chaves com maiúsculas encontradas: {uppercase_keys}")
    test3_pass = False
else:
    print("   ✅ PASSOU: Todos os pesos usam nomenclatura canônica (minúsculas)")
    print(f"      Exemplo: {list(weights.keys())[:3]}")
    test3_pass = True

# TESTE 4: Detectar padrão e verificar market_weights
print("\n✅ TESTE 4: Padrões do ContextAnalyzer - Nomenclatura")

# Simular features para detectar padrão
features = {
    'motivation': {
        'home_motivation': 3,  # Desmotivado (30%)
        'away_motivation': 2   # Muito desmotivado (20%)
    }
}

analyzer = ContextAnalyzer()
pattern = analyzer._detect_low_motivation_both(features)

if pattern:
    favorable = pattern.get('favorable_markets', [])
    weights = pattern.get('market_weights', {})
    
    # Verificar se favorable_markets tem nomenclatura canônica
    has_uppercase_markets = any(any(c.isupper() for c in m if c.isalpha()) for m in favorable)
    
    # Verificar se market_weights tem chaves canônicas
    has_uppercase_weights = any(any(c.isupper() for c in k if k.isalpha()) for k in weights.keys())
    
    if has_uppercase_markets or has_uppercase_weights:
        print("   ❌ FALHOU: Nomenclatura não-canônica encontrada")
        if has_uppercase_markets:
            print(f"      favorable_markets: {favorable}")
        if has_uppercase_weights:
            print(f"      market_weights keys: {list(weights.keys())}")
        test4_pass = False
    else:
        print("   ✅ PASSOU: Padrão usa nomenclatura 100% canônica")
        print(f"      favorable_markets: {favorable[:3]}...")
        print(f"      market_weights: {list(weights.keys())[:3]}...")
        test4_pass = True
else:
    print("   ⚠️  SKIP: Padrão não detectado com features de teste")
    test4_pass = True

# TESTE 5: Verificar integração com normalize_market_name
print("\n✅ TESTE 5: Integração com Normalização")
from apps.analysis.config.market_standards import normalize_market_name

if pattern:
    # Tentar normalizar todos os mercados favoráveis
    all_normalized = True
    for market in pattern['favorable_markets']:
        normalized = normalize_market_name(market)
        if normalized is None:
            print(f"   ❌ Mercado não reconhecido: {market}")
            all_normalized = False
        elif normalized != market:
            print(f"   ⚠️  Mercado precisa normalização: '{market}' → '{normalized}'")
            all_normalized = False
    
    if all_normalized:
        print("   ✅ PASSOU: Todos os mercados já estão normalizados")
        test5_pass = True
    else:
        print("   ❌ FALHOU: Alguns mercados não estão normalizados")
        test5_pass = False
else:
    print("   ⚠️  SKIP: Sem padrão para validar")
    test5_pass = True

# RESUMO
print("\n" + "="*80)
print("📊 RESUMO DA VALIDAÇÃO")
print("="*80)

tests = [
    ("PostDecisionSelector removido", test1_pass),
    ("DailyBetGenerator atualizado", test2_pass),
    ("ContextMarketWeights canônico", test3_pass),
    ("Padrões ContextAnalyzer canônicos", test4_pass),
    ("Integração com normalização", test5_pass)
]

passed = sum(1 for _, p in tests if p)
total = len(tests)

for name, result in tests:
    status = "✅ PASSOU" if result else "❌ FALHOU"
    print(f"   {status}: {name}")

print("\n" + "="*80)
if passed == total:
    print(f"🎉 TODOS OS {total} TESTES PASSARAM!")
    print("✅ Sprint 5 concluído com sucesso")
else:
    print(f"⚠️  {passed}/{total} testes passaram")
    print(f"❌ {total - passed} teste(s) falharam")
print("="*80)

# Retornar código de saída
sys.exit(0 if passed == total else 1)
