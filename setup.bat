@echo off
REM Quick setup script for Windows

echo ========================================
echo Intent Detection System - Quick Setup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [1/6] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure Python 3.11+ is installed
        pause
        exit /b 1
    )
    echo Done!
) else (
    echo [1/6] Virtual environment already exists
)

echo.
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/6] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo [4/6] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Done!

echo.
echo [5/6] Creating .env file...
if not exist ".env" (
    copy .env.example .env >nul
    echo Created .env file
    echo.
    echo IMPORTANT: Please edit .env and add your GOOGLE_API_KEY
    echo You can get it from: https://ai.google.dev/
    echo.
    set /p dummy="Press Enter to open .env file in Notepad..."
    notepad .env
) else (
    echo .env file already exists
)

echo.
echo [6/6] Creating directories and initializing database...
python scripts\init_db.py
if errorlevel 1 (
    echo ERROR: Database initialization failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure GOOGLE_API_KEY is set in .env file
echo 2. Ingest sample knowledge base:
echo    python scripts\ingest_cli.py --tenant bank-asia kb\sample_channels.md
echo.
echo 3. Start the server:
echo    python -m uvicorn app.main:app --reload
echo.
echo 4. Visit: http://localhost:8000/docs
echo.
echo For more help, see README.md or QUICKSTART.md
echo ========================================
echo.
pause
