import ccxt.async_support as ccxt
from .base_adapter import BaseAdapter
from typing import Optional, Dict, Any

class BinanceAdapter(BaseAdapter):
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Binance adapter with API credentials.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.client = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })
        self.connected = False
        self.subscribed_symbols = set()

    async def connect(self) -> None:
        """
        Connect to Binance API and load markets.
        """
        if not self.connected:
            await self.client.load_markets()
            self.connected = True
            
    async def disconnect(self) -> None:
        """
        Disconnect from Binance API.
        """
        if self.connected:
            await self.client.close()
            self.connected = False

    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get market data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Dictionary with market data
        """
        if not self.connected:
            await self.connect()
            
        try:
            ticker = await self.client.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'volume': ticker['volume'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            # Log error and return minimal data
            return {
                'symbol': symbol,
                'error': str(e)
            }

    async def create_order(self, symbol: str, side: str, quantity: float, **kwargs) -> Dict[str, Any]:
        """
        Create a new order on Binance.
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('buy' or 'sell')
            quantity: Order quantity
            **kwargs: Additional parameters (order_type, price, etc.)
            
        Returns:
            Dictionary with order details
        """
        if not self.connected:
            await self.connect()
            
        order_type = kwargs.get('order_type', 'market')
        
        try:
            return await self.client.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=quantity,
                price=kwargs.get('price')
            )
        except Exception as e:
            # Log error and return error information
            return {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'status': 'error',
                'error': str(e)
            }

    async def cancel_order(self, order_id: str, symbol: str = None) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading pair symbol (required by some exchanges)
            
        Returns:
            Dictionary with cancellation result
        """
        if not self.connected:
            await self.connect()
            
        try:
            return await self.client.cancel_order(order_id, symbol)
        except Exception as e:
            # Log error and return error information
            return {
                'order_id': order_id,
                'status': 'error',
                'error': str(e)
            }

    async def get_order_status(self, order_id: str, symbol: str = None) -> Dict[str, Any]:
        """
        Get the status of an existing order.
        
        Args:
            order_id: Order ID to check
            symbol: Trading pair symbol (required by some exchanges)
            
        Returns:
            Dictionary with order status
        """
        if not self.connected:
            await self.connect()
            
        try:
            return await self.client.fetch_order(order_id, symbol)
        except Exception as e:
            # Log error and return error information
            return {
                'order_id': order_id,
                'status': 'error',
                'error': str(e)
            }
            
    async def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance.
        
        Returns:
            Dictionary with balance information
        """
        if not self.connected:
            await self.connect()
            
        try:
            return await self.client.fetch_balance()
        except Exception as e:
            # Log error and return error information
            return {
                'status': 'error',
                'error': str(e)
            }