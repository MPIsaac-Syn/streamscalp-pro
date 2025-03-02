# utils/event_bus.py
import redis.asyncio
import json
from typing import Dict, Any, AsyncGenerator, Optional
import asyncio
from enum import Enum
from datetime import datetime

class EventBus:
    def __init__(self, redis: redis.asyncio.Redis):
        """
        Initialize the event bus with a Redis connection.
        
        Args:
            redis: Redis connection pool
        """
        self.redis = redis
        self.pubsub = None
        self.connected = False
    
    async def connect(self) -> None:
        """
        Connect to Redis and initialize the pubsub client.
        """
        if not self.connected:
            self.pubsub = self.redis.pubsub()
            self.connected = True
    
    async def disconnect(self) -> None:
        """
        Disconnect from Redis.
        """
        if self.connected and self.pubsub:
            await self.pubsub.close()
            self.connected = False
    
    async def publish(self, channel: str, message: Dict[str, Any]) -> None:
        """
        Publish a message to a channel.
        
        Args:
            channel: Channel to publish to
            message: Message to publish (will be serialized to JSON)
        """
        await self.redis.publish(channel, json.dumps(message))
    
    async def subscribe(self, channel: str) -> None:
        """
        Subscribe to a channel.
        
        Args:
            channel: Channel to subscribe to
        """
        if not self.connected:
            await self.connect()
        await self.pubsub.subscribe(channel)
    
    async def listen(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Listen for messages on subscribed channels.
        
        Yields:
            Deserialized message data
        """
        if not self.connected:
            await self.connect()
            
        while True:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                try:
                    data = json.loads(message['data'])
                    yield data
                except (json.JSONDecodeError, TypeError):
                    # Handle non-JSON messages
                    yield {'raw_data': message['data']}
            
            # Small sleep to avoid CPU spinning
            await asyncio.sleep(0.01)

class ErrorEventType(str, Enum):
    """Error event types."""
    GENERAL_ERROR = "general_error"
    STRATEGY_ERROR = "strategy_error"
    ORDER_ERROR = "order_error"
    TRADE_ERROR = "trade_error"
    RISK_ERROR = "risk_error"
    EXCHANGE_ERROR = "exchange_error"
    DATABASE_ERROR = "database_error"
    NETWORK_ERROR = "network_error"

async def publish_error(
    error_type: ErrorEventType,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    source: Optional[str] = None
) -> None:
    """
    Publish an error event to the event bus.
    
    Args:
        error_type: Type of error
        message: Error message
        details: Additional error details
        source: Source of the error
    """
    await publish(
        channel="error",
        message={
            "error_type": error_type,
            "message": message,
            "details": details or {},
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
    )