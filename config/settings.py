from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, Field
import os

class Settings(BaseSettings):
    binance_api_key: str = Field(alias="BINANCE_API_KEY", default="")
    binance_api_secret: str = Field(alias="BINANCE_SECRET", default="")
    alpaca_api_key: str = Field(alias="ALPACA_API_KEY", default="")
    alpaca_api_secret: str = Field(alias="ALPACA_SECRET", default="")
    
    # Use SQLite for local development
    postgres_url: str = "sqlite:///./trades.db"
    
    # Redis configuration
    redis_url: str = "redis://redis:6379"
    redis_host: str = Field(alias="REDIS_HOST", default="localhost")
    redis_port: int = Field(alias="REDIS_PORT", default=6379)
    redis_password: str = Field(alias="REDIS_PASSWORD", default="")  # Changed from None to empty string
    
    # Exchange settings
    binance_testnet: bool = Field(alias="BINANCE_TESTNET", default=True)
    
    # Risk management settings
    max_position_size: float = Field(alias="MAX_POSITION_SIZE", default=0.1)
    max_daily_loss: float = Field(alias="MAX_DAILY_LOSS", default=0.02)
    max_open_positions: int = Field(alias="MAX_OPEN_POSITIONS", default=3)
    max_exposure_per_asset: float = Field(alias="MAX_EXPOSURE_PER_ASSET", default=0.05)
    
    # Debug mode flag
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()

def get_settings() -> Settings:
    """Return the settings instance."""
    return settings