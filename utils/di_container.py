"""
Dependency Injection Container for StreamScalp Pro.

This module provides a centralized container for managing dependencies
throughout the application, ensuring proper initialization and lifecycle
management of components.
"""
import logging
from typing import Dict, Any, Type, Optional, TypeVar, cast
import redis.asyncio
from redis.asyncio import ConnectionPool

from utils.logger import setup_logger
from utils.event_bus import EventBus
from adapters.binance_adapter import BinanceAdapter
from adapters.alpaca_adapter import AlpacaAdapter
from order_manager.order_manager import OrderManager
from risk_manager.risk_manager import RiskManager
from utils.error_handler import ErrorCode
from utils.error_handler import (
    safe_execute,
    safe_execute_async,
    with_error_handler,
    with_error_handler_async
)
from config.settings import settings

T = TypeVar('T')
logger = setup_logger("di_container")

class DIContainer:
    """
    Dependency Injection Container for managing application components.
    
    This container manages the lifecycle and dependencies of various
    application components, ensuring they are properly initialized
    and configured.
    """
    
    def __init__(self):
        """Initialize an empty container."""
        self._components: Dict[str, Any] = {}
        self._factories: Dict[str, Any] = {}
        logger.info("Dependency Injection Container initialized")
    
    def register(self, name: str, component: Any) -> None:
        """
        Register a component in the container.
        
        Args:
            name: Name to register the component under
            component: The component instance to register
        """
        self._components[name] = component
        logger.debug(f"Registered component: {name}")
    
    def register_factory(self, name: str, factory: Any, is_singleton: bool = True) -> None:
        """
        Register a factory function for lazy component creation.
        
        Args:
            name: Name to register the factory under
            factory: Factory function that creates the component
            is_singleton: Whether the component is a singleton (default: True)
        """
        self._factories[name] = (factory, is_singleton)
        logger.debug(f"Registered factory: {name}")
    
    def register_instance(self, name: str, component: Any, is_singleton: bool = True) -> None:
        """
        Register a component instance in the container.
        
        Args:
            name: Name to register the component under
            component: The component instance to register
            is_singleton: Whether the component is a singleton (default: True)
        """
        self._components[name] = component
        logger.debug(f"Registered instance: {name}")
    
    def get(self, name: str, component_type: Optional[Type[T]] = None) -> Any:
        """
        Get a component from the container.
        
        Args:
            name: Name of the component to retrieve
            component_type: Optional type for type checking
            
        Returns:
            The requested component
            
        Raises:
            KeyError: If the component is not registered
        """
        if name in self._components:
            component = self._components[name]
            if component_type:
                return cast(T, component)  # Type cast for type checking
            return component
        
        if name in self._factories:
            # Lazy initialization using factory
            factory, is_singleton = self._factories[name]
            if is_singleton:
                if name not in self._components:
                    self._components[name] = factory()
                return self._components[name]
            else:
                return factory()
        
        raise KeyError(f"Component not found: {name}")
    
    def has(self, name: str) -> bool:
        """
        Check if a component is registered.
        
        Args:
            name: Name of the component to check
            
        Returns:
            True if the component is registered, False otherwise
        """
        return name in self._components or name in self._factories
    
    async def create_redis_pool(self, config: Dict[str, Any]) -> ConnectionPool:
        """
        Create a Redis connection pool.
        
        Args:
            config: Redis configuration
            
        Returns:
            Redis connection pool
        """
        host = config.get("host", "localhost")
        port = config.get("port", 6379)
        db = config.get("db", 0)
        password = config.get("password", None)
        
        pool = redis.asyncio.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
        
        logger.info(f"Created Redis connection pool: {host}:{port}/{db}")
        return pool
    
    async def create_event_bus(self, config: Dict[str, Any]) -> EventBus:
        """
        Create and initialize an event bus.
        
        Args:
            config: Event bus configuration
            
        Returns:
            Initialized event bus
        """
        redis_config = config.get("redis", {})
        pool = await self.create_redis_pool(redis_config)
        
        event_bus = EventBus(pool)
        await event_bus.connect()
        
        logger.info("Created and connected event bus")
        self.register("event_bus", event_bus)
        return event_bus
    
    async def create_exchange_adapter(self, exchange: str, config: Dict[str, Any]) -> Any:
        """
        Create and initialize an exchange adapter.
        
        Args:
            exchange: Exchange name (binance, alpaca)
            config: Exchange configuration
            
        Returns:
            Initialized exchange adapter
            
        Raises:
            ValueError: If the exchange is not supported
        """
        if exchange.lower() == "binance":
            api_key = config.get("api_key", "")
            api_secret = config.get("api_secret", "")
            testnet = config.get("testnet", True)
            
            adapter = BinanceAdapter(api_key, api_secret, testnet)
            await adapter.connect()
            
            logger.info(f"Created and connected Binance adapter (testnet: {testnet})")
            self.register("exchange_adapter", adapter)
            return adapter
        
        elif exchange.lower() == "alpaca":
            api_key = config.get("api_key", "")
            api_secret = config.get("api_secret", "")
            paper = config.get("paper", True)
            
            adapter = AlpacaAdapter(api_key, api_secret, paper)
            await adapter.connect()
            
            logger.info(f"Created and connected Alpaca adapter (paper: {paper})")
            self.register("exchange_adapter", adapter)
            return adapter
        
        else:
            raise ValueError(f"Unsupported exchange: {exchange}")
    
    async def create_order_manager(self, config: Dict[str, Any]) -> OrderManager:
        """
        Create and initialize an order manager.
        
        Args:
            config: Order manager configuration
            
        Returns:
            Initialized order manager
        """
        # Get dependencies
        if not self.has("exchange_adapter"):
            raise ValueError("Exchange adapter must be created before order manager")
        
        if not self.has("event_bus"):
            raise ValueError("Event bus must be created before order manager")
        
        exchange_adapter = self.get("exchange_adapter")
        event_bus = self.get("event_bus")
        
        # Create risk manager if not already created
        if not self.has("risk_manager"):
            risk_config = config.get("risk", {})
            await self.create_risk_manager(risk_config)
        
        risk_manager = self.get("risk_manager")
        
        # Create order manager
        order_manager = OrderManager(
            exchange_adapter=exchange_adapter,
            event_bus=event_bus,
            risk_manager=risk_manager,
            config=config
        )
        
        await order_manager.start()
        
        logger.info("Created and started order manager")
        self.register("order_manager", order_manager)
        return order_manager
    
    async def create_risk_manager(self, config: Dict[str, Any]) -> RiskManager:
        """
        Create and initialize a risk manager.
        
        Args:
            config: Risk manager configuration
            
        Returns:
            Initialized risk manager
        """
        risk_manager = RiskManager(config)
        await risk_manager.start()
        
        logger.info("Created and started risk manager")
        self.register("risk_manager", risk_manager)
        return risk_manager
    
    async def shutdown(self) -> None:
        """Shutdown all components in the container."""
        logger.info("Shutting down all components")
        
        # Shutdown order manager
        if self.has("order_manager"):
            order_manager = self.get("order_manager")
            await order_manager.stop()
            logger.info("Order manager stopped")
        
        # Shutdown risk manager
        if self.has("risk_manager"):
            risk_manager = self.get("risk_manager")
            await risk_manager.stop()
            logger.info("Risk manager stopped")
        
        # Shutdown exchange adapter
        if self.has("exchange_adapter"):
            exchange_adapter = self.get("exchange_adapter")
            await exchange_adapter.disconnect()
            logger.info("Exchange adapter disconnected")
        
        # Shutdown event bus
        if self.has("event_bus"):
            event_bus = self.get("event_bus")
            await event_bus.disconnect()
            logger.info("Event bus disconnected")
        
        logger.info("All components shut down")

# Create a singleton container instance
container = DIContainer()

# Register error handler and logger components
container.register_factory(
    "logger_factory", 
    lambda name, **kwargs: setup_logger(name, **kwargs),
    is_singleton=False
)

container.register_instance(
    "error_codes",
    ErrorCode,
    is_singleton=True
)

# Register error handler utilities
container.register_factory(
    "safe_execute",
    lambda: safe_execute,
    is_singleton=True
)

container.register_factory(
    "safe_execute_async",
    lambda: safe_execute_async,
    is_singleton=True
)

container.register_factory(
    "with_error_handler",
    lambda: with_error_handler,
    is_singleton=True
)

container.register_factory(
    "with_error_handler_async",
    lambda: with_error_handler_async,
    is_singleton=True
)

# Register configuration
container.register_factory(
    "config",
    lambda: settings,
    is_singleton=True
)
