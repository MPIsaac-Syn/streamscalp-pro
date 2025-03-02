# dashboard/backend/routes/trades.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

# Import internal modules
from models.trade import Trade as DBTrade  # Renamed to avoid conflict
from utils.logger import TradeLogger
from config.database import get_db

router = APIRouter()
logger = TradeLogger()

# Pydantic models
class TradeBase(BaseModel):
    symbol: str
    entry_price: float
    position_size: float
    side: str  # Add 'side' field (buy/sell)

class TradeCreate(TradeBase):
    pass

class TradeResponse(TradeBase):
    id: int
    entry_time: datetime
    exit_time: datetime | None = None
    exit_price: float | None = None
    pnl: float | None = None
    status: str

    class Config:
        orm_mode = True

# Database operations
def get_trade(db: Session, trade_id: int):
    return db.query(DBTrade).filter(DBTrade.id == trade_id).first()

# API endpoints
@router.get("/", response_model=List[TradeResponse])
async def read_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all trades from database"""
    trades = db.query(DBTrade).offset(skip).limit(limit).all()
    return trades

@router.get("/{trade_id}", response_model=TradeResponse)
async def read_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get a specific trade by ID"""
    db_trade = get_trade(db, trade_id=trade_id)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return db_trade

@router.post("/", response_model=TradeResponse)
async def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    """Create a new trade in database"""
    try:
        db_trade = DBTrade(
            symbol=trade.symbol,
            entry_price=trade.entry_price,
            position_size=trade.position_size,
            side=trade.side,
            status='open',
            entry_time=datetime.utcnow()
        )
        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)
        logger.log_trade({
            'symbol': trade.symbol,
            'side': trade.side,
            'quantity': trade.position_size,
            'price': trade.entry_price
        })
        return db_trade
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))