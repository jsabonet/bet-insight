@echo off
REM Agendador para executar validação de resultados em background

cd /d "%~dp0"

REM Criar pasta de logs se não existir
if not exist "logs" mkdir logs

REM Ativar ambiente virtual e executar
call venv\Scripts\activate.bat
python manage.py validate_daily_bets >> logs\validation_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log 2>&1
