"""
Adapters module for connecting to various trading platforms.
"""

from .base_adapter import BaseAdapter
from .binance_adapter import BinanceAdapter
from .alpaca_adapter import AlpacaAdapter

__all__ = ['BaseAdapter', 'BinanceAdapter', 'AlpacaAdapter']
