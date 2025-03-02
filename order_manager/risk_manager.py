from datetime import datetime, date
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.trade import Trade
from models.strategy import Strategy

class RiskManager:
    def __init__(self, session: Session, daily_loss_limit: float = -0.05, max_consecutive_losses: int = 3):
        self.session = session
        self.daily_loss_limit = daily_loss_limit
        self.max_consecutive_losses = max_consecutive_losses
        self.today_pnl = 0.0
        self.consecutive_losses = 0
        self.position_tracker = {}  # Tracks open positions by symbol
        self._initialize_daily_metrics()
    
    def _initialize_daily_metrics(self):
        """Initialize daily metrics from database"""
        today = date.today()
        today_trades = self.session.query(Trade).filter(
            datetime.date(Trade.timestamp) == today
        ).all()
        
        # Calculate today's PnL from trades
        self.today_pnl = sum(trade.profit for trade in today_trades)
        
        # Calculate consecutive losses
        recent_trades = self.session.query(Trade).order_by(
            Trade.timestamp.desc()
        ).limit(10).all()
        
        self.consecutive_losses = 0
        for trade in recent_trades:
            if trade.profit < 0:
                self.consecutive_losses += 1
            else:
                break
    
    async def get_portfolio_value(self) -> float:
        """Get current portfolio value - replace with actual implementation"""
        # This should query the exchange for actual account balance
        return 10000.0  # Placeholder value
    
    async def get_strategy(self, strategy_id: int) -> Strategy:
        """Get strategy by ID"""
        return self.session.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    async def calculate_position_size(self, strategy_id: int, symbol: str, entry_price: float) -> float:
        """Calculate appropriate position size based on risk parameters"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return 0.0
            
        portfolio_value = await self.get_portfolio_value()
        
        # Extract risk parameters from strategy
        risk_per_trade = portfolio_value * strategy.risk_settings.get('max_drawdown_pct', 0.01)
        stop_loss_pct = strategy.risk_settings.get('stop_loss_pct', 0.02)
        
        # Calculate position size based on risk and stop loss
        if stop_loss_pct > 0:
            position_size = risk_per_trade / (stop_loss_pct * entry_price)
        else:
            position_size = 0.0
            
        # Apply additional limits
        max_position_pct = strategy.risk_settings.get('max_position_size', 0.1)
        max_position_size = portfolio_value * max_position_pct
        
        return min(position_size, max_position_size)
    
    def validate_order(self, order_event: dict) -> bool:
        """Validate if an order should be placed based on risk rules"""
        # Check daily loss limit
        if self.today_pnl < self.daily_loss_limit:
            print(f"Daily loss limit reached: {self.today_pnl:.2f} < {self.daily_loss_limit:.2f}")
            return False
            
        # Check consecutive losses (circuit breaker)
        if self.consecutive_losses >= self.max_consecutive_losses:
            print(f"Circuit breaker triggered: {self.consecutive_losses} consecutive losses")
            return False
            
        # Check position size
        symbol = order_event.get('symbol')
        quantity = order_event.get('quantity', 0)
        price = order_event.get('price', 0)
        
        # Check if we're already tracking this symbol
        current_position = self.position_tracker.get(symbol, 0)
        
        # For sell orders, ensure we have the position
        if order_event.get('side') == 'sell' and current_position < quantity:
            print(f"Insufficient position for {symbol}: {current_position} < {quantity}")
            return False
            
        return True
    
    def update_position(self, trade: Trade):
        """Update position tracker after a trade"""
        symbol = trade.symbol
        quantity = trade.quantity
        
        if symbol not in self.position_tracker:
            self.position_tracker[symbol] = 0
            
        # Update position (add for buys, subtract for sells)
        if trade.side.lower() == 'buy':
            self.position_tracker[symbol] += quantity
        else:
            self.position_tracker[symbol] -= quantity
    
    def update_pnl(self, trade: Trade):
        """Update PnL metrics after a trade"""
        self.today_pnl += trade.profit
        
        # Update consecutive losses counter
        if trade.profit < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
            
        # Update position tracker
        self.update_position(trade)