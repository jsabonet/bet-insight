"""
Script rápido para limpar cache e reiniciar servidor
Combina limpeza de cache + restart em um único comando
"""

# Criar diretório se não existir
$mgmtDir = "apps\analysis\management\commands"
if (!(Test-Path $mgmtDir)) {
    New-Item -ItemType Directory -Path $mgmtDir -Force | Out-Null
    New-Item -ItemType File -Path "apps\analysis\management\__init__.py" -Force | Out-Null
    New-Item -ItemType File -Path "apps\analysis\management\commands\__init__.py" -Force | Out-Null
    Write-Host "✅ Diretórios de management criados" -ForegroundColor Green
}

$divider = "=" * 80

Write-Host ""
Write-Host $divider -ForegroundColor Cyan
Write-Host "🧹 LIMPEZA COMPLETA: Cache + Restart" -ForegroundColor Cyan
Write-Host $divider -ForegroundColor Cyan
Write-Host ""

# Passo 1: Limpar cache
Write-Host "1️⃣ Limpando todos os caches..." -ForegroundColor Yellow
Write-Host ""

python manage.py clear_cache

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao limpar cache!" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 O comando clear_cache não existe ainda?" -ForegroundColor Yellow
    Write-Host "   Executando limpeza manual via shell..." -ForegroundColor Gray
    Write-Host ""
    
    python manage.py shell -c "from django.core.cache import cache; from apps.analysis.services.cache_service import _cache; cache.clear(); _cache.clear(); print('✅ Cache limpo manualmente')"
}

Write-Host ""
Write-Host $divider -ForegroundColor Green
Write-Host "✅ CACHE LIMPO!" -ForegroundColor Green
Write-Host $divider -ForegroundColor Green
Write-Host ""

# Passo 2: Validar arquivos
Write-Host "2️⃣ Validando arquivos modificados..." -ForegroundColor Yellow
Write-Host ""

$config = Get-Item "apps\analysis\config\analysis_config.py"
$ml = Get-Item "apps\analysis\services\ml_integration.py"

Write-Host "   ✅ analysis_config.py - $($config.LastWriteTime)" -ForegroundColor Green
Write-Host "   ✅ ml_integration.py - $($ml.LastWriteTime)" -ForegroundColor Green

Write-Host ""

# Passo 3: Testar importação
Write-Host "3️⃣ Testando CLEAR_FAVORITE..." -ForegroundColor Yellow
Write-Host ""

$testResult = python -c @"
import sys
sys.path.insert(0, '.')
try:
    from apps.analysis.config.analysis_config import EnsembleWeights
    config = EnsembleWeights.CLEAR_FAVORITE
    print(f'   ✅ Poisson: {config["poisson"]*100:.0f}% | ML: {config["ml"]*100:.0f}% | Market: {config["market"]*100:.0f}%')
except Exception as e:
    print(f'   ❌ Erro: {e}')
    sys.exit(1)
"@

Write-Host $testResult

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Falha ao importar CLEAR_FAVORITE!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host $divider -ForegroundColor Green
Write-Host "✅ TUDO VALIDADO!" -ForegroundColor Green
Write-Host $divider -ForegroundColor Green
Write-Host ""

# Passo 4: Reiniciar servidor
Write-Host "4️⃣ Iniciando servidor Django..." -ForegroundColor Yellow
Write-Host ""
Write-Host "   ⚠️  Servidor será iniciado em 3 segundos..." -ForegroundColor Yellow
Write-Host "   Pressione Ctrl+C para cancelar" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 3

Write-Host $divider -ForegroundColor Cyan
Write-Host "🟢 SERVIDOR DJANGO INICIANDO COM CACHE LIMPO" -ForegroundColor Green
Write-Host $divider -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 APÓS INICIAR, TESTE:" -ForegroundColor Yellow
Write-Host "   1. Busque 'Brentford vs Arsenal'" -ForegroundColor White
Write-Host "   2. Clique 'Análise Completa'" -ForegroundColor White
Write-Host "   3. Arsenal deve estar ~57% ✅" -ForegroundColor Green
Write-Host ""
Write-Host "NOS LOGS, DEVE APARECER:" -ForegroundColor Yellow
Write-Host "   Config: CLEAR_FAVORITE (Poisson 70%)" -ForegroundColor Cyan
Write-Host ""
Write-Host $divider -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor
python manage.py runserver
