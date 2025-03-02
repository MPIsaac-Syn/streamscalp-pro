"""
Tests for the configuration utilities.
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock

from utils.config import (
    Environment,
    LogLevel,
    DatabaseSettings,
    RedisSettings,
    ExchangeCredentials,
    ExchangeSettings,
    RiskSettings,
    ServerSettings,
    Settings,
    get_settings
)


class TestEnvironment:
    """Tests for Environment enum."""
    
    def test_environment_values(self):
        """Test Environment enum values."""
        assert Environment.DEVELOPMENT == "development"
        assert Environment.STAGING == "staging"
        assert Environment.PRODUCTION == "production"


class TestLogLevel:
    """Tests for LogLevel enum."""
    
    def test_log_level_values(self):
        """Test LogLevel enum values."""
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.CRITICAL == "CRITICAL"


class TestDatabaseSettings:
    """Tests for DatabaseSettings."""
    
    def test_database_settings_defaults(self):
        """Test DatabaseSettings defaults."""
        # Create settings with required values
        settings = DatabaseSettings(DATABASE_URL="sqlite:///./test.db")
        
        # Check defaults
        assert settings.url == "sqlite:///./test.db"
        assert settings.pool_size == 20
        assert settings.max_overflow == 10
        assert settings.pool_timeout == 30
        assert settings.pool_recycle == 1800
        assert settings.echo is False
    
    def test_database_settings_custom(self):
        """Test DatabaseSettings with custom values."""
        # Create settings with custom values
        settings = DatabaseSettings(
            DATABASE_URL="postgresql://user:pass@localhost/test",
            DATABASE_POOL_SIZE=30,
            DATABASE_MAX_OVERFLOW=20,
            DATABASE_POOL_TIMEOUT=60,
            DATABASE_POOL_RECYCLE=3600,
            DATABASE_ECHO=True
        )
        
        # Check values
        assert settings.url == "postgresql://user:pass@localhost/test"
        assert settings.pool_size == 30
        assert settings.max_overflow == 20
        assert settings.pool_timeout == 60
        assert settings.pool_recycle == 3600
        assert settings.echo is True


class TestRedisSettings:
    """Tests for RedisSettings."""
    
    def test_redis_settings_defaults(self):
        """Test RedisSettings defaults."""
        # Create settings with required values
        settings = RedisSettings(REDIS_URL="redis://localhost:6379/0")
        
        # Check defaults
        assert settings.url == "redis://localhost:6379/0"
        assert settings.pool_size == 10
        assert settings.socket_timeout == 5
        assert settings.socket_connect_timeout == 5
        assert settings.retry_on_timeout is True
    
    def test_redis_settings_custom(self):
        """Test RedisSettings with custom values."""
        # Create settings with custom values
        settings = RedisSettings(
            REDIS_URL="redis://localhost:6379/1",
            REDIS_POOL_SIZE=20,
            REDIS_SOCKET_TIMEOUT=10,
            REDIS_SOCKET_CONNECT_TIMEOUT=10,
            REDIS_RETRY_ON_TIMEOUT=False
        )
        
        # Check values
        assert settings.url == "redis://localhost:6379/1"
        assert settings.pool_size == 20
        assert settings.socket_timeout == 10
        assert settings.socket_connect_timeout == 10
        assert settings.retry_on_timeout is False


class TestExchangeCredentials:
    """Tests for ExchangeCredentials."""
    
    def test_exchange_credentials_defaults(self):
        """Test ExchangeCredentials defaults."""
        # Create credentials with required values
        credentials = ExchangeCredentials(
            api_key="test_key",
            api_secret="test_secret"
        )
        
        # Check values
        assert credentials.api_key == "test_key"
        assert credentials.api_secret == "test_secret"
        assert credentials.passphrase is None
        assert credentials.testnet is False
    
    def test_exchange_credentials_custom(self):
        """Test ExchangeCredentials with custom values."""
        # Create credentials with custom values
        credentials = ExchangeCredentials(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_passphrase",
            testnet=True
        )
        
        # Check values
        assert credentials.api_key == "test_key"
        assert credentials.api_secret == "test_secret"
        assert credentials.passphrase == "test_passphrase"
        assert credentials.testnet is True


class TestExchangeSettings:
    """Tests for ExchangeSettings."""
    
    def test_exchange_settings_defaults(self):
        """Test ExchangeSettings defaults."""
        # Create settings
        settings = ExchangeSettings()
        
        # Check defaults
        assert settings.binance is None
        assert settings.binance_futures is None
        assert settings.alpaca is None
    
    def test_exchange_settings_custom(self):
        """Test ExchangeSettings with custom values."""
        # Create settings with custom values
        settings = ExchangeSettings(
            binance=ExchangeCredentials(
                api_key="binance_key",
                api_secret="binance_secret"
            ),
            binance_futures=ExchangeCredentials(
                api_key="binance_futures_key",
                api_secret="binance_futures_secret",
                testnet=True
            ),
            alpaca=ExchangeCredentials(
                api_key="alpaca_key",
                api_secret="alpaca_secret",
                testnet=True
            )
        )
        
        # Check values
        assert settings.binance.api_key == "binance_key"
        assert settings.binance.api_secret == "binance_secret"
        assert settings.binance.testnet is False
        
        assert settings.binance_futures.api_key == "binance_futures_key"
        assert settings.binance_futures.api_secret == "binance_futures_secret"
        assert settings.binance_futures.testnet is True
        
        assert settings.alpaca.api_key == "alpaca_key"
        assert settings.alpaca.api_secret == "alpaca_secret"
        assert settings.alpaca.testnet is True
    
    def test_exchange_settings_env_vars(self):
        """Test ExchangeSettings with environment variables."""
        # Set environment variables for testing
        with patch.dict(os.environ, {
            "BINANCE_API_KEY": "env_binance_key",
            "BINANCE_API_SECRET": "env_binance_secret",
            "BINANCE_TESTNET": "true",
            "BINANCE_FUTURES_API_KEY": "env_binance_futures_key",
            "BINANCE_FUTURES_API_SECRET": "env_binance_futures_secret",
            "BINANCE_FUTURES_TESTNET": "false",
            "ALPACA_API_KEY": "env_alpaca_key",
            "ALPACA_API_SECRET": "env_alpaca_secret",
            "ALPACA_PAPER": "true"
        }):
            # Create settings
            settings = ExchangeSettings()
            
            # Check values
            assert settings.binance is not None
            assert settings.binance.api_key == "env_binance_key"
            assert settings.binance.api_secret == "env_binance_secret"
            assert settings.binance.testnet is True
            
            assert settings.binance_futures is not None
            assert settings.binance_futures.api_key == "env_binance_futures_key"
            assert settings.binance_futures.api_secret == "env_binance_futures_secret"
            assert settings.binance_futures.testnet is False
            
            assert settings.alpaca is not None
            assert settings.alpaca.api_key == "env_alpaca_key"
            assert settings.alpaca.api_secret == "env_alpaca_secret"
            assert settings.alpaca.testnet is True


class TestRiskSettings:
    """Tests for RiskSettings."""
    
    def test_risk_settings_defaults(self):
        """Test RiskSettings defaults."""
        # Create settings
        settings = RiskSettings()
        
        # Check defaults
        assert settings.max_position_size == 0.1
        assert settings.max_daily_loss == 0.02
        assert settings.max_open_positions == 5
        assert settings.max_open_orders == 10
        assert settings.max_leverage == 3.0
        assert settings.default_stop_loss_percent == 0.02
        assert settings.default_take_profit_percent == 0.04
    
    def test_risk_settings_custom(self):
        """Test RiskSettings with custom values."""
        # Create settings with custom values
        settings = RiskSettings(
            RISK_MAX_POSITION_SIZE=0.2,
            RISK_MAX_DAILY_LOSS=0.03,
            RISK_MAX_OPEN_POSITIONS=10,
            RISK_MAX_OPEN_ORDERS=20,
            RISK_MAX_LEVERAGE=5.0,
            RISK_DEFAULT_STOP_LOSS_PERCENT=0.03,
            RISK_DEFAULT_TAKE_PROFIT_PERCENT=0.06
        )
        
        # Check values
        assert settings.max_position_size == 0.2
        assert settings.max_daily_loss == 0.03
        assert settings.max_open_positions == 10
        assert settings.max_open_orders == 20
        assert settings.max_leverage == 5.0
        assert settings.default_stop_loss_percent == 0.03
        assert settings.default_take_profit_percent == 0.06


class TestServerSettings:
    """Tests for ServerSettings."""
    
    def test_server_settings_defaults(self):
        """Test ServerSettings defaults."""
        # Create settings
        settings = ServerSettings()
        
        # Check defaults
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.workers == 4
        assert settings.reload is False
        assert settings.log_level == "info"
        assert settings.timeout == 60
    
    def test_server_settings_custom(self):
        """Test ServerSettings with custom values."""
        # Create settings with custom values
        settings = ServerSettings(
            SERVER_HOST="127.0.0.1",
            SERVER_PORT=9000,
            SERVER_WORKERS=8,
            SERVER_RELOAD=True,
            SERVER_LOG_LEVEL="debug",
            SERVER_TIMEOUT=120
        )
        
        # Check values
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.workers == 8
        assert settings.reload is True
        assert settings.log_level == "debug"
        assert settings.timeout == 120


class TestSettings:
    """Tests for Settings."""
    
    def test_settings_defaults(self):
        """Test Settings defaults."""
        # Set required environment variables
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///./test.db",
            "REDIS_URL": "redis://localhost:6379/0",
            "LOG_LEVEL": "INFO"  # Explicitly set LOG_LEVEL to INFO for this test
        }):
            # Create settings
            settings = Settings()
            
            # Check defaults
            assert settings.app_name == "StreamScalp Pro"
            assert settings.environment == Environment.DEVELOPMENT
            assert settings.debug is False
            assert settings.log_level == LogLevel.INFO
            assert settings.cors_origins == ["*"]
            
            # Check database settings
            assert settings.database.url == "sqlite:///./test.db"
            
            # Check redis settings
            assert settings.redis.url == "redis://localhost:6379/0"
    
    def test_settings_custom(self):
        """Test Settings with custom values."""
        # Set environment variables for testing
        with patch.dict(os.environ, {
            "APP_NAME": "Custom App",
            "ENVIRONMENT": "production",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "CORS_ORIGINS": '["http://localhost:3000", "https://example.com"]',
            "DATABASE_URL": "postgresql://user:pass@localhost/test",
            "REDIS_URL": "redis://localhost:6379/1"
        }):
            # Create settings
            settings = Settings()
            
            # Check values
            assert settings.app_name == "Custom App"
            assert settings.environment == Environment.PRODUCTION
            assert settings.debug is True
            assert settings.log_level == LogLevel.DEBUG
            assert settings.cors_origins == ["http://localhost:3000", "https://example.com"]
            
            # Check database settings
            assert settings.database.url == "postgresql://user:pass@localhost/test"
            
            # Check redis settings
            assert settings.redis.url == "redis://localhost:6379/1"
    
    def test_settings_helper_methods(self):
        """Test Settings helper methods."""
        # Set required environment variables
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///./test.db",
            "REDIS_URL": "redis://localhost:6379/0",
            "ENVIRONMENT": "development"
        }):
            # Create settings
            settings = Settings()
            
            # Check helper methods
            assert settings.get_database_url() == "sqlite:///./test.db"
            assert settings.get_redis_url() == "redis://localhost:6379/0"
            assert settings.is_development() is True
            assert settings.is_production() is False
            
            # Change environment and check again
            with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
                settings = Settings()
                assert settings.is_development() is False
                assert settings.is_production() is True


class TestGetSettings:
    """Tests for get_settings."""
    
    def test_get_settings_cache(self):
        """Test get_settings caching."""
        # Set required environment variables
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///./test.db",
            "REDIS_URL": "redis://localhost:6379/0"
        }):
            # Get settings twice
            settings1 = get_settings()
            settings2 = get_settings()
            
            # Check that the same instance is returned
            assert settings1 is settings2
    
    def test_get_settings_error(self):
        """Test get_settings error handling."""
        # Clear the cache to ensure we don't get a cached result
        get_settings.cache_clear()
        
        # Mock the Settings class to raise an exception when instantiated
        with patch('utils.config.Settings', side_effect=ValueError("Required environment variables missing")):
            # Get settings should raise the exception
            with pytest.raises(Exception):
                get_settings()
