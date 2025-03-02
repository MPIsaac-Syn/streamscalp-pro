from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str) -> dict:
        pass
    
    @abstractmethod
    async def create_order(self, symbol: str, side: str, quantity: float, **kwargs) -> dict:
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> dict:
        pass
    
    async def disconnect(self):
        pass