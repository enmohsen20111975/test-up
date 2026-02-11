@echo off
echo.
echo.
echo [33m🚀 Starting EngiSuite Analytics Pro...[0m
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [31m❌ Python is not installed. Please install Python 3.10 or later first.[0m
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
    set "PYTHON_VERSION=%%i"
)
for /f "delims=. tokens=1-2" %%a in ("%PYTHON_VERSION%") do (
    set "PYTHON_MAJOR=%%a"
    set "PYTHON_MINOR=%%b"
)

if %PYTHON_MAJOR% LSS 3 (
    echo [31m❌ Python 3.10 or later is required[0m
    pause
    exit /b 1
)

if %PYTHON_MAJOR% EQU 3 if %PYTHON_MINOR% LSS 10 (
    echo [31m❌ Python 3.10 or later is required[0m
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo [36m📦 Creating virtual environment...[0m
    python -m venv venv
    if errorlevel 1 (
        echo [31m❌ Failed to create virtual environment[0m
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [36m🔧 Activating virtual environment...[0m
call venv\Scripts\activate.bat

REM Install dependencies
echo [36m📦 Installing dependencies...[0m
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo [31m❌ Failed to install dependencies[0m
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [33m⚠️  .env file not found. Creating from .env.example...[0m
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [33mℹ️  Please edit the .env file with your API keys before starting.[0m
    ) else (
        echo [31m❌ .env.example file not found[0m
        pause
        exit /b 1
    )
)

REM Start the application
echo [36m🔧 Starting backend server...[0m
echo [36m📱 Frontend: http://localhost[0m
echo [36m🔧 Backend API: http://localhost:8000[0m
echo [36m📚 API Documentation: http://localhost:8000/docs[0m
echo.
echo [33mPress Ctrl+C to stop the server[0m
echo.

cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause