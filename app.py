from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from models.base import Base
from models.strategy import Strategy
from models.order import Order
from models.trade import Trade
from utils.config import get_settings
from config.database import get_db
from utils.health import router as health_router
from utils.metrics import router as metrics_router, init_metrics
from utils.error_handler import setup_exception_handlers
from utils.logger import setup_logger
from api.v1.router import api_router

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# Get application settings
settings = get_settings()

# Configure logging
logger = setup_logger("app")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Trading automation platform for cryptocurrency markets",
    version="0.1.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
setup_exception_handlers(app)

# Database setup
engine = create_engine(settings.postgres_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize metrics
init_metrics(app)

# Include routers
app.include_router(health_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(api_router, prefix="/api")

# Pydantic models for API
class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    market: str
    timeframe: str
    parameters: dict = Field(default_factory=dict)
    risk_settings: dict = Field(default_factory=dict)
    active: bool = True

class StrategyCreate(StrategyBase):
    pass

class StrategyResponse(StrategyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    performance_metrics: Optional[dict] = None

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    order_id: Optional[str] = None
    symbol: str
    side: str
    quantity: float
    price: float
    status: Optional[str] = "new"
    strategy_id: Optional[int] = None

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class TradeBase(BaseModel):
    trade_id: Optional[str] = None
    order_id: Optional[str] = None
    symbol: str
    side: str
    quantity: float
    price: float
    fee: Optional[float] = None
    order_db_id: Optional[int] = None

class TradeCreate(TradeBase):
    pass

class TradeResponse(TradeBase):
    id: int
    timestamp: datetime
    value: float

    class Config:
        from_attributes = True

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "environment": settings.environment
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    
    uvicorn.run(
        "app:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload and settings.is_development(),
        workers=settings.server.workers,
        log_level=settings.server.log_level
    )
