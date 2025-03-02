import unittest
import asyncio
import os
import json
from unittest.mock import patch, MagicMock

from adapters.binance_adapter import BinanceAdapter
from adapters.alpaca_adapter import AlpacaAdapter

class TestBinanceAdapter(unittest.TestCase):
    def setUp(self):
        # Use test API keys or mock values
        self.api_key = os.environ.get("TEST_BINANCE_API_KEY", "test_key")
        self.api_secret = os.environ.get("TEST_BINANCE_API_SECRET", "test_secret")
        
        # Create adapter with mock CCXT
        with patch('ccxt.binance') as mock_binance:
            self.mock_client = MagicMock()
            mock_binance.return_value = self.mock_client
            self.adapter = BinanceAdapter(self.api_key, self.api_secret)
    
    def test_initialization(self):
        """Test adapter initialization"""
        self.assertEqual(self.adapter.client, self.mock_client)
        self.assertFalse(self.adapter.connected)
    
    def test_connect(self):
        """Test connect method"""
        # Setup mock
        self.mock_client.load_markets = MagicMock(return_value=None)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.connect())
        
        # Verify
        self.mock_client.load_markets.assert_called_once()
        self.assertTrue(self.adapter.connected)
        self.assertTrue(result)
    
    def test_get_market_data(self):
        """Test get_market_data method"""
        # Setup mock
        mock_ticker = {
            'bid': 50000.0,
            'ask': 50100.0,
            'last': 50050.0
        }
        self.mock_client.fetch_ticker = MagicMock(return_value=mock_ticker)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.get_market_data("BTCUSDT"))
        
        # Verify
        self.mock_client.fetch_ticker.assert_called_once_with("BTCUSDT")
        self.assertEqual(result['symbol'], "BTCUSDT")
        self.assertEqual(result['bid'], 50000.0)
        self.assertEqual(result['ask'], 50100.0)
        self.assertEqual(result['last'], 50050.0)
    
    def test_create_order(self):
        """Test create_order method"""
        # Setup mock
        mock_order_result = {
            'id': '12345',
            'status': 'filled',
            'filled': 0.1,
            'price': 50000.0
        }
        self.mock_client.create_order = MagicMock(return_value=mock_order_result)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.create_order(
            symbol="BTCUSDT",
            side="buy",
            quantity=0.1,
            order_type="market"
        ))
        
        # Verify
        self.mock_client.create_order.assert_called_once_with(
            symbol="BTCUSDT",
            type="market",
            side="buy",
            amount=0.1,
            price=None
        )
        self.assertEqual(result, mock_order_result)
    
    def test_cancel_order(self):
        """Test cancel_order method"""
        # Setup mock
        self.mock_client.cancel_order = MagicMock(return_value=True)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.cancel_order("12345"))
        
        # Verify
        self.mock_client.cancel_order.assert_called_once_with("12345")
        self.assertTrue(result)
    
    def test_get_order_status(self):
        """Test get_order_status method"""
        # Setup mock
        mock_order = {
            'id': '12345',
            'status': 'filled',
            'filled': 0.1,
            'price': 50000.0
        }
        self.mock_client.fetch_order = MagicMock(return_value=mock_order)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.get_order_status("12345"))
        
        # Verify
        self.mock_client.fetch_order.assert_called_once_with("12345")
        self.assertEqual(result, mock_order)


