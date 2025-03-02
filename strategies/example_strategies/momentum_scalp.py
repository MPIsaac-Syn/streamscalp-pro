from strategies.base_strategy import BaseStrategy

class MomentumScalpStrategy(BaseStrategy):
    def __init__(self, event_bus, symbol: str, threshold: float = 0.01):
        super().__init__(event_bus)
        self.symbol = symbol
        self.threshold = threshold
    
    async def execute(self, data: dict):
        if data['symbol'] == self.symbol:
            price_change = (data['last_price'] - data['open_price']) / data['open_price']
            if abs(price_change) > self.threshold:
                side = 'buy' if price_change > 0 else 'sell'
                await self.event_bus.publish('order_event', {
                    'symbol': self.symbol,
                    'side': side,
                    'quantity': 0.1  # Fixed size for demo
                })