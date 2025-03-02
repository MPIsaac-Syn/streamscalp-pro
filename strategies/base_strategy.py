from abc import ABC, abstractmethod
from utils.event_bus import EventBus

class BaseStrategy(ABC):
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    @abstractmethod
    async def execute(self, data: dict):
        """Process market data and emit orders"""
        pass