@echo off
REM UiPath Workflow Analyzer - Streamlit App Launcher (Windows)

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   🤖 UiPath Workflow Analyzer - Streamlit App         ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check Python installation
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call .venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ pip upgraded
echo.

REM Install requirements
echo 📥 Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ⚠️  requirements.txt not found
    echo Installing essential packages...
    pip install streamlit pandas reportlab
)
echo.

REM Check if app.py exists
if not exist "app.py" (
    echo ❌ app.py not found
    pause
    exit /b 1
)

REM Display app info
echo ════════════════════════════════════════════════════════
echo 📊 Application Information:
echo ════════════════════════════════════════════════════════
echo App:         UiPath Workflow Analyzer
echo Type:        Streamlit Web Application
echo File:        app.py
echo Port:        8501
echo URL:         http://localhost:8501
echo ════════════════════════════════════════════════════════
echo.

REM Display features
echo ✨ Features:
echo    🔍 Workflow Analysis
echo    📊 Health Score Calculation
echo    ⚠️  Issue Detection
echo    💡 Recommendations
echo    📥 Multiple Export Formats (Markdown, PDF, JSON)
echo.

REM Ask for custom port
set PORT=8501
set /p PORT="Press Enter to start (or type custom port [default: 8501]): "

if "%PORT%"=="" (
    set PORT=8501
)

echo.
echo 🚀 Starting Streamlit application...
echo 📱 Access the app at: http://localhost:%PORT%
echo.
echo 💡 Tips:
echo    • Press 'q' to quit
echo    • Reload the browser to restart
echo    • Check the terminal for logs
echo.

REM Run Streamlit
streamlit run app.py --server.port %PORT%

pause
