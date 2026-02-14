@echo off
REM Agendador para executar geração de bilhetes em background

cd /d "%~dp0"

REM Criar pasta de logs se não existir
if not exist "logs" mkdir logs

REM Ativar ambiente virtual e executar
call venv\Scripts\activate.bat
python manage.py generate_daily_bets >> logs\daily_bets_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log 2>&1
