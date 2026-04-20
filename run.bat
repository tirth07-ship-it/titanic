@echo off
echo ========================================
echo   Titanic App - API ^& Frontend
echo ========================================
echo.

cd backend
echo [1/4] Checking Virtual Environment...
if not exist "venv" (
    python -m venv venv
)

echo [2/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
cd ..

echo [3/4] Starting Backend (Flask API) on Port 5000...
start "Titanic Backend API" cmd /c "cd backend && call venv\Scripts\activate.bat && python app.py"

echo [4/4] Starting Frontend on Port 8000...
start "Titanic Frontend" cmd /c "cd frontend && python -m http.server 8000"

echo.
echo ========================================
echo   Backend: http://127.0.0.1:5000
echo   Frontend: http://127.0.0.1:8000
echo   Opening in Chrome...
echo ========================================
echo.

:: Open Chrome after a short delay
timeout /t 3 >nul
start chrome http://127.0.0.1:8000

echo Done! Keep the two new command prompt windows open to keep the servers running.
pause
