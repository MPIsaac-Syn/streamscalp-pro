"""
Backtrader Integration Module for StreamScalp Pro.

This module provides integration between StreamScalp Pro strategies and the Backtrader
backtesting framework, allowing strategies to be tested on historical data before
deployment to live trading.
"""
import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import backtrader as bt
import datetime
import pandas as pd
import logging
import asyncio
from typing import Dict, Any, Type, List, Optional, Union

from strategies.base_strategy import BaseStrategy
from utils.logger import setup_logger

logger = setup_logger("backtrader_integration")

class BacktraderStrategyAdapter(bt.Strategy):
    """
    Adapter class that wraps StreamScalp Pro strategies for use with Backtrader.
    
    This adapter translates between Backtrader's event-driven model and
    StreamScalp Pro's strategy interface, allowing existing strategies to be
    used for backtesting without modification.
    """
    params = (
        ("strategy_class", None),  # Reference to the strategy class
        ("strategy_params", {}),   # Parameters for the strategy
        ("debug", False),          # Enable debug logging
    )

    def __init__(self):
        """Initialize the adapter with the provided strategy."""
        # Create a mock event bus for the strategy
        self.mock_event_bus = MockEventBus()
        
        # Instantiate the strategy with the mock event bus
        self.strategy = self.p.strategy_class(
            event_bus=self.mock_event_bus,
            **self.p.strategy_params
        )
        
        # Store orders and trades for analysis
        self.orders = []
        self.trades = []
        
        # Set up indicators if needed
        # This will depend on what indicators your strategies typically use
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
        
        if self.p.debug:
            logger.info(f"Initialized {self.p.strategy_class.__name__} with params: {self.p.strategy_params}")

    def next(self):
        """
        Process the next bar of data.
        
        This method is called by Backtrader for each new bar of data. It converts
        the Backtrader data to the format expected by StreamScalp Pro strategies,
        then calls the strategy's execute method.
        """
        # Convert Backtrader data to the format expected by the strategy
        data = {
            'symbol': self.data._name,
            'timestamp': bt.num2date(self.data.datetime[0]),
            'open_price': self.data.open[0],
            'high_price': self.data.high[0],
            'low_price': self.data.low[0],
            'last_price': self.data.close[0],
            'volume': self.data.volume[0] if hasattr(self.data, 'volume') else 0,
            # Add any other fields your strategies expect
        }
        
        # Call the strategy's execute method
        # Since execute is async, we need to handle it differently in a backtest
        # We'll use the synchronous version for backtesting
        self.mock_event_bus.reset_events()
        self.strategy.execute_sync(data)
        
        # Check if the strategy emitted any order events
        for event in self.mock_event_bus.get_events('order_event'):
            self._process_order_event(event)
    
    def _process_order_event(self, event: Dict[str, Any]):
        """Process an order event emitted by the strategy."""
        side = event.get('side', '').lower()
        quantity = event.get('quantity', 0)
        
        if side == 'buy' and quantity > 0:
            self.buy(size=quantity)
            if self.p.debug:
                logger.info(f"BUY {quantity} {event.get('symbol')} at {self.data.close[0]}")
        elif side == 'sell' and quantity > 0:
            self.sell(size=quantity)
            if self.p.debug:
                logger.info(f"SELL {quantity} {event.get('symbol')} at {self.data.close[0]}")
    
    def notify_order(self, order):
        """Called when an order status changes."""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            else:
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            
            self.orders.append({
                'timestamp': bt.num2date(self.data.datetime[0]),
                'type': 'buy' if order.isbuy() else 'sell',
                'price': order.executed.price,
                'size': order.executed.size,
                'value': order.executed.value,
                'commission': order.executed.comm
            })
    
    def notify_trade(self, trade):
        """Called when a trade is completed."""
        if trade.isclosed:
            self.log(f'TRADE CLOSED, PnL: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}')
            self.trades.append({
                'timestamp': bt.num2date(self.data.datetime[0]),
                'pnl': trade.pnl,
                'net_pnl': trade.pnlcomm,
                'price': trade.price,
                'size': trade.size
            })
    
    def log(self, txt, dt=None):
        """Log a message with timestamp."""
        if self.p.debug:
            dt = dt or bt.num2date(self.data.datetime[0])
            logger.info(f'{dt.isoformat()} {txt}')


