@echo off
echo ============================================================
echo   Competitive Intelligence Dashboard
echo ============================================================
echo.
echo Freeing port 8000 if in use...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo Building frontend...
cd /d "C:\Users\SUBBU\Downloads\Multi-Agent Competitive Intelligence System\frontend"
call npm run build
cd ..

echo.
echo Starting server...
call venv\Scripts\activate
echo.
echo Dashboard: http://localhost:8000
echo.
python main.py
