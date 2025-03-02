"""
Risk management module for StreamScalp Pro.

This module is responsible for evaluating and managing trading risks,
including position sizing, maximum drawdown, and exposure limits.
"""
import logging
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta

from utils.logger import setup_logger

logger = setup_logger("risk_manager")

class RiskManager:
    """
    Risk manager for evaluating and managing trading risks.
    
    Attributes:
        config (Dict[str, Any]): Risk manager configuration
        max_position_size (float): Maximum position size as percentage of account balance
        max_daily_loss (float): Maximum daily loss as percentage of account balance
        max_open_positions (int): Maximum number of concurrent open positions
        max_exposure_per_asset (float): Maximum exposure per asset as percentage of account balance
        open_positions (Dict[str, Dict]): Currently open positions
        daily_pnl (float): Daily profit and loss
        daily_trades (List[Dict]): List of trades executed today
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the risk manager.
        
        Args:
            config: Risk manager configuration
        """
        self.config = config or {}
        self.max_position_size = self.config.get("max_position_size", 0.05)  # 5% of account balance
        self.max_daily_loss = self.config.get("max_daily_loss", 0.02)  # 2% of account balance
        self.max_open_positions = self.config.get("max_open_positions", 5)
        self.max_exposure_per_asset = self.config.get("max_exposure_per_asset", 0.10)  # 10% of account balance
        
        self.open_positions = {}
        self.daily_pnl = 0.0
        self.daily_trades = []
        self.last_reset = datetime.utcnow()
        
        logger.info(f"Risk manager initialized with config: {self.config}")
    
    async def start(self):
        """Start the risk manager and schedule daily reset"""
        logger.info("Starting risk manager")
        asyncio.create_task(self._schedule_daily_reset())
    
    async def stop(self):
        """Stop the risk manager"""
        logger.info("Stopping risk manager")
    
    async def _schedule_daily_reset(self):
        """Schedule daily reset of risk metrics"""
        while True:
            now = datetime.utcnow()
            next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            seconds_until_reset = (next_day - now).total_seconds()
            
            logger.info(f"Scheduling next risk metrics reset in {seconds_until_reset} seconds")
            await asyncio.sleep(seconds_until_reset)
            await self.reset_daily_metrics()
    
    async def reset_daily_metrics(self):
        """Reset daily risk metrics"""
        logger.info("Resetting daily risk metrics")
        self.daily_pnl = 0.0
        self.daily_trades = []
        self.last_reset = datetime.utcnow()
    
    async def evaluate_order(self, order: Dict[str, Any], account_balance: float) -> Dict[str, Any]:
        """
        Evaluate if an order meets risk management criteria.
        
        Args:
            order: Order details
            account_balance: Current account balance
            
        Returns:
            Dict with evaluation result and reason if rejected
        """
        symbol = order.get("symbol")
        side = order.get("side")
        quantity = order.get("quantity", 0)
        price = order.get("price", 0)
        
        order_value = quantity * price
        position_size_pct = order_value / account_balance if account_balance > 0 else float('inf')
        
        # Check position size limit
        if position_size_pct > self.max_position_size:
            logger.warning(f"Order rejected: Position size {position_size_pct:.2%} exceeds maximum {self.max_position_size:.2%}")
            return {
                "approved": False,
                "reason": f"Position size {position_size_pct:.2%} exceeds maximum {self.max_position_size:.2%}"
            }
        
        # Check maximum open positions
        if len(self.open_positions) >= self.max_open_positions and side.lower() == "buy":
            logger.warning(f"Order rejected: Maximum open positions ({self.max_open_positions}) reached")
            return {
                "approved": False,
                "reason": f"Maximum open positions ({self.max_open_positions}) reached"
            }
        
        # Check asset exposure
        current_exposure = 0
        for pos_symbol, pos_data in self.open_positions.items():
            if pos_symbol == symbol:
                current_exposure += pos_data.get("value", 0)
        
        current_exposure_pct = current_exposure / account_balance if account_balance > 0 else 0
        new_exposure_pct = current_exposure_pct
        
        if side.lower() == "buy":
            new_exposure_pct += position_size_pct
        
        if new_exposure_pct > self.max_exposure_per_asset:
            logger.warning(f"Order rejected: Total exposure to {symbol} ({new_exposure_pct:.2%}) exceeds maximum {self.max_exposure_per_asset:.2%}")
            return {
                "approved": False,
                "reason": f"Total exposure to {symbol} ({new_exposure_pct:.2%}) exceeds maximum {self.max_exposure_per_asset:.2%}"
            }
        
        # Check daily loss limit
        if self.daily_pnl < 0 and abs(self.daily_pnl) > account_balance * self.max_daily_loss:
            logger.warning(f"Order rejected: Daily loss limit reached ({abs(self.daily_pnl):.2f} > {account_balance * self.max_daily_loss:.2f})")
            return {
                "approved": False,
                "reason": f"Daily loss limit reached ({abs(self.daily_pnl):.2f} > {account_balance * self.max_daily_loss:.2f})"
            }
        
        logger.info(f"Order approved: {symbol} {side} {quantity} @ {price}")
        return {"approved": True}
    
    async def record_position_open(self, position: Dict[str, Any]):
        """
        Record a new open position.
        
        Args:
            position: Position details
        """
        symbol = position.get("symbol")
        self.open_positions[symbol] = position
        logger.info(f"Position opened: {symbol} - {position}")
    
    async def record_position_close(self, symbol: str, pnl: float):
        """
        Record a position close and update daily PnL.
        
        Args:
            symbol: Symbol of the closed position
            pnl: Profit and loss from the position
        """
        if symbol in self.open_positions:
            position = self.open_positions.pop(symbol)
            self.daily_pnl += pnl
            logger.info(f"Position closed: {symbol} - PnL: {pnl:.2f} - Daily PnL: {self.daily_pnl:.2f}")
        else:
            logger.warning(f"Attempted to close unknown position: {symbol}")
    
    async def record_trade(self, trade: Dict[str, Any]):
        """
        Record a trade and update risk metrics.
        
        Args:
            trade: Trade details
        """
        self.daily_trades.append(trade)
        
        # Update PnL if this is a closing trade
        if trade.get("is_closing_trade", False):
            pnl = trade.get("pnl", 0)
            self.daily_pnl += pnl
            logger.info(f"Trade recorded: {trade.get('symbol')} - PnL: {pnl:.2f} - Daily PnL: {self.daily_pnl:.2f}")
        else:
            logger.info(f"Trade recorded: {trade.get('symbol')} - {trade.get('side')} {trade.get('quantity')} @ {trade.get('price')}")
    
    async def get_risk_metrics(self) -> Dict[str, Any]:
        """
        Get current risk metrics.
        
        Returns:
            Dict with current risk metrics
        """
        return {
            "open_positions": len(self.open_positions),
            "open_positions_details": self.open_positions,
            "daily_pnl": self.daily_pnl,
            "daily_trades_count": len(self.daily_trades),
            "max_position_size": self.max_position_size,
            "max_daily_loss": self.max_daily_loss,
            "max_open_positions": self.max_open_positions,
            "max_exposure_per_asset": self.max_exposure_per_asset,
            "last_reset": self.last_reset.isoformat()
        }
    
    async def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update risk manager configuration.
        
        Args:
            new_config: New configuration values
            
        Returns:
            Updated configuration
        """
        self.config.update(new_config)
        
        # Update risk parameters
        if "max_position_size" in new_config:
            self.max_position_size = new_config["max_position_size"]
        if "max_daily_loss" in new_config:
            self.max_daily_loss = new_config["max_daily_loss"]
        if "max_open_positions" in new_config:
            self.max_open_positions = new_config["max_open_positions"]
        if "max_exposure_per_asset" in new_config:
            self.max_exposure_per_asset = new_config["max_exposure_per_asset"]
        
        logger.info(f"Risk manager configuration updated: {self.config}")
        return self.config
