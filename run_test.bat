@echo off
echo ============================================
echo iHerb Cloudflare Bypass - Quick Test
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
python -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)

echo [2/3] Installing Playwright browsers...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Playwright
    pause
    exit /b 1
)

echo [3/3] Running quick test...
echo.
python iherb_bypass.py

echo.
echo ============================================
echo Test completed!
echo ============================================
pause
