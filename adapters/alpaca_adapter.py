import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST
from alpaca_trade_api.stream import Stream
from typing import Dict, Any, Optional, List
import asyncio
import logging

from .base_adapter import BaseAdapter

logger = logging.getLogger(__name__)

class AlpacaAdapter(BaseAdapter):
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://paper-api.alpaca.markets"):
        """
        Initialize Alpaca adapter with API credentials
        
        Args:
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            base_url: API base URL (paper or live)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        
        # Initialize REST client
        self.rest_client = REST(
            key_id=api_key,
            secret_key=api_secret,
            base_url=base_url
        )
        
        # Initialize streaming client
        self.stream_client = Stream(
            key_id=api_key,
            secret_key=api_secret,
            base_url=base_url,
            data_feed='iex'  # Use IEX for market data
        )
        
        self.connected = False
        self.account_info = None
        self.subscribed_symbols = set()
        self.data_callbacks = {}
    
    async def connect(self) -> bool:
        """Connect to Alpaca API and verify credentials"""
        if self.connected:
            return True
            
        try:
            # Test connection by getting account info
            self.account_info = self.rest_client.get_account()
            self.connected = True
            logger.info(f"Connected to Alpaca: {self.account_info.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {str(e)}")
            return False
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get latest market data for a symbol"""
        try:
            # Get latest bar
            bars = self.rest_client.get_latest_bar(symbol)
            
            # Get current quote
            quote = self.rest_client.get_latest_quote(symbol)
            
            return {
                'symbol': symbol,
                'bid': quote.bp if quote else None,
                'ask': quote.ap if quote else None,
                'last': bars.c if bars else None,
                'volume': bars.v if bars else None,
                'timestamp': bars.t if bars else None
            }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def subscribe_to_market_data(self, symbol: str, callback) -> bool:
        """Subscribe to real-time market data for a symbol"""
        if symbol in self.subscribed_symbols:
            return True
            
        try:
            # Add to subscribed symbols
            self.subscribed_symbols.add(symbol)
            self.data_callbacks[symbol] = callback
            
            # Define handlers
            async def on_bar(bar):
                if callback and symbol == bar.symbol:
                    await callback({
                        'type': 'bar',
                        'symbol': bar.symbol,
                        'open': bar.open,
                        'high': bar.high,
                        'low': bar.low,
                        'close': bar.close,
                        'volume': bar.volume,
                        'timestamp': bar.timestamp
                    })
            
            async def on_quote(quote):
                if callback and symbol == quote.symbol:
                    await callback({
                        'type': 'quote',
                        'symbol': quote.symbol,
                        'bid': quote.bid_price,
                        'ask': quote.ask_price,
                        'bid_size': quote.bid_size,
                        'ask_size': quote.ask_size,
                        'timestamp': quote.timestamp
                    })
            
            # Register handlers
            self.stream_client.subscribe_bars(on_bar, symbol)
            self.stream_client.subscribe_quotes(on_quote, symbol)
            
            # Start streaming if not already running
            if not self.stream_client.running:
                asyncio.create_task(self.stream_client.run())
                
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to {symbol}: {str(e)}")
            if symbol in self.subscribed_symbols:
                self.subscribed_symbols.remove(symbol)
            if symbol in self.data_callbacks:
                del self.data_callbacks[symbol]
            return False
    
    async def unsubscribe_from_market_data(self, symbol: str) -> bool:
        """Unsubscribe from market data for a symbol"""
        if symbol not in self.subscribed_symbols:
            return True
            
        try:
            # Remove from subscribed symbols
            self.subscribed_symbols.remove(symbol)
            if symbol in self.data_callbacks:
                del self.data_callbacks[symbol]
                
            # Note: Alpaca API doesn't have a direct way to unsubscribe
            # We just stop processing the callbacks
            
            return True
        except Exception as e:
            logger.error(f"Error unsubscribing from {symbol}: {str(e)}")
            return False
    
    async def create_order(self, symbol: str, side: str, quantity: float, **kwargs) -> Dict[str, Any]:
        """
        Create an order on Alpaca
        
        Args:
            symbol: Symbol to trade
            side: 'buy' or 'sell'
            quantity: Quantity to trade
            **kwargs: Additional parameters including:
                - order_type: 'market', 'limit', 'stop', 'stop_limit'
                - time_in_force: 'day', 'gtc', 'opg', 'cls', 'ioc', 'fok'
                - price: Limit price (for limit orders)
                - stop_price: Stop price (for stop orders)
        """
        try:
            # Ensure connection
            if not self.connected:
                await self.connect()
                
            # Map parameters
            order_type = kwargs.get('order_type', 'market')
            time_in_force = kwargs.get('time_in_force', 'gtc')
            limit_price = kwargs.get('price') if order_type in ['limit', 'stop_limit'] else None
            stop_price = kwargs.get('stop_price') if order_type in ['stop', 'stop_limit'] else None
            
            # Map order type to Alpaca format
            alpaca_order_type = {
                'market': 'market',
                'limit': 'limit',
                'stop': 'stop',
                'stop_limit': 'stop_limit'
            }.get(order_type, 'market')
            
            # Submit order
            order = self.rest_client.submit_order(
                symbol=symbol,
                qty=quantity,
                side=side,
                type=alpaca_order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price
            )
            
            # Map response to common format
            return {
                'id': order.id,
                'client_order_id': order.client_order_id,
                'symbol': order.symbol,
                'side': order.side,
                'type': order.type,
                'status': order.status,
                'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                'created_at': order.created_at,
                'updated_at': order.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error creating order for {symbol}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            # Ensure connection
            if not self.connected:
                await self.connect()
                
            # Cancel order
            self.rest_client.cancel_order(order_id)
            
            # Get updated order status
            order = self.rest_client.get_order(order_id)
            
            return {
                'id': order.id,
                'status': order.status,
                'canceled_at': order.canceled_at
            }
            
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get the status of an existing order"""
        try:
            # Ensure connection
            if not self.connected:
                await self.connect()
                
            # Get order
            order = self.rest_client.get_order(order_id)
            
            return {
                'id': order.id,
                'client_order_id': order.client_order_id,
                'symbol': order.symbol,
                'side': order.side,
                'type': order.type,
                'status': order.status,
                'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                'created_at': order.created_at,
                'updated_at': order.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting order status for {order_id}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions"""
        try:
            # Ensure connection
            if not self.connected:
                await self.connect()
                
            # Get positions
            positions = self.rest_client.list_positions()
            
            return [{
                'symbol': position.symbol,
                'qty': float(position.qty),
                'avg_entry_price': float(position.avg_entry_price),
                'market_value': float(position.market_value),
                'current_price': float(position.current_price),
                'unrealized_pl': float(position.unrealized_pl),
                'unrealized_plpc': float(position.unrealized_plpc),
                'side': 'long' if float(position.qty) > 0 else 'short'
            } for position in positions]
            
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            # Ensure connection
            if not self.connected:
                await self.connect()
                
            # Get account
            account = self.rest_client.get_account()
            
            return {
                'id': account.id,
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'initial_margin': float(account.initial_margin),
                'maintenance_margin': float(account.maintenance_margin),
                'daytrade_count': account.daytrade_count,
                'last_equity': float(account.last_equity),
                'status': account.status
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return {'status': 'error', 'error': str(e)}