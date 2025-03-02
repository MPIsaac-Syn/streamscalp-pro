"""
Pydantic models for trade data validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class TradeBase(BaseModel):
    """Base model for trade data"""
    trade_id: Optional[str] = None
    order_id: Optional[str] = None
    symbol: str
    side: str
    quantity: float
    price: float
    fee: Optional[float] = None
    order_db_id: Optional[int] = None

    @validator('side')
    def validate_side(cls, v):
        valid_sides = ['buy', 'sell']
        if v.lower() not in valid_sides:
            raise ValueError(f"Invalid side. Must be one of {valid_sides}")
        return v.lower()

class TradeCreate(TradeBase):
    """Model for creating a new trade"""
    pass

class TradeResponse(TradeBase):
    """Model for trade response"""
    id: int
    timestamp: datetime
    value: float
    exchange: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