class MockEventBus:
    """
    Mock implementation of the EventBus for backtesting.
    
    This class mimics the behavior of the real EventBus but stores events
    locally instead of publishing them to Redis.
    """
    def __init__(self):
        """Initialize an empty event store."""
        self.events = {}
    
    def reset_events(self):
        """Clear all stored events."""
        self.events = {}
    
    async def publish(self, event_type: str, data: Dict[str, Any]):
        """Store an event of the given type."""
        if event_type not in self.events:
            self.events[event_type] = []
        self.events[event_type].append(data)
        return True
    
    def publish_sync(self, event_type: str, data: Dict[str, Any]):
        """Synchronous version of publish for backtesting."""
        if event_type not in self.events:
            self.events[event_type] = []
        self.events[event_type].append(data)
        return True
    
    def get_events(self, event_type: str) -> List[Dict[str, Any]]:
        """Get all events of the given type."""
        return self.events.get(event_type, [])


# Add a synchronous version of execute to BaseStrategy for backtesting
def add_sync_execute_to_base_strategy():
    """
    Add a synchronous version of the execute method to BaseStrategy.
    
    This is needed because Backtrader is synchronous, but our strategies
    use async methods.
    """
    if not hasattr(BaseStrategy, 'execute_sync'):
        def execute_sync(self, data: Dict[str, Any]):
            """Synchronous version of execute for backtesting."""
            # Call the async execute method and extract the result
            # This is a simplified approach - in a real implementation,
            # you might want to use asyncio.run() or similar
            result = None
            try:
                # For backtesting, we'll use the publish_sync method of our mock event bus
                original_publish = self.event_bus.publish
                self.event_bus.publish = self.event_bus.publish_sync
                
                # Call the strategy's execute method
                # Handle both sync and async execute methods
                if asyncio.iscoroutinefunction(self.execute):
                    # If it's an async method, run it in a new event loop
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(self.execute(data))
                else:
                    self.execute(data)
                
                # Restore the original publish method
                self.event_bus.publish = original_publish
            except Exception as e:
                logger.error(f"Error executing strategy: {e}")
            
            return result
        
        # Add the method to the BaseStrategy class
        BaseStrategy.execute_sync = execute_sync


class CSVDataLoader:
    """
    Utility class for loading historical data from CSV files.
    
    This class provides methods for loading historical data from CSV files
    into a format that can be used by Backtrader.
    """
    @staticmethod
    def load_from_csv(filepath: str, 
                      timeframe: bt.TimeFrame = bt.TimeFrame.Days,
                      compression: int = 1,
                      **kwargs) -> bt.feeds.GenericCSVData:
        """
        Load historical data from a CSV file.
        
        Args:
            filepath: Path to the CSV file
            timeframe: Backtrader timeframe (default: Days)
            compression: Data compression (default: 1)
            **kwargs: Additional arguments for GenericCSVData
            
        Returns:
            Backtrader data feed
        """
        # Ensure the file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        # Default CSV format (can be overridden with kwargs)
        default_args = {
            'dataname': filepath,
            'timeframe': timeframe,  # Default to Minutes for yfinance data
            'compression': compression,
            
            # CSV format for yfinance data with index=True
            'datetime': 0,     # Column containing datetime (index)
            'open': 1,         # Column containing open price
            'high': 2,         # Column containing high price
            'low': 3,          # Column containing low price
            'close': 4,        # Column containing close price
            'adjclose': 5,     # Column containing adjusted close price
            'volume': 6,       # Column containing volume
            'openinterest': -1,  # Column containing open interest (-1 = not available)
            
            # Date parsing for yfinance data
            'dtformat': '%Y-%m-%d %H:%M:%S%z',  # Format for datetime index from yfinance
            'sessionstart': datetime.time(9, 30),  # Market open time
            'sessionend': datetime.time(16, 0),    # Market close time
        }
        
        # Override defaults with any provided kwargs
        args = {**default_args, **kwargs}
        
        # Create and return the data feed
        return bt.feeds.GenericCSVData(**args)


