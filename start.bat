@echo off
echo ===============================================
echo Starting DP System - Fullstack Application
echo ===============================================
echo.

echo Step 1: Initializing Database...
cd backend
python init_database.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo.

echo Step 2: Starting Backend Server...
start "DP System Backend" cmd /k "python app.py"
echo Backend server starting at http://localhost:5000
echo.

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul
echo.

echo Step 3: Starting Frontend...
cd ..\frontend
start "DP System Frontend" cmd /k "npm start"
echo Frontend will open at http://localhost:3000
echo.

echo ===============================================
echo DP System is starting!
echo ===============================================
echo.
echo Two terminal windows will open:
echo   1. Backend API (Flask)
echo   2. Frontend UI (React)
echo.
echo Your browser should open automatically.
echo If not, navigate to: http://localhost:3000
echo.
echo Press Ctrl+C in each terminal window to stop.
echo ===============================================
pause
