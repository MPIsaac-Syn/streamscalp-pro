# dashboard/backend/routes/strategies.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from datetime import datetime
import logging

# Internal imports
from models.strategy import Strategy as DBStrategy
from config.database import get_db
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("strategy_routes")

# --- Pydantic Models ---
class StrategyBase(BaseModel):
    name: str
    description: str
    market: str
    timeframe: str
    parameters: dict  # Added strategy parameters
    risk_settings: dict  # Added risk configuration

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
    pass

class StrategyResponse(StrategyBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
    performance_metrics: dict  # Changed to dict for multiple metrics

    class Config:
        orm_mode = True

# --- Database Operations ---
def get_strategy(db: Session, strategy_id: int):
    return db.query(DBStrategy).filter(DBStrategy.id == strategy_id).first()

# --- API Endpoints ---
@router.get("/", response_model=List[StrategyResponse])
def get_strategies(
    skip: int = 0,
    limit: int = 100,
    active: bool = None,
    db: Session = Depends(get_db)
):
    """Get all strategies with optional filters"""
    query = db.query(DBStrategy)
    
    if active is not None:
        query = query.filter(DBStrategy.active == active)
        
    strategies = query.offset(skip).limit(limit).all()
    return strategies

@router.get("/{strategy_id}", response_model=StrategyResponse)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get a specific strategy by ID"""
    strategy = get_strategy(db, strategy_id=strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    return strategy

@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """Create a new trading strategy"""
    try:
        db_strategy = DBStrategy(
            **strategy.dict(),
            active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_strategy)
        db.commit()
        db.refresh(db_strategy)
        logger.info(f"Created new strategy: {db_strategy.name}")
        return db_strategy
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create strategy"
        )

@router.put("/{strategy_id}", response_model=StrategyResponse)
def update_strategy(
    strategy_id: int,
    updated_strategy: StrategyCreate,
    db: Session = Depends(get_db)
):
    """Update an existing strategy"""
    try:
        db_strategy = get_strategy(db, strategy_id=strategy_id)
        if not db_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
            
        for key, value in updated_strategy.dict().items():
            setattr(db_strategy, key, value)
            
        db_strategy.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_strategy)
        logger.info(f"Updated strategy ID {strategy_id}")
        return db_strategy
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update strategy"
        )

@router.patch("/{strategy_id}/toggle", response_model=StrategyResponse)
def toggle_strategy_status(strategy_id: int, db: Session = Depends(get_db)):
    """Toggle strategy active/inactive status"""
    db_strategy = get_strategy(db, strategy_id=strategy_id)
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db_strategy.active = not db_strategy.active
    db_strategy.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_strategy)
    logger.info(f"Toggled status for strategy ID {strategy_id} to {db_strategy.active}")
    return db_strategy