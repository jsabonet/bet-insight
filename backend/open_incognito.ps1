# Testar em modo anônimo (sem cache)
# Abre navegador em modo privado direto no frontend

$divider = "=" * 80

Write-Host "`n$divider" -ForegroundColor Cyan
Write-Host "🔓 ABRINDO NAVEGADOR EM MODO ANONIMO" -ForegroundColor Cyan
Write-Host "$divider`n" -ForegroundColor Cyan

Write-Host "Por que modo anônimo?" -ForegroundColor Yellow
Write-Host "  - SEM cache (arquivos sempre novos)" -ForegroundColor White
Write-Host "  - SEM cookies antigos" -ForegroundColor White
Write-Host "  - SEM localStorage" -ForegroundColor White
Write-Host "  - Teste limpo e isolado`n" -ForegroundColor White

# Detectar navegadores instalados
$chrome = Get-Command "chrome.exe" -ErrorAction SilentlyContinue
$edge = Get-Command "msedge.exe" -ErrorAction SilentlyContinue

$url = "http://127.0.0.1:5173"

if ($edge) {
    Write-Host "✅ Abrindo Microsoft Edge (Modo InPrivate)...`n" -ForegroundColor Green
    Start-Process "msedge.exe" -ArgumentList "--inprivate", $url
} elseif ($chrome) {
    Write-Host "✅ Abrindo Google Chrome (Modo Incógnito)...`n" -ForegroundColor Green
    Start-Process "chrome.exe" -ArgumentList "--incognito", $url
} else {
    Write-Host "❌ Chrome/Edge não encontrados!" -ForegroundColor Red
    Write-Host "`nAbra manualmente:" -ForegroundColor Yellow
    Write-Host "  1. Pressione Ctrl + Shift + N (Chrome) ou Ctrl + Shift + P (Edge)" -ForegroundColor White
    Write-Host "  2. Vá para: $url`n" -ForegroundColor Cyan
    exit
}

Write-Host "$divider" -ForegroundColor Green
Write-Host "PRÓXIMAS ETAPAS:" -ForegroundColor Green
Write-Host "$divider`n" -ForegroundColor Green

Write-Host "Na janela anônima que abriu:" -ForegroundColor Yellow
Write-Host "`n1. Fazer LOGIN" -ForegroundColor White
Write-Host "   Usuario/Email e Senha`n" -ForegroundColor Cyan

Write-Host "2. BUSCAR 'Brentford vs Arsenal'" -ForegroundColor White
Write-Host "   Na barra de pesquisa`n" -ForegroundColor Cyan

Write-Host "3. CLICAR 'Análise Completa'" -ForegroundColor White
Write-Host "   No card da partida`n" -ForegroundColor Cyan

Write-Host "4. AGUARDAR 25-35 SEGUNDOS" -ForegroundColor Yellow
Write-Host "   Sistema está RECALCULANDO (não é cache)`n" -ForegroundColor Cyan

Write-Host "5. VERIFICAR RESULTADOS:" -ForegroundColor White
Write-Host "   Arsenal deve mostrar ~57% (NÃO 42.4%)" -ForegroundColor Green
Write-Host "   Brentford ~18% (NÃO 26.5%)" -ForegroundColor Green
Write-Host "   Empate ~25% (NÃO 31.1%)`n" -ForegroundColor Green

Write-Host "$divider" -ForegroundColor Cyan
Write-Host "SE AINDA MOSTRAR ARSENAL 42.4%:" -ForegroundColor Red
Write-Host "$divider`n" -ForegroundColor Cyan

Write-Host "1. PRESSIONAR F12 (abrir DevTools)" -ForegroundColor Yellow
Write-Host "2. IR na aba CONSOLE" -ForegroundColor Yellow
Write-Host "3. CLICAR 'Análise Completa' novamente" -ForegroundColor Yellow
Write-Host "4. PROCURAR no console:" -ForegroundColor Yellow
Write-Host "   'FORCAR RECALCULO' ou 'force_recalculate'" -ForegroundColor Cyan
Write-Host "5. TIRAR SCREENSHOT e me mostrar`n" -ForegroundColor Yellow

Write-Host $divider -ForegroundColor Cyan
Write-Host ""
