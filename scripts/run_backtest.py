#!/usr/bin/env python
"""
StreamScalp Pro - Backtesting Script
Runs a backtest using Backtrader with local CSV data or Binance API data.
"""

import sys
import os
import datetime
import argparse
import pandas as pd
import backtrader as bt
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.backtrader_integration import BacktestRunner
from strategies.example_strategies.momentum_scalp import MomentumScalpStrategy


# 🔹 Function to fetch historical OHLCV data using CCXT (Binance)
def fetch_binance_data(symbol, timeframe="1m", limit=1000):
    import ccxt
    exchange = ccxt.binanceus()
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    # Convert to Pandas DataFrame
    df = pd.DataFrame(
        bars, columns=["datetime", "open", "high", "low", "close", "volume"]
    )
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")  # Convert timestamp
    df.set_index("datetime", inplace=True)  # Set index for Backtrader compatibility

    return df


# 🔹 Command-line argument parser
def parse_args():
    parser = argparse.ArgumentParser(description="Run a backtest with StreamScalp Pro strategies")

    parser.add_argument("--symbol", type=str, default="AAPL",
                        help="Symbol to backtest (default: AAPL)")
    parser.add_argument("--threshold", type=float, default=0.01,
                        help="Price change threshold for momentum strategy (default: 0.01)")
    parser.add_argument("--cash", type=float, default=10000.0,
                        help="Initial cash amount (default: 10000.0)")
    parser.add_argument("--commission", type=float, default=0.001,
                        help="Commission rate (default: 0.001 = 0.1%)")
    parser.add_argument("--start-date", type=str, default="2024-01-01",
                        help="Start date for backtest (default: 2024-01-01)")
    parser.add_argument("--end-date", type=str, default="2024-12-31",
                        help="End date for backtest (default: 2024-12-31)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("--no-plot", action="store_true",
                        help="Disable plotting")
    parser.add_argument("--data-source", type=str, choices=["csv", "binance"], default="csv",
                        help="Data source to use (csv or binance, default: csv)")
    parser.add_argument("--csv-file", type=str, default="historical_data.csv",
                        help="CSV file to use for backtesting (default: historical_data.csv)")

    return parser.parse_args()


# 🔹 Main function to run backtest
def main():
    args = parse_args()
    
    # Create a backtest runner
    runner = BacktestRunner(
        initial_cash=args.cash,
        commission=args.commission,
        debug=args.debug
    )
    
    # Add the strategy
    runner.add_strategy(
        strategy_class=MomentumScalpStrategy,
        strategy_params={
            "symbol": args.symbol,
            "threshold": args.threshold
        }
    )
    
    # Load data based on the selected source
    if args.data_source == "csv":
        csv_path = args.csv_file
        if not os.path.isabs(csv_path):
            # If not an absolute path, assume it's relative to the project root
            project_root = Path(__file__).parent.parent
            csv_path = os.path.join(project_root, csv_path)
        
        if not os.path.exists(csv_path):
            print(f"❌ Error: CSV file not found: {csv_path}")
            print("   Run 'python scripts/get_history_csv.py' to generate the file first.")
            return
        
        print(f"🔄 Loading data from CSV file: {csv_path}")
        
        # Add CSV data with correct column mappings for our format
        runner.add_csv_data(
            filepath=csv_path,
            name=args.symbol,
            timeframe=bt.TimeFrame.Minutes,
            
            # Column mappings for our CSV format
            datetime=0,     # Datetime column
            open=2,         # Open price column
            high=3,         # High price column
            low=4,          # Low price column
            close=5,        # Close price column
            volume=6,       # Volume column
            openinterest=-1,  # No open interest column
            
            # Skip the header row
            headers=True,
            
            # Date format in our CSV
            dtformat="%Y-%m-%d %H:%M:%S%z"
        )
    else:  # binance
        print(f"🔄 Fetching {args.symbol} historical data from Binance...")
        df = fetch_binance_data(args.symbol)
        
        # Convert Pandas DataFrame to Backtrader Data Feed
        data = bt.feeds.PandasData(dataname=df)
        runner.add_data(data, name=args.symbol)
    
    print(f"🚀 Starting backtest for {args.symbol} with initial cash: ${args.cash:,.2f}")
    
    # Run the backtest
    results = runner.run()
    
    # Print summary
    print("\n📊 Backtest Results:")
    print(f"Initial cash: ${results['initial_cash']:.2f}")
    print(f"Final value: ${results['final_value']:.2f}")
    print(f"Returns: {results['returns_pct']:.2f}%")
    
    # Handle None values in results
    sharpe_ratio = results['sharpe_ratio'] or 0.0
    max_drawdown = results['max_drawdown_pct'] or 0.0
    total_trades = results['trades']['total'] or 0
    won_trades = results['trades']['won'] or 0
    lost_trades = results['trades']['lost'] or 0
    
    print(f"Sharpe ratio: {sharpe_ratio:.4f}")
    print(f"Max drawdown: {max_drawdown:.2f}%")
    print(f"Trades: {total_trades} total, {won_trades} won, {lost_trades} lost")
    
    # Plot the results if not disabled
    if not args.no_plot:
        print("\n📈 Generating plot...")
        runner.plot()


if __name__ == "__main__":
    main()
