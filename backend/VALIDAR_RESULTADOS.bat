@echo off
REM Script para validar resultados de bilhetes pendentes

echo ================================================================================
echo   PLACERCERTO - Validacao de Resultados
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

echo [2/2] Validando resultados...
echo.
python manage.py validate_daily_bets

echo.
echo ================================================================================
echo   Comando concluido!
echo ================================================================================
echo.
pause
