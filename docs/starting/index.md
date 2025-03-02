# Getting Started with StreamScalp Pro

This guide will help you set up and run StreamScalp Pro on your local machine.

## Prerequisites

- Python 3.8 or higher
- API keys for supported exchanges (Binance, Alpaca)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/streamscalp-pro.git
   cd streamscalp-pro
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source .venv/bin/activate
     ```

4. Install dependencies:

   The project uses a structured approach to manage dependencies to avoid conflicts. You can use the provided setup scripts:

   - Windows:
     ```
     .\setup.bat
     ```
   - macOS/Linux:
     ```
     ./setup.sh
     ```

   Alternatively, you can install dependencies manually:
   
   ```
   # Install base dependencies
   pip install -r requirements-base.txt
   
   # Install CCXT
   pip install -r requirements-ccxt.txt
   
   # Install Alpaca API with --no-deps to avoid conflicts
   pip install -r requirements-alpaca.txt --no-deps
   
   # Optional: Install development dependencies
   pip install -r requirements-dev.txt
   
   # Optional: Install Backtrader for backtesting capabilities
   pip install -r requirements-backtrader.txt
   ```

   > **Note:** The project uses separate requirement files to manage dependency conflicts. This approach ensures that incompatible package versions don't cause runtime issues.

## Configuration

1. Create a `.env` file in the root directory with your API keys:
   ```
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_SECRET=your_binance_secret
   ALPACA_API_KEY=your_alpaca_api_key
   ALPACA_SECRET=your_alpaca_secret
   ```

2. Run database migrations:
   ```
   alembic upgrade head
   ```

## Running the Application

To start the application:

```
python main.py
```

You can use various command-line options:

```
python main.py --help
```

## Running Backtests

To run a backtest of your trading strategies:

```
python scripts/run_backtest.py --symbol BTC-USD --threshold 0.01
```

For more information on backtesting, see the [Backtesting Guide](../guides/howtoguides01.md).

## Docker Deployment

StreamScalp Pro can also be run using Docker:

1. Make sure you have Docker and Docker Compose installed on your system

2. Configure which requirements to install by editing the `docker-compose.yml` file:
   ```yaml
   build:
     context: .
     dockerfile: Dockerfile
     args:
       - INSTALL_ALPACA=true  # Set to false if not needed
       - INSTALL_CCXT=true    # Set to false if not needed
       - INSTALL_DEV=false    # Set to true for development environment
       - INSTALL_BACKTRADER=false  # Set to true for backtesting capabilities
   ```

3. Build and start the containers:
   ```
   docker-compose up -d
   ```

4. Access the dashboard at http://localhost:8000

5. To stop the containers:
   ```
   docker-compose down
   ```

The Docker setup handles dependency installation in the correct order to avoid conflicts, similar to the setup scripts.

## Troubleshooting

### Common Issues

#### Dependency Conflicts

If you encounter dependency conflicts:

1. Make sure you've installed dependencies using the provided setup scripts or followed the manual installation steps
2. Check for warning messages about incompatible packages
3. Consider creating a fresh virtual environment and reinstalling dependencies

#### Backtrader Installation Issues

If you encounter issues with Backtrader:

1. Ensure you have matplotlib installed correctly
2. For plotting issues, try installing a different backend: `pip install pyqt5`
3. If you see errors about missing indicators, check that you're using the correct version of Backtrader

#### Database Migration Errors

If you encounter errors during migration:

1. Ensure your database URL is correctly set in `config/settings.py`
2. For SQLite, make sure the directory is writable
3. For PostgreSQL, verify the database exists and credentials are correct

#### API Connection Issues

If you can't connect to exchanges:

1. Verify your API keys in the `.env` file
2. Check that your API keys have the necessary permissions
3. Ensure your network allows connections to the exchange APIs

For more troubleshooting help, see the [Troubleshooting Guide](../support/troubleshooting.md).
