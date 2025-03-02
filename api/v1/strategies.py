"""
API endpoints for strategy management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models.strategy import Strategy as DBStrategy
from config.database import get_db
from utils.logger import setup_logger
from schemas.strategy import StrategyCreate, StrategyResponse, StrategyUpdate

router = APIRouter()
logger = setup_logger("strategy_routes")

# --- Database Operations ---
def get_strategy(db: Session, strategy_id: int):
    """Get a strategy by ID"""
    return db.query(DBStrategy).filter(DBStrategy.id == strategy_id).first()

# --- API Endpoints ---
@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    skip: int = 0,
    limit: int = 100,
    active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all strategies with optional filters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active: Filter by active status
        db: Database session
        
    Returns:
        List of strategies
    """
    query = db.query(DBStrategy)
    
    if active is not None:
        query = query.filter(DBStrategy.active == active)
        
    strategies = query.offset(skip).limit(limit).all()
    return strategies

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy_by_id(strategy_id: int, db: Session = Depends(get_db)):
    """
    Get a specific strategy by ID.
    
    Args:
        strategy_id: Strategy ID
        db: Database session
        
    Returns:
        Strategy details
        
    Raises:
        HTTPException: If strategy not found
    """
    strategy = get_strategy(db, strategy_id=strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    return strategy

@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """
    Create a new trading strategy.
    
    Args:
        strategy: Strategy data
        db: Database session
        
    Returns:
        Created strategy
        
    Raises:
        HTTPException: If strategy creation fails
    """
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
async def update_strategy(
    strategy_id: int,
    updated_strategy: StrategyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing strategy.
    
    Args:
        strategy_id: Strategy ID
        updated_strategy: Updated strategy data
        db: Database session
        
    Returns:
        Updated strategy
        
    Raises:
        HTTPException: If strategy not found or update fails
    """
    try:
        db_strategy = get_strategy(db, strategy_id=strategy_id)
        if not db_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
            
        # Update fields
        update_data = updated_strategy.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_strategy, key, value)
            
        db_strategy.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_strategy)
        logger.info(f"Updated strategy ID {strategy_id}")
        return db_strategy
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update strategy"
        )

@router.patch("/{strategy_id}/toggle", response_model=StrategyResponse)
async def toggle_strategy_status(strategy_id: int, db: Session = Depends(get_db)):
    """
    Toggle strategy active/inactive status.
    
    Args:
        strategy_id: Strategy ID
        db: Database session
        
    Returns:
        Updated strategy
        
    Raises:
        HTTPException: If strategy not found
    """
    db_strategy = get_strategy(db, strategy_id=strategy_id)
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db_strategy.active = not db_strategy.active
    db_strategy.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_strategy)
    logger.info(f"Toggled status for strategy ID {strategy_id} to {db_strategy.active}")
    return db_strategy

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """
    Delete a strategy.
    
    Args:
        strategy_id: Strategy ID
        db: Database session
        
    Raises:
        HTTPException: If strategy not found
    """
    db_strategy = get_strategy(db, strategy_id=strategy_id)
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db.delete(db_strategy)
    db.commit()
    logger.info(f"Deleted strategy ID {strategy_id}")
    return None
