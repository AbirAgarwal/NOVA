@echo off
cd /d "%~dp0"

echo Starting NOVA Backend Server...
start "NOVA Server" venv\Scripts\python.exe nova_server.py

echo Waiting for server to start...
timeout /t 3 >nul

echo Opening NOVA Interface...
start "" nova.html

echo.
echo NOVA is running!
echo Backend: http://localhost:8765
echo Frontend: nova.html (opened in your browser)
echo.
pause
