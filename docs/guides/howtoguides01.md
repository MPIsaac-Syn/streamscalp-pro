# Backtesting Strategies with Backtrader

This guide explains how to use the Backtrader integration in StreamScalp Pro to backtest your trading strategies on historical data before deploying them to live trading.

## Overview

Backtesting is a crucial step in strategy development that allows you to evaluate how your strategy would have performed in the past. StreamScalp Pro integrates with [Backtrader](https://www.backtrader.com/), a popular Python framework for backtesting trading strategies.

The integration allows you to:

- Test existing StreamScalp Pro strategies on historical data
- Analyze performance metrics like returns, Sharpe ratio, and drawdowns
- Visualize trade entries, exits, and equity curves
- Optimize strategy parameters

## Installation

To use the Backtrader integration, you need to install the required dependencies:

1. Install the Backtrader dependencies:
   ```bash
   pip install -r requirements-backtrader.txt
   ```

2. If you encounter installation issues with matplotlib (especially on macOS), try:
   ```bash
   pip install matplotlib==3.6.3  # Use a specific version known to work
   pip install pyqt5  # Alternative backend for matplotlib
   ```

This will install Backtrader and its dependencies, including matplotlib for plotting.

## Basic Usage

The simplest way to run a backtest is to use the provided `run_backtest.py` script:

```bash
python scripts/run_backtest.py --symbol BTC-USD --threshold 0.01
```

This will run a backtest of the MomentumScalpStrategy on BTC-USD data from Yahoo Finance for the year 2020, with a price change threshold of 1%.

### Command Line Options

The script supports several command line options:

- `--symbol`: Symbol to backtest (default: BTC-USD)
- `--threshold`: Price change threshold for momentum strategy (default: 0.01)
- `--cash`: Initial cash amount (default: 10000.0)
- `--commission`: Commission rate (default: 0.001 = 0.1%)
- `--start-date`: Start date for backtest (default: 2020-01-01)
- `--end-date`: End date for backtest (default: 2020-12-31)
- `--csv-file`: Path to CSV file with historical data (optional)
- `--output-dir`: Directory to save results (default: backtest_results)
- `--debug`: Enable debug logging
- `--no-plot`: Disable plotting

### Using CSV Data

If you have historical data in CSV format, you can use it instead of Yahoo Finance data:

```bash
python scripts/run_backtest.py --symbol BTCUSDT --csv-file data/BTCUSDT_1d.csv
```

The CSV file should have columns for datetime, open, high, low, close, and volume. By default, the script expects these columns to be in positions 0, 1, 2, 3, 4, and 5 respectively.

## Advanced Usage

For more advanced usage, you can create your own scripts that use the `BacktestRunner` class directly. This allows for more customization and integration with other parts of your application.

### Creating a Custom Backtest

Here's an example of how to create a custom backtest:

```python
import datetime
import backtrader as bt
from strategies.backtrader_integration import BacktestRunner
from strategies.example_strategies.momentum_scalp import MomentumScalpStrategy

# Create a backtest runner
runner = BacktestRunner(initial_cash=10000.0, commission=0.001, debug=True)

# Add a strategy
runner.add_strategy(
    strategy_class=MomentumScalpStrategy,
    strategy_params={
        "symbol": "BTCUSDT",
        "threshold": 0.01
    }
)

# Add data
data = bt.feeds.YahooFinanceData(
    dataname="BTC-USD",
    fromdate=datetime.datetime(2020, 1, 1),
    todate=datetime.datetime(2020, 12, 31)
)
runner.add_data(data, name="BTCUSDT")

# Run the backtest
results = runner.run()

# Plot the results
runner.plot()

# Print summary
print(f"Initial cash: ${results['initial_cash']:.2f}")
print(f"Final value: ${results['final_value']:.2f}")
print(f"Returns: {results['returns_pct']:.2f}%")
print(f"Sharpe ratio: {results['sharpe_ratio']:.4f}")
print(f"Max drawdown: {results['max_drawdown_pct']:.2f}%")
print(f"Trades: {results['trades']['total']} total, {results['trades']['won']} won, {results['trades']['lost']} lost")
```

### Testing Custom Strategies

To test your own custom strategies, simply import them and pass them to the `add_strategy` method:

```python
from strategies.my_strategies.my_custom_strategy import MyCustomStrategy

runner.add_strategy(
    strategy_class=MyCustomStrategy,
    strategy_params={
        "symbol": "BTCUSDT",
        "param1": 10,
        "param2": 0.05
    }
)
```

Your custom strategy must inherit from `BaseStrategy` and implement the `execute` method.

### Loading Data from Different Sources

The `BacktestRunner` class supports loading data from different sources:

1. CSV files:

```python
runner.add_csv_data(
    filepath="data/BTCUSDT_1d.csv",
    name="BTCUSDT",
    timeframe=bt.TimeFrame.Days,
    dtformat="%Y-%m-%d"
)
```

2. Pandas DataFrames:

```python
import pandas as pd
import backtrader as bt

# Load data from a DataFrame
df = pd.read_csv("data/BTCUSDT_1d.csv")
data = bt.feeds.PandasData(
    dataname=df,
    datetime='date',
    open='open',
    high='high',
    low='low',
    close='close',
    volume='volume',
    openinterest=-1
)
runner.add_data(data, name="BTCUSDT")
```

3. Other Backtrader data feeds:

```python
# Use any Backtrader data feed
data = bt.feeds.GenericCSVData(
    dataname="data/BTCUSDT_1d.csv",
    dtformat="%Y-%m-%d",
    # ... other parameters
)
runner.add_data(data, name="BTCUSDT")
```

## Understanding the Results

The `run` method of the `BacktestRunner` class returns a dictionary with the following keys:

- `initial_cash`: Initial cash amount
- `final_value`: Final portfolio value
- `returns_pct`: Percentage returns
- `sharpe_ratio`: Sharpe ratio
- `max_drawdown_pct`: Maximum drawdown percentage
- `trades`: Dictionary with trade statistics
  - `total`: Total number of trades
  - `won`: Number of winning trades
  - `lost`: Number of losing trades
- `orders`: List of all orders executed
- `trades_detail`: List of all trades with PnL information

You can use this information to evaluate the performance of your strategy and make improvements.

## Adapting Strategies for Backtrader

The `BacktraderStrategyAdapter` class adapts StreamScalp Pro strategies to work with Backtrader. It handles the conversion between Backtrader's event-driven model and StreamScalp Pro's strategy interface.

If your strategy requires special handling, you can create a custom adapter by subclassing `BacktraderStrategyAdapter` and overriding the necessary methods.

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Make sure you have installed all required dependencies with `pip install -r requirements-backtrader.txt`. 

2. **Data format issues**: If you're using CSV data, make sure the format matches what the `CSVDataLoader` expects. You may need to adjust the column mappings.

3. **Matplotlib installation issues**: If you encounter errors installing matplotlib (especially on macOS):
   ```bash
   # Try installing a specific version
   pip install matplotlib==3.6.3
   
   # Install build dependencies if needed
   pip install wheel setuptools
   pip install --upgrade pip
   ```

4. **Import errors**: If you encounter errors like "Import 'backtrader' could not be resolved" or "Import 'pandas' could not be resolved", make sure you've installed all dependencies:
   ```bash
   pip install -r requirements-backtrader.txt
   ```
   Note that pandas is already included in requirements-base.txt, but is also listed in requirements-backtrader.txt for clarity.

5. **Plotting issues**: If you encounter problems with plotting:
   ```bash
   # Install an alternative backend
   pip install pyqt5
   ```
   You can also try running without plotting by using the `--no-plot` flag with the `run_backtest.py` script.

### Debugging

To enable debug logging, pass `debug=True` to the `BacktestRunner` constructor or use the `--debug` flag with the `run_backtest.py` script.

This will print detailed information about the backtest execution, including strategy initialization, data processing, and trade execution.

## Next Steps

- **Parameter optimization**: Try different parameter values to find the optimal settings for your strategy.
- **Multi-asset backtesting**: Test your strategy on multiple assets simultaneously.
- **Custom indicators**: Implement custom indicators for your strategies.
- **Walk-forward testing**: Implement walk-forward testing to evaluate strategy robustness.
