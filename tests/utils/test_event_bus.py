"""
Tests for the event bus utilities.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from utils.event_bus import (
    EventType,
    ErrorEventType,
    OrderEventType,
    TradeEventType,
    StrategyEventType,
    ExchangeEventType,
    SystemEventType,
    Event,
    ErrorEvent,
    OrderEvent,
    TradeEvent,
    StrategyEvent,
    ExchangeEvent,
    SystemEvent,
    publish_event,
    publish_error,
    subscribe,
    unsubscribe,
    get_redis_client
)


class TestEventTypes:
    """Tests for event type enums."""
    
    def test_event_type_values(self):
        """Test EventType enum values."""
        assert EventType.ERROR == "error"
        assert EventType.ORDER == "order"
        assert EventType.TRADE == "trade"
        assert EventType.STRATEGY == "strategy"
        assert EventType.EXCHANGE == "exchange"
        assert EventType.SYSTEM == "system"
    
    def test_error_event_type_values(self):
        """Test ErrorEventType enum values."""
        assert ErrorEventType.GENERAL_ERROR == "general_error"
        assert ErrorEventType.VALIDATION_ERROR == "validation_error"
        assert ErrorEventType.EXCHANGE_ERROR == "exchange_error"
        assert ErrorEventType.DATABASE_ERROR == "database_error"
        assert ErrorEventType.NETWORK_ERROR == "network_error"
        assert ErrorEventType.AUTHENTICATION_ERROR == "authentication_error"
        assert ErrorEventType.AUTHORIZATION_ERROR == "authorization_error"
        assert ErrorEventType.STRATEGY_ERROR == "strategy_error"
        assert ErrorEventType.ORDER_ERROR == "order_error"
        assert ErrorEventType.TRADE_ERROR == "trade_error"
    
    def test_order_event_type_values(self):
        """Test OrderEventType enum values."""
        assert OrderEventType.ORDER_CREATED == "order_created"
        assert OrderEventType.ORDER_UPDATED == "order_updated"
        assert OrderEventType.ORDER_CANCELLED == "order_cancelled"
        assert OrderEventType.ORDER_FILLED == "order_filled"
        assert OrderEventType.ORDER_REJECTED == "order_rejected"
    
    def test_trade_event_type_values(self):
        """Test TradeEventType enum values."""
        assert TradeEventType.TRADE_EXECUTED == "trade_executed"
        assert TradeEventType.TRADE_UPDATED == "trade_updated"
        assert TradeEventType.TRADE_CLOSED == "trade_closed"
    
    def test_strategy_event_type_values(self):
        """Test StrategyEventType enum values."""
        assert StrategyEventType.STRATEGY_STARTED == "strategy_started"
        assert StrategyEventType.STRATEGY_STOPPED == "strategy_stopped"
        assert StrategyEventType.STRATEGY_UPDATED == "strategy_updated"
        assert StrategyEventType.STRATEGY_SIGNAL == "strategy_signal"
    
    def test_exchange_event_type_values(self):
        """Test ExchangeEventType enum values."""
        assert ExchangeEventType.EXCHANGE_CONNECTED == "exchange_connected"
        assert ExchangeEventType.EXCHANGE_DISCONNECTED == "exchange_disconnected"
        assert ExchangeEventType.EXCHANGE_ERROR == "exchange_error"
        assert ExchangeEventType.MARKET_DATA_UPDATED == "market_data_updated"
    
    def test_system_event_type_values(self):
        """Test SystemEventType enum values."""
        assert SystemEventType.SYSTEM_STARTED == "system_started"
        assert SystemEventType.SYSTEM_STOPPED == "system_stopped"
        assert SystemEventType.SYSTEM_ERROR == "system_error"
        assert SystemEventType.SYSTEM_WARNING == "system_warning"
        assert SystemEventType.SYSTEM_INFO == "system_info"


class TestEventClasses:
    """Tests for event classes."""
    
    def test_event_base_class(self):
        """Test Event base class."""
        # Create event
        event = Event(
            event_type=EventType.SYSTEM,
            sub_type="test_sub_type",
            data={"test": "value"},
            source="test_source"
        )
        
        # Check attributes
        assert event.event_type == EventType.SYSTEM
        assert event.sub_type == "test_sub_type"
        assert event.data == {"test": "value"}
        assert event.source == "test_source"
        assert event.timestamp is not None
    
    def test_error_event(self):
        """Test ErrorEvent class."""
        # Create event
        event = ErrorEvent(
            error_type=ErrorEventType.GENERAL_ERROR,
            message="Test error",
            details={"test": "value"},
            source="test_source"
        )
        
        # Check attributes
        assert event.event_type == EventType.ERROR
        assert event.sub_type == ErrorEventType.GENERAL_ERROR
        assert event.data == {
            "message": "Test error",
            "details": {"test": "value"}
        }
        assert event.source == "test_source"
        assert event.timestamp is not None
    
    def test_order_event(self):
        """Test OrderEvent class."""
        # Create event
        event = OrderEvent(
            order_event_type=OrderEventType.ORDER_CREATED,
            order_id="test_order_id",
            order_data={"symbol": "BTC/USDT", "side": "buy"},
            source="test_source"
        )
        
        # Check attributes
        assert event.event_type == EventType.ORDER
        assert event.sub_type == OrderEventType.ORDER_CREATED
        assert event.data == {
            "order_id": "test_order_id",
            "order_data": {"symbol": "BTC/USDT", "side": "buy"}
        }
        assert event.source == "test_source"
        assert event.timestamp is not None
    
    def test_trade_event(self):
        """Test TradeEvent class."""
        # Create event
        event = TradeEvent(
            trade_event_type=TradeEventType.TRADE_EXECUTED,
            trade_id="test_trade_id",
            trade_data={"symbol": "BTC/USDT", "price": 50000},
            source="test_source"
        )
        
        # Check attributes
        assert event.event_type == EventType.TRADE
        assert event.sub_type == TradeEventType.TRADE_EXECUTED
        assert event.data == {
            "trade_id": "test_trade_id",
            "trade_data": {"symbol": "BTC/USDT", "price": 50000}
        }
        assert event.source == "test_source"
        assert event.timestamp is not None
    
    def test_strategy_event(self):
        """Test StrategyEvent class."""
        # Create event
        event = StrategyEvent(
            strategy_event_type=StrategyEventType.STRATEGY_SIGNAL,
            strategy_id="test_strategy_id",
            strategy_data={"signal": "buy", "symbol": "BTC/USDT"},
            source="test_source"
        )
        
        # Check attributes
        assert event.event_type == EventType.STRATEGY
        assert event.sub_type == StrategyEventType.STRATEGY_SIGNAL
        assert event.data == {
            "strategy_id": "test_strategy_id",
            "strategy_data": {"signal": "buy", "symbol": "BTC/USDT"}
        }
        assert event.source == "test_source"
        assert event.timestamp is not None
    
    def test_exchange_event(self):
        """Test ExchangeEvent class."""
        # Create event
        event = ExchangeEvent(
            exchange_event_type=ExchangeEventType.MARKET_DATA_UPDATED,
            exchange_id="binance",
            exchange_data={"symbol": "BTC/USDT", "price": 50000},
            source="test_source"
        )
        
        # Check attributes
        assert event.event_type == EventType.EXCHANGE
        assert event.sub_type == ExchangeEventType.MARKET_DATA_UPDATED
        assert event.data == {
            "exchange_id": "binance",
            "exchange_data": {"symbol": "BTC/USDT", "price": 50000}
        }
        assert event.source == "test_source"
        assert event.timestamp is not None
    
    def test_system_event(self):
        """Test SystemEvent class."""
        # Create event
        event = SystemEvent(
            system_event_type=SystemEventType.SYSTEM_INFO,
            message="System started",
            details={"version": "1.0.0"},
            source="test_source"
        )
        
        # Check attributes
        assert event.event_type == EventType.SYSTEM
        assert event.sub_type == SystemEventType.SYSTEM_INFO
        assert event.data == {
            "message": "System started",
            "details": {"version": "1.0.0"}
        }
        assert event.source == "test_source"
        assert event.timestamp is not None


class TestEventBusFunctions:
    """Tests for event bus functions."""
    
    @pytest.mark.asyncio
    async def test_publish_event(self):
        """Test publish_event function."""
        # Create a mock redis client
        mock_redis = AsyncMock()
        
        # Mock get_redis_client to return the mock redis client
        with patch("utils.event_bus.get_redis_client", return_value=mock_redis):
            # Create event
            event = Event(
                event_type=EventType.SYSTEM,
                sub_type="test_sub_type",
                data={"test": "value"},
                source="test_source"
            )
            
            # Publish event
            await publish_event(event)
            
            # Check that publish was called
            mock_redis.publish.assert_called_once()
            
            # Check channel and message
            args, kwargs = mock_redis.publish.call_args
            assert args[0] == "streamscalp:events:system:test_sub_type"
            assert "test" in args[1]  # JSON string contains "test"
    
    @pytest.mark.asyncio
    async def test_publish_error(self):
        """Test publish_error function."""
        # Create a mock redis client
        mock_redis = AsyncMock()
        
        # Mock get_redis_client to return the mock redis client
        with patch("utils.event_bus.get_redis_client", return_value=mock_redis):
            # Publish error
            await publish_error(
                error_type=ErrorEventType.GENERAL_ERROR,
                message="Test error",
                details={"test": "value"},
                source="test_source"
            )
            
            # Check that publish was called
            mock_redis.publish.assert_called_once()
            
            # Check channel and message
            args, kwargs = mock_redis.publish.call_args
            assert args[0] == "streamscalp:events:error:general_error"
            assert "Test error" in args[1]  # JSON string contains error message
    
    @pytest.mark.asyncio
    async def test_subscribe(self):
        """Test subscribe function."""
        # Create a mock redis client
        mock_redis = AsyncMock()
        
        # Create a mock pubsub
        mock_pubsub = AsyncMock()
        mock_redis.pubsub.return_value = mock_pubsub
        
        # Mock get_redis_client to return the mock redis client
        with patch("utils.event_bus.get_redis_client", return_value=mock_redis):
            # Create a mock callback
            callback = AsyncMock()
            
            # Subscribe
            await subscribe(
                event_type=EventType.SYSTEM,
                sub_type="test_sub_type",
                callback=callback
            )
            
            # Check that subscribe was called
            mock_pubsub.subscribe.assert_called_once_with(
                "streamscalp:events:system:test_sub_type"
            )
            
            # Check that pubsub.run was called
            mock_pubsub.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test unsubscribe function."""
        # Create a mock redis client
        mock_redis = AsyncMock()
        
        # Create a mock pubsub
        mock_pubsub = AsyncMock()
        mock_redis.pubsub.return_value = mock_pubsub
        
        # Mock get_redis_client to return the mock redis client
        with patch("utils.event_bus.get_redis_client", return_value=mock_redis):
            # Unsubscribe
            await unsubscribe(
                event_type=EventType.SYSTEM,
                sub_type="test_sub_type"
            )
            
            # Check that unsubscribe was called
            mock_pubsub.unsubscribe.assert_called_once_with(
                "streamscalp:events:system:test_sub_type"
            )
    
    def test_get_redis_client(self):
        """Test get_redis_client function."""
        # Mock redis.Redis
        mock_redis_class = MagicMock()
        
        # Mock get_settings
        mock_settings = MagicMock()
        mock_settings.get_redis_url.return_value = "redis://localhost:6379/0"
        
        with patch("utils.event_bus.redis.Redis", return_value=mock_redis_class), \
             patch("utils.event_bus.get_settings", return_value=mock_settings):
            
            # Get redis client
            client = get_redis_client()
            
            # Check that Redis was called with the correct URL
            mock_settings.get_redis_url.assert_called_once()
