#!/bin/bash
# StreamScalp Pro Setup Script
# This script helps set up the project dependencies in the correct order
# to avoid dependency conflicts

echo "Setting up StreamScalp Pro dependencies..."

# Check if virtual environment is active
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Error: No virtual environment detected."
    echo "Please activate your virtual environment first with:"
    echo "  source .venv/bin/activate (or equivalent for your system)"
    exit 1
fi

echo "Step 1: Installing base dependencies..."
pip install -r requirements-base.txt

echo "Step 2: Installing CCXT..."
pip install -r requirements-ccxt.txt

echo "Step 3: Installing Alpaca API with --no-deps to avoid conflicts..."
pip install -r requirements-alpaca.txt --no-deps

echo "Do you want to install development dependencies? (y/n)"
read -r install_dev
if [[ "$install_dev" == "y" || "$install_dev" == "Y" ]]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

echo "Do you want to install Backtrader for backtesting capabilities? (y/n)"
read -r install_backtrader
if [[ "$install_backtrader" == "y" || "$install_backtrader" == "Y" ]]; then
    echo "Installing Backtrader dependencies..."
    pip install -r requirements-backtrader.txt
fi

echo "Setup complete!"
echo "You may see dependency conflict warnings, but the application should work correctly."
echo "To test, run: python main.py --help"