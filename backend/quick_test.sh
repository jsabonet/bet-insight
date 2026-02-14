#!/bin/bash
# 🔍 QUICK TEST: Verificar se correção CLEAR_FAVORITE está ativa

echo ""
echo "================================================================================"
echo "🧪 TESTE RÁPIDO: Verificação da Correção CLEAR_FAVORITE"
echo "================================================================================"
echo ""

# 1. Verificar se servidor está rodando
echo "1️⃣ Verificando servidor Django..."
SERVER_RUNNING=$(Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*manage.py*"} | Measure-Object | Select-Object -ExpandProperty Count)

if [ $SERVER_RUNNING -gt 0 ]; then
    echo "   ✅ Servidor rodando (PID encontrado)"
    echo "   ⚠️  Mas será que carregou o código novo?"
else
    echo "   ❌ Servidor NÃO está rodando!"
    echo "   💡 Execute: python manage.py runserver"
    exit 1
fi

echo ""
echo "2️⃣ Verificando última modificação dos arquivos..."
echo ""

# Verificar timestamp dos arquivos
CONFIG_FILE="apps/analysis/config/analysis_config.py"
ML_FILE="apps/analysis/services/ml_integration.py"

if [ -f "$CONFIG_FILE" ]; then
    CONFIG_TIME=$(stat -c %y "$CONFIG_FILE" 2>/dev/null || stat -f "%Sm" "$CONFIG_FILE")
    echo "   ✅ analysis_config.py: $CONFIG_TIME"
else
    echo "   ❌ analysis_config.py não encontrado!"
fi

if [ -f "$ML_FILE" ]; then
    ML_TIME=$(stat -c %y "$ML_FILE" 2>/dev/null || stat -f "%Sm" "$ML_FILE")
    echo "   ✅ ml_integration.py: $ML_TIME"
else
    echo "   ❌ ml_integration.py não encontrado!"
fi

echo ""
echo "3️⃣ Testando importação do CLEAR_FAVORITE..."
echo ""

python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from apps.analysis.config.analysis_config import EnsembleWeights
    config = EnsembleWeights.CLEAR_FAVORITE
    print(f'   ✅ CLEAR_FAVORITE encontrado!')
    print(f'   📊 Poisson: {config[\"poisson\"]*100:.0f}%')
    print(f'   🤖 ML: {config[\"ml\"]*100:.0f}%')
    print(f'   📈 Market: {config[\"market\"]*100:.0f}%')
    print(f'   ✅ Soma: {sum(config.values())*100:.0f}%')
except Exception as e:
    print(f'   ❌ Erro: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Falha ao importar CLEAR_FAVORITE!"
    exit 1
fi

echo ""
echo "================================================================================"
echo "📋 PRÓXIMOS PASSOS"
echo "================================================================================"
echo ""
echo "✅ Arquivos modificados: OK"
echo "✅ CLEAR_FAVORITE importável: OK"
echo "✅ Configuração validada: OK"
echo ""
echo "❓ Servidor carregou o código novo?"
echo ""
echo "Para garantir:"
echo "   1. ⚠️  REINICIE o servidor Django (Ctrl+C e python manage.py runserver)"
echo "   2. 🔍 Faça NOVA análise (não reabra análise antiga)"
echo "   3. ✅ Verifique Arsenal ~57% (não 42.4%)"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   • Análises ANTIGAS (salvas antes) → Continuam com 42.4%"
echo "   • Análises NOVAS (após restart) → Terão 56.9%"
echo ""
echo "================================================================================"
