import asyncio
import logging
import argparse
from typing import Dict, Any

from utils.logger import setup_logger
from config.settings import settings

# Configure logging
logger = setup_logger("main")

async def main(args):
    """Main application entry point"""
    logger.info("Starting StreamScalp Pro")
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    try:
        # Import modules here to avoid import errors when just showing help
        from utils.di_container import container
        from config.database import init_db
        from utils.health import check_system_health
        from utils.metrics import start_metrics_server
        
        # Initialize database
        init_db()
        logger.info("Database initialized")
        
        # Initialize Redis configuration
        redis_config = {
            "host": settings.redis_host,
            "port": settings.redis_port,
            "db": 0,
            "password": settings.redis_password
        }
        
        # Initialize event bus
        event_bus_config = {
            "redis": redis_config
        }
        event_bus = await container.create_event_bus(event_bus_config)
        logger.info("Event bus initialized")
        
        # Initialize exchange adapter
        exchange_config = {
            "api_key": settings.binance_api_key,
            "api_secret": settings.binance_api_secret,
            "testnet": settings.binance_testnet
        }
        exchange_adapter = await container.create_exchange_adapter("binance", exchange_config)
        logger.info("Exchange adapter initialized")
        
        # Initialize risk manager
        risk_config = {
            "max_position_size": settings.max_position_size,
            "max_daily_loss": settings.max_daily_loss,
            "max_open_positions": settings.max_open_positions,
            "max_exposure_per_asset": settings.max_exposure_per_asset
        }
        risk_manager = await container.create_risk_manager(risk_config)
        logger.info("Risk manager initialized")
        
        # Initialize order manager
        order_manager_config = {
            "risk": risk_config
        }
        order_manager = await container.create_order_manager(order_manager_config)
        logger.info("Order manager initialized")
        
        # Start metrics server
        metrics_server = asyncio.create_task(start_metrics_server())
        logger.info("Metrics server started")
        
        # Perform initial health check
        health_status = await check_system_health()
        logger.info(f"Initial health check: {health_status}")
        
        try:
            # Keep the application running
            while True:
                await asyncio.sleep(60)
                # Periodic health check
                health_status = await check_system_health()
                if not health_status["status"] == "healthy":
                    logger.warning(f"Health check failed: {health_status}")
        except asyncio.CancelledError:
            logger.info("Shutdown signal received")
        finally:
            # Graceful shutdown
            logger.info("Shutting down services")
            await container.shutdown()
            metrics_server.cancel()
            logger.info("All services stopped")
    
    except Exception as e:
        logger.exception(f"Error during application startup: {e}")
        raise

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="StreamScalp Pro - A professional trading system for scalping strategies",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode with verbose logging"
    )
    
    parser.add_argument(
        "--exchange", 
        choices=["binance", "alpaca"], 
        default="binance",
        help="Trading exchange to use"
    )
    
    parser.add_argument(
        "--testnet", 
        action="store_true", 
        help="Use exchange testnet/paper trading"
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to custom configuration file"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.exception(f"Application terminated due to error: {e}")