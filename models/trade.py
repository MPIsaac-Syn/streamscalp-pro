from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
from .base import Base

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(String, nullable=True)
    order_id = Column(String, nullable=True)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # 'buy' or 'sell'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    order_db_id = Column(Integer, ForeignKey("orders.id"))
    
    # Relationships
    order = relationship("Order", back_populates="trade")
    
    @property
    def value(self) -> float:
        """Calculate the total value of the trade"""
        return self.quantity * self.price
    
    @property
    def profit(self) -> float:
        """Calculate the profit/loss of the trade (placeholder)"""
        # This is a placeholder - in a real implementation, this would calculate
        # profit based on entry and exit prices, accounting for fees
        return 0.0
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'trade_id': self.trade_id,
            'order_id': self.order_id,
            'fee': self.fee,
            'value': self.value
        }