"""
Configuration for pytest.
"""
import os
import sys
import pytest

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables for testing
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("LOG_DIR", "./logs")

# Exchange credentials for testing
os.environ.setdefault("BINANCE_API_KEY", "test_binance_key")
os.environ.setdefault("BINANCE_API_SECRET", "test_binance_secret")
os.environ.setdefault("BINANCE_TESTNET", "true")

os.environ.setdefault("BINANCE_FUTURES_API_KEY", "test_binance_futures_key")
os.environ.setdefault("BINANCE_FUTURES_API_SECRET", "test_binance_futures_secret")
os.environ.setdefault("BINANCE_FUTURES_TESTNET", "false")

os.environ.setdefault("ALPACA_API_KEY", "test_alpaca_key")
os.environ.setdefault("ALPACA_API_SECRET", "test_alpaca_secret")
os.environ.setdefault("ALPACA_PAPER", "true")
