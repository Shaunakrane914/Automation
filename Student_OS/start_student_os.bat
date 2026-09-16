@echo off
setlocal
cd /d "%~dp0backend"

:: 1. Check if backend port 8000 is already active
netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul
if %errorlevel% neq 0 (
    :: Launch FastAPI uvicorn daemon in minimized background process
    start "Student OS Backend" /min python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    timeout /t 2 /nobreak >nul
)

:: 2. Launch web application in default browser
start "" "http://127.0.0.1:8000/"
exit /b 0
