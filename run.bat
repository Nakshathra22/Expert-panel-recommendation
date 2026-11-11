@echo off
REM ═══════════════════════════════════════════════════════
REM  Expert Panel Recommendation System — Quick Start
REM ═══════════════════════════════════════════════════════

echo.
echo  ====================================================
echo   Expert Panel Recommendation System
echo  ====================================================
echo.

REM 1. Create venv if missing
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/4] Virtual environment exists. Skipping.
)

REM 2. Activate and install
echo [2/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

REM 3. Seed demo data (safe — won't duplicate)
echo [3/4] Seeding demo data...
python seed_demo.py

REM 4. Start server
echo [4/4] Starting Flask server at http://127.0.0.1:5000
echo.
echo  Admin Login:   username=admin  password=admin123
echo  Faculty Login: Use credentials sent via email (after accepting invitation)
echo.
python app.py
pause
