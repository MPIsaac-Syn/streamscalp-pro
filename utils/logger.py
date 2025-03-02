"""
Logging utility for StreamScalp Pro.

This module provides standardized logging configuration across the application.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

# Configure default logging format
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_DIR = 'logs'

def setup_logger(name: str, 
                log_level: Optional[int] = None, 
                log_format: Optional[str] = None,
                log_to_file: bool = True,
                log_to_console: bool = True) -> logging.Logger:
    """
    Set up a logger with standardized configuration.
    
    Args:
        name: Logger name
        log_level: Logging level (default: INFO)
        log_format: Log message format
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        
    Returns:
        Configured logger
    """
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Only configure if it hasn't been configured yet
    if not logger.handlers:
        # Set log level
        level = log_level or DEFAULT_LOG_LEVEL
        logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(log_format or DEFAULT_FORMAT)
        
        # Add console handler if requested
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Add file handler if requested
        if log_to_file:
            # Create logs directory if it doesn't exist
            if not os.path.exists(DEFAULT_LOG_DIR):
                os.makedirs(DEFAULT_LOG_DIR)
            
            # Create rotating file handler
            log_file = os.path.join(DEFAULT_LOG_DIR, f"{name}.log")
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger


class TradeLogger:
    """
    Logger class specifically for trade-related operations.
    Provides convenient methods for logging trade events.
    """
    
    def __init__(self, log_level=None):
        """Initialize the trade logger"""
        self.logger = setup_logger('trades', log_level=log_level)
    
    def info(self, message, **kwargs):
        """Log an info message with optional extra context"""
        self.logger.info(message, extra=kwargs if kwargs else None)
    
    def error(self, message, **kwargs):
        """Log an error message with optional extra context"""
        self.logger.error(message, extra=kwargs if kwargs else None)
    
    def warning(self, message, **kwargs):
        """Log a warning message with optional extra context"""
        self.logger.warning(message, extra=kwargs if kwargs else None)
    
    def debug(self, message, **kwargs):
        """Log a debug message with optional extra context"""
        self.logger.debug(message, extra=kwargs if kwargs else None)
    
    def trade_created(self, trade_id, symbol, entry_price, position_size, side):
        """Log trade creation event"""
        self.info(
            f"Trade created: ID={trade_id}, Symbol={symbol}, Entry={entry_price}, Size={position_size}, Side={side}",
            trade_id=trade_id,
            symbol=symbol,
            entry_price=entry_price,
            position_size=position_size,
            side=side,
            event="trade_created"
        )
    
    def trade_closed(self, trade_id, symbol, exit_price, pnl):
        """Log trade closing event"""
        self.info(
            f"Trade closed: ID={trade_id}, Symbol={symbol}, Exit={exit_price}, PnL={pnl}",
            trade_id=trade_id,
            symbol=symbol,
            exit_price=exit_price,
            pnl=pnl,
            event="trade_closed"
        )