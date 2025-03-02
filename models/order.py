from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_id = Column(String)
    symbol = Column(String)
    side = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    status = Column(String)
    timestamp = Column(DateTime)
    
    # Foreign keys
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    
    # Relationships
    strategy = relationship("Strategy", back_populates="orders")
    trade = relationship("Trade", uselist=False, back_populates="order")