class TestAlpacaAdapter(unittest.TestCase):
    def setUp(self):
        # Use test API keys or mock values
        self.api_key = os.environ.get("TEST_ALPACA_API_KEY", "test_key")
        self.api_secret = os.environ.get("TEST_ALPACA_API_SECRET", "test_secret")
        
        # Create adapter with mocked Alpaca API
        with patch('alpaca_trade_api.rest.REST') as mock_rest, \
             patch('alpaca_trade_api.stream.Stream') as mock_stream:
            
            self.mock_rest_client = MagicMock()
            self.mock_stream_client = MagicMock()
            mock_rest.return_value = self.mock_rest_client
            mock_stream.return_value = self.mock_stream_client
            
            self.adapter = AlpacaAdapter(self.api_key, self.api_secret)
    
    def test_initialization(self):
        """Test adapter initialization"""
        self.assertEqual(self.adapter.rest_client, self.mock_rest_client)
        self.assertEqual(self.adapter.stream_client, self.mock_stream_client)
        self.assertFalse(self.adapter.connected)
        self.assertEqual(self.adapter.subscribed_symbols, set())
    
    def test_connect(self):
        """Test connect method"""
        # Setup mock
        mock_account = MagicMock()
        mock_account.id = "test_account_id"
        self.mock_rest_client.get_account = MagicMock(return_value=mock_account)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.connect())
        
        # Verify
        self.mock_rest_client.get_account.assert_called_once()
        self.assertTrue(self.adapter.connected)
        self.assertEqual(self.adapter.account_info, mock_account)
        self.assertTrue(result)
    
    def test_get_market_data(self):
        """Test get_market_data method"""
        # Setup mocks
        mock_bar = MagicMock()
        mock_bar.c = 50050.0
        mock_bar.v = 100.0
        mock_bar.t = "2023-01-01T00:00:00Z"
        
        mock_quote = MagicMock()
        mock_quote.bp = 50000.0
        mock_quote.ap = 50100.0
        
        self.mock_rest_client.get_latest_bar = MagicMock(return_value=mock_bar)
        self.mock_rest_client.get_latest_quote = MagicMock(return_value=mock_quote)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.get_market_data("AAPL"))
        
        # Verify
        self.mock_rest_client.get_latest_bar.assert_called_once_with("AAPL")
        self.mock_rest_client.get_latest_quote.assert_called_once_with("AAPL")
        self.assertEqual(result['symbol'], "AAPL")
        self.assertEqual(result['bid'], 50000.0)
        self.assertEqual(result['ask'], 50100.0)
        self.assertEqual(result['last'], 50050.0)
        self.assertEqual(result['volume'], 100.0)
        self.assertEqual(result['timestamp'], "2023-01-01T00:00:00Z")
    
    def test_create_order(self):
        """Test create_order method"""
        # Setup mock
        mock_order = MagicMock()
        mock_order.id = "order123"
        mock_order.client_order_id = "client_order123"
        mock_order.symbol = "AAPL"
        mock_order.side = "buy"
        mock_order.type = "market"
        mock_order.status = "filled"
        mock_order.filled_qty = "10"
        mock_order.filled_avg_price = "150.0"
        mock_order.created_at = "2023-01-01T00:00:00Z"
        mock_order.updated_at = "2023-01-01T00:00:01Z"
        
        self.mock_rest_client.submit_order = MagicMock(return_value=mock_order)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.create_order(
            symbol="AAPL",
            side="buy",
            quantity=10,
            order_type="market"
        ))
        
        # Verify
        self.mock_rest_client.submit_order.assert_called_once_with(
            symbol="AAPL",
            qty=10,
            side="buy",
            type="market",
            time_in_force="gtc",
            limit_price=None,
            stop_price=None
        )
        
        self.assertEqual(result['id'], "order123")
        self.assertEqual(result['symbol'], "AAPL")
        self.assertEqual(result['side'], "buy")
        self.assertEqual(result['type'], "market")
        self.assertEqual(result['status'], "filled")
        self.assertEqual(result['filled_qty'], 10.0)
        self.assertEqual(result['filled_avg_price'], 150.0)
    
    def test_cancel_order(self):
        """Test cancel_order method"""
        # Setup mocks
        self.mock_rest_client.cancel_order = MagicMock()
        
        mock_order = MagicMock()
        mock_order.id = "order123"
        mock_order.status = "canceled"
        mock_order.canceled_at = "2023-01-01T00:00:02Z"
        
        self.mock_rest_client.get_order = MagicMock(return_value=mock_order)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.cancel_order("order123"))
        
        # Verify
        self.mock_rest_client.cancel_order.assert_called_once_with("order123")
        self.mock_rest_client.get_order.assert_called_once_with("order123")
        self.assertEqual(result['id'], "order123")
        self.assertEqual(result['status'], "canceled")
        self.assertEqual(result['canceled_at'], "2023-01-01T00:00:02Z")
    
    def test_get_account_info(self):
        """Test get_account_info method"""
        # Setup mock
        mock_account = MagicMock()
        mock_account.id = "account123"
        mock_account.cash = "10000.0"
        mock_account.portfolio_value = "15000.0"
        mock_account.equity = "15000.0"
        mock_account.buying_power = "30000.0"
        mock_account.initial_margin = "5000.0"
        mock_account.maintenance_margin = "4000.0"
        mock_account.daytrade_count = 2
        mock_account.last_equity = "14500.0"
        mock_account.status = "ACTIVE"
        
        self.mock_rest_client.get_account = MagicMock(return_value=mock_account)
        
        # Run test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.adapter.get_account_info())
        
        # Verify
        self.mock_rest_client.get_account.assert_called_once()
        self.assertEqual(result['id'], "account123")
        self.assertEqual(result['cash'], 10000.0)
        self.assertEqual(result['portfolio_value'], 15000.0)
        self.assertEqual(result['equity'], 15000.0)
        self.assertEqual(result['buying_power'], 30000.0)
        self.assertEqual(result['status'], "ACTIVE")


if __name__ == "__main__":
    unittest.main()
