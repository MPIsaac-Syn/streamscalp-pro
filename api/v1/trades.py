"""
API endpoints for trade management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models.trade import Trade as DBTrade
from config.database import get_db
from utils.logger import setup_logger
from schemas.trade import TradeCreate, TradeResponse

router = APIRouter()
logger = setup_logger("trade_routes")

# --- Database Operations ---
def get_trade(db: Session, trade_id: int):
    """Get a trade by database ID"""
    return db.query(DBTrade).filter(DBTrade.id == trade_id).first()

def get_trade_by_exchange_id(db: Session, trade_id: str):
    """Get a trade by exchange trade ID"""
    return db.query(DBTrade).filter(DBTrade.trade_id == trade_id).first()

# --- API Endpoints ---
@router.get("/", response_model=List[TradeResponse])
async def get_trades(
    skip: int = 0,
    limit: int = 100,
    symbol: Optional[str] = None,
    side: Optional[str] = None,
    order_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all trades with optional filters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        symbol: Filter by trading symbol
        side: Filter by trade side (buy/sell)
        order_id: Filter by order ID
        db: Database session
        
    Returns:
        List of trades
    """
    query = db.query(DBTrade)
    
    if symbol:
        query = query.filter(DBTrade.symbol == symbol)
    if side:
        query = query.filter(DBTrade.side == side)
    if order_id:
        query = query.filter(DBTrade.order_id == order_id)
        
    trades = query.offset(skip).limit(limit).all()
    return trades

@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade_by_id(trade_id: int, db: Session = Depends(get_db)):
    """
    Get a specific trade by ID.
    
    Args:
        trade_id: Trade ID
        db: Database session
        
    Returns:
        Trade details
        
    Raises:
        HTTPException: If trade not found
    """
    trade = get_trade(db, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    return trade

@router.post("/", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    """
    Create a new trade record manually.
    
    Args:
        trade: Trade data
        db: Database session
        
    Returns:
        Created trade
        
    Raises:
        HTTPException: If trade creation fails
    """
    try:
        # Calculate trade value
        value = trade.quantity * trade.price
        
        # Create trade record
        db_trade = DBTrade(
            **trade.dict(),
            value=value,
            timestamp=datetime.utcnow()
        )
        
        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)
        
        logger.info(f"Created new trade: {db_trade.trade_id}")
        return db_trade
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating trade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trade: {str(e)}"
        )

@router.get("/by-order/{order_id}", response_model=List[TradeResponse])
async def get_trades_by_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all trades associated with a specific order.
    
    Args:
        order_id: Order ID
        db: Database session
        
    Returns:
        List of trades
    """
    trades = db.query(DBTrade).filter(DBTrade.order_id == order_id).all()
    return trades

@router.get("/by-symbol/{symbol}", response_model=List[TradeResponse])
async def get_trades_by_symbol(
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get all trades for a specific symbol with optional date range.
    
    Args:
        symbol: Trading symbol
        start_date: Optional start date filter
        end_date: Optional end date filter
        db: Database session
        
    Returns:
        List of trades
    """
    query = db.query(DBTrade).filter(DBTrade.symbol == symbol)
    
    if start_date:
        query = query.filter(DBTrade.timestamp >= start_date)
    if end_date:
        query = query.filter(DBTrade.timestamp <= end_date)
        
    trades = query.order_by(DBTrade.timestamp.desc()).all()
    return trades
