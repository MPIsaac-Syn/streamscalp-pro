"""
Pydantic models for strategy data validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class StrategyBase(BaseModel):
    """Base model for strategy data"""
    name: str
    description: str
    market: str
    timeframe: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_settings: Dict[str, Any] = Field(default_factory=dict)

    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        if v not in valid_timeframes:
            raise ValueError(f"Invalid timeframe. Must be one of {valid_timeframes}")
        return v

    @validator('market')
    def validate_market(cls, v):
        # Add actual market validation logic
        if not v.isupper() or len(v) < 5:
            raise ValueError("Invalid market format. Use uppercase symbol (e.g., BTCUSDT)")
        return v

class StrategyCreate(StrategyBase):
    """Model for creating a new strategy"""
    pass

class StrategyUpdate(BaseModel):
    """Model for updating an existing strategy"""
    name: Optional[str] = None
    description: Optional[str] = None
    market: Optional[str] = None
    timeframe: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    risk_settings: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        if v is None:
            return v
        valid_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        if v not in valid_timeframes:
            raise ValueError(f"Invalid timeframe. Must be one of {valid_timeframes}")
        return v

    @validator('market')
    def validate_market(cls, v):
        if v is None:
            return v
        # Add actual market validation logic
        if not v.isupper() or len(v) < 5:
            raise ValueError("Invalid market format. Use uppercase symbol (e.g., BTCUSDT)")
        return v

class StrategyResponse(StrategyBase):
    """Model for strategy response"""
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
    performance_metrics: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
