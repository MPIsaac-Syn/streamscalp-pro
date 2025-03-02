@echo off
REM StreamScalp Pro Setup Script for Windows
REM This script helps set up the project dependencies in the correct order
REM to avoid dependency conflicts

echo Setting up StreamScalp Pro dependencies...

REM Check if virtual environment is active
if "%VIRTUAL_ENV%"=="" (
    echo Error: No virtual environment detected.
    echo Please activate your virtual environment first with:
    echo   .venv\Scripts\activate.bat ^(or equivalent for your system^)
    exit /b 1
)

echo Step 1: Installing base dependencies...
pip install -r requirements-base.txt

echo Step 2: Installing CCXT...
pip install -r requirements-ccxt.txt

echo Step 3: Installing Alpaca API with --no-deps to avoid conflicts...
pip install -r requirements-alpaca.txt --no-deps

set /p install_dev=Do you want to install development dependencies? (y/n): 
if /i "%install_dev%"=="y" (
    echo Installing development dependencies...
    pip install -r requirements-dev.txt
)

set /p install_backtrader=Do you want to install Backtrader for backtesting capabilities? (y/n): 
if /i "%install_backtrader%"=="y" (
    echo Installing Backtrader dependencies...
    pip install -r requirements-backtrader.txt
)

echo Setup complete!
echo You may see dependency conflict warnings, but the application should work correctly.
echo To test, run: python main.py --help