"""
Pydantic models for order data validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class OrderBase(BaseModel):
    """Base model for order data"""
    order_id: Optional[str] = None
    symbol: str
    side: str
    quantity: float
    price: float
    status: Optional[str] = "new"
    strategy_id: Optional[int] = None

    @validator('side')
    def validate_side(cls, v):
        valid_sides = ['buy', 'sell']
        if v.lower() not in valid_sides:
            raise ValueError(f"Invalid side. Must be one of {valid_sides}")
        return v.lower()

class OrderCreate(OrderBase):
    """Model for creating a new order"""
    pass

class OrderUpdate(BaseModel):
    """Model for updating an existing order"""
    symbol: Optional[str] = None
    side: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    status: Optional[str] = None
    
    @validator('side')
    def validate_side(cls, v):
        if v is None:
            return v
        valid_sides = ['buy', 'sell']
        if v.lower() not in valid_sides:
            raise ValueError(f"Invalid side. Must be one of {valid_sides}")
        return v.lower()

class OrderResponse(OrderBase):
    """Model for order response"""
    id: int
    timestamp: datetime
    value: Optional[float] = None
    exchange_order_id: Optional[str] = None
    exchange: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
