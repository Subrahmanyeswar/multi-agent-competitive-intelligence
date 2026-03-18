@echo off
echo Starting in DEV mode (hot reload)...
echo.
echo Open two terminals:
echo.
echo Terminal 1 (Backend):
echo   venv\Scripts\activate
echo   python api_server.py
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo.
pause
