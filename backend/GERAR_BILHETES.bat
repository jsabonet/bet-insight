@echo off
REM Script para gerar bilhetes automáticos diariamente

echo ================================================================================
echo   PLACERCERTO - Gerador de Bilhetes Automaticos
echo ================================================================================
echo.

cd /d "%~dp0"

REM Ativar ambiente virtual
echo [1/2] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERRO: Nao foi possivel ativar o ambiente virtual!
    pause
    exit /b 1
)

echo [2/2] Gerando bilhetes...
echo.
python manage.py generate_daily_bets

echo.
echo ================================================================================
echo   Comando concluido!
echo ================================================================================
echo.
pause