class BacktestRunner:
    """
    Main class for running backtests with StreamScalp Pro strategies.
    
    This class provides methods for setting up and running backtests,
    as well as analyzing the results.
    """
    def __init__(self, 
                 initial_cash: float = 10000.0,
                 commission: float = 0.001,
                 debug: bool = False):
        """
        Initialize the backtest runner.
        
        Args:
            initial_cash: Initial cash amount (default: 10000.0)
            commission: Commission rate (default: 0.001 = 0.1%)
            debug: Enable debug logging (default: False)
        """
        # Ensure the sync execute method is available
        add_sync_execute_to_base_strategy()
        
        self.initial_cash = initial_cash
        self.commission = commission
        self.debug = debug
        self.cerebro = bt.Cerebro()
        
        # Set up the broker
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.broker.setcommission(commission=commission)
        
        # Add analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        self.data_feeds = []
    
    def add_strategy(self, 
                     strategy_class: Type[BaseStrategy], 
                     strategy_params: Dict[str, Any] = None):
        """
        Add a strategy to the backtest.
        
        Args:
            strategy_class: The strategy class to backtest
            strategy_params: Parameters for the strategy (default: None)
        """
        if strategy_params is None:
            strategy_params = {}
        
        self.cerebro.addstrategy(
            BacktraderStrategyAdapter,
            strategy_class=strategy_class,
            strategy_params=strategy_params,
            debug=self.debug
        )
        
        logger.info(f"Added strategy: {strategy_class.__name__} with params: {strategy_params}")
    
    def add_data(self, data_feed: bt.feeds.DataBase, name: str = None):
        """
        Add a data feed to the backtest.
        
        Args:
            data_feed: Backtrader data feed
            name: Name for the data feed (default: None)
        """
        if name:
            data_feed._name = name
        
        self.cerebro.adddata(data_feed)
        self.data_feeds.append(data_feed)
        
        logger.info(f"Added data feed: {name or 'unnamed'}")
    
    def add_csv_data(self, 
                     filepath: str, 
                     name: str = None, 
                     timeframe: bt.TimeFrame = bt.TimeFrame.Minutes,
                     compression: int = 1,
                     **kwargs):
        """
        Add data from a CSV file to the backtest.
        
        Args:
            filepath: Path to the CSV file
            name: Name for the data feed (default: None)
            timeframe: Backtrader timeframe (default: Minutes)
            compression: Data compression (default: 1)
            **kwargs: Additional arguments for GenericCSVData
        """
        data_feed = CSVDataLoader.load_from_csv(
            filepath=filepath,
            timeframe=timeframe,
            compression=compression,
            **kwargs
        )
        
        self.add_data(data_feed, name or Path(filepath).stem)
    
    def run(self) -> Dict[str, Any]:
        """
        Run the backtest and return the results.
        
        Returns:
            Dictionary containing backtest results
        """
        if not self.data_feeds:
            raise ValueError("No data feeds added to the backtest")
        
        logger.info(f"Starting backtest with {len(self.data_feeds)} data feeds")
        logger.info(f"Initial cash: ${self.initial_cash:.2f}, Commission: {self.commission:.4f}")
        
        # Run the backtest
        results = self.cerebro.run()
        strat = results[0]
        
        # Extract results
        portfolio_value = self.cerebro.broker.getvalue()
        returns = (portfolio_value / self.initial_cash - 1.0) * 100
        
        # Get analyzer results
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        returns_analyzer = strat.analyzers.returns.get_analysis() if hasattr(strat.analyzers, 'returns') else {}
        trades_analyzer = strat.analyzers.trades.get_analysis() if hasattr(strat.analyzers, 'trades') else {}
        
        # Compile results
        results_dict = {
            'initial_cash': self.initial_cash,
            'final_value': portfolio_value,
            'returns_pct': returns,
            'sharpe_ratio': sharpe.get('sharperatio', 0.0) if hasattr(sharpe, 'get') and sharpe is not None else 0.0,
            'max_drawdown_pct': drawdown.get('max', {}).get('drawdown', 0.0) * 100 if hasattr(drawdown, 'get') and drawdown is not None else 0.0,
            'trades': {
                'total': trades_analyzer.get('total', {}).get('total', 0) if hasattr(trades_analyzer, 'get') and trades_analyzer is not None else 0,
                'won': trades_analyzer.get('won', {}).get('total', 0) if hasattr(trades_analyzer, 'get') and trades_analyzer is not None else 0,
                'lost': trades_analyzer.get('lost', {}).get('total', 0) if hasattr(trades_analyzer, 'get') and trades_analyzer is not None else 0,
            },
            'orders': strat.orders,
            'trades_detail': strat.trades,
        }
        
        # Log results with null checks
        logger.info(f"Backtest completed. Final value: ${portfolio_value:.2f}, Returns: {returns:.2f}%")
        
        # Handle None values in logging
        sharpe_ratio = results_dict['sharpe_ratio'] or 0.0
        max_drawdown = results_dict['max_drawdown_pct'] or 0.0
        logger.info(f"Sharpe Ratio: {sharpe_ratio:.4f}, Max Drawdown: {max_drawdown:.2f}%")
        
        total_trades = results_dict['trades']['total'] or 0
        won_trades = results_dict['trades']['won'] or 0
        lost_trades = results_dict['trades']['lost'] or 0
        logger.info(f"Trades: {total_trades} total, {won_trades} won, {lost_trades} lost")
        
        return results_dict
    
    def plot(self, 
             filename: str = None, 
             **kwargs):
        """
        Plot the backtest results.
        
        Args:
            filename: Path to save the plot (default: None, display only)
            **kwargs: Additional arguments for plot
        """
        try:
            import matplotlib.pyplot as plt
            
            # Default plot arguments
            default_args = {
                'style': 'candle',
                'barup': 'green',
                'bardown': 'red',
                'volup': 'green',
                'voldown': 'red',
                'plotdist': 0.1,
                'width': 16,
                'height': 9,
            }
            
            # Override defaults with any provided kwargs
            args = {**default_args, **kwargs}
            
            # Create the plot
            figs = self.cerebro.plot(**args)
            
            # Save the plot if a filename is provided
            if filename:
                for i, fig in enumerate(figs):
                    for j, subfig in enumerate(fig):
                        subfig.savefig(f"{filename}_{i}_{j}.png")
            
            # Show the plot
            plt.show()
            
        except Exception as e:
            logger.error(f"Error plotting results: {e}")


# Example usage
if __name__ == "__main__":
    from strategies.example_strategies.momentum_scalp import MomentumScalpStrategy
    
    # Create a backtest runner with debug enabled
    runner = BacktestRunner(initial_cash=10000.0, commission=0.001, debug=True)
    
    # Add a strategy
    runner.add_strategy(
        strategy_class=MomentumScalpStrategy,
        strategy_params={
            "symbol": "BTCUSDT",
            "threshold": 0.01
        }
    )
    
    # Add data from the CSV file generated by get_history_csv.py
    try:
        runner.add_csv_data(
            filepath="historical_data.csv",
            name="AAPL",
            timeframe=bt.TimeFrame.Minutes
        )
        print("Successfully loaded historical_data.csv")
    except FileNotFoundError:
        print("historical_data.csv not found. Run scripts/get_history_csv.py first.")
    
    # Alternatively, use Backtrader's built-in Yahoo Finance data
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