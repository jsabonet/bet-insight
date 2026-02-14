# 🚀 RESTART E TESTE - Correção CLEAR_FAVORITE
# Script para reiniciar servidor e validar correção

Write-Host "`n" -NoNewline
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host "🚀 REINICIANDO SERVIDOR COM CORREÇÃO CLEAR_FAVORITE" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Cyan

Write-Host "`n📋 CHECKLIST PRÉ-RESTART:`n" -ForegroundColor Yellow

# 1. Verificar arquivos
Write-Host "1. Arquivos modificados:" -ForegroundColor White
$config = Get-Item "apps\analysis\config\analysis_config.py"
$ml = Get-Item "apps\analysis\services\ml_integration.py"
Write-Host "   ✅ analysis_config.py - $($config.LastWriteTime)" -ForegroundColor Green
Write-Host "   ✅ ml_integration.py - $($ml.LastWriteTime)" -ForegroundColor Green

# 2. Validar sintaxe
Write-Host "`n2. Validando sintaxe:" -ForegroundColor White
python -m py_compile apps\analysis\config\analysis_config.py 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ analysis_config.py - OK" -ForegroundColor Green
} else {
    Write-Host "   ❌ analysis_config.py - ERRO!" -ForegroundColor Red
    exit 1
}

python -m py_compile apps\analysis\services\ml_integration.py 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ ml_integration.py - OK" -ForegroundColor Green
} else {
    Write-Host "   ❌ ml_integration.py - ERRO!" -ForegroundColor Red
    exit 1
}

# 3. Testar importação
Write-Host "`n3. Testando importação CLEAR_FAVORITE:" -ForegroundColor White
$testImport = python -c @"
import sys
sys.path.insert(0, '.')
from apps.analysis.config.analysis_config import EnsembleWeights
config = EnsembleWeights.CLEAR_FAVORITE
print(f'Poisson={config[\"poisson\"]*100:.0f}% ML={config[\"ml\"]*100:.0f}% Market={config[\"market\"]*100:.0f}%')
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ CLEAR_FAVORITE importado: $testImport" -ForegroundColor Green
} else {
    Write-Host "   ❌ Falha ao importar!" -ForegroundColor Red
    exit 1
}

Write-Host "`n" -NoNewline
Write-Host ("="*80) -ForegroundColor Green
Write-Host "✅ TUDO PRONTO! INICIANDO SERVIDOR..." -ForegroundColor Green
Write-Host ("="*80) -ForegroundColor Green

Write-Host "`n⏳ Servidor será iniciado em 3 segundos..." -ForegroundColor Yellow
Write-Host "   Pressione Ctrl+C para cancelar`n" -ForegroundColor Gray

Start-Sleep -Seconds 3

Write-Host ("="*80) -ForegroundColor Cyan
Write-Host "🟢 SERVIDOR DJANGO INICIANDO" -ForegroundColor Green
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 APÓS INICIAR, FAÇA:" -ForegroundColor Yellow
Write-Host "   1. Busque 'Brentford vs Arsenal' no frontend" -ForegroundColor White
Write-Host "   2. Clique em 'Análise Completa'" -ForegroundColor White
Write-Host "   3. Verifique: Arsenal deve estar ~57% (não 42%)" -ForegroundColor White
Write-Host ""
Write-Host "🔍 NOS LOGS, DEVE APARECER:" -ForegroundColor Yellow
Write-Host "   ⚖️ Config: CLEAR_FAVORITE (Poisson 70%)" -ForegroundColor Cyan
Write-Host "   📊 Arsenal: 56.9%" -ForegroundColor Cyan
Write-Host ""
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor
python manage.py runserver
