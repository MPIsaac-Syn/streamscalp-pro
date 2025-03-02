from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
from typing import Dict, Any, List
import psutil
import os
import asyncio

from config.database import get_db
from adapters import BinanceAdapter, AlpacaAdapter
from config.settings import get_settings
from utils.logger import setup_logger
from utils.error_handler import safe_execute_async, with_error_handler_async, AppException

# Setup logger
logger = setup_logger("health")
router = APIRouter(tags=["health"])
settings = get_settings()

class HealthCheck:
    def __init__(self):
        self.start_time = time.time()
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get system resource information"""
        return {
            "cpu_usage": psutil.cpu_percent(interval=0.1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "uptime_seconds": int(time.time() - self.start_time)
        }
        
    @with_error_handler_async
    async def check_database(self, db: Session) -> Dict[str, bool]:
        """Check database connection"""
        try:
            # Execute a simple query to check connection
            db.execute(text("SELECT 1"))
            return {"status": True, "message": "Database connection successful"}
        except Exception as e:
            raise AppException(f"Database health check failed: {str(e)}")
            
    @with_error_handler_async
    async def check_exchanges(self) -> Dict[str, Dict[str, Any]]:
        """Check exchange connections"""
        results = {}
        
        # Check Binance
        try:
            binance = BinanceAdapter(
                api_key=settings.binance_api_key,
                api_secret=settings.binance_api_secret
            )
            await binance.connect()
            btc_data = await binance.get_market_data("BTCUSDT")
            results["binance"] = {
                "status": True,
                "message": "Binance connection successful",
                "data": {"price": btc_data.get("last")}
            }
        except Exception as e:
            raise AppException(f"Binance health check failed: {str(e)}")
            
        # Check Alpaca
        try:
            alpaca = AlpacaAdapter(
                api_key=settings.alpaca_api_key,
                api_secret=settings.alpaca_api_secret
            )
            await alpaca.connect()
            account_info = await alpaca.get_account_info()
            results["alpaca"] = {
                "status": True,
                "message": "Alpaca connection successful",
                "data": {"account_status": account_info.get("status")}
            }
        except Exception as e:
            raise AppException(f"Alpaca health check failed: {str(e)}")
            
        return results
        
    @with_error_handler_async
    async def get_health_status(self, db: Session = None) -> Dict[str, Any]:
        """Get overall health status"""
        system_info = self.get_system_info()
        
        # Check database if db session is provided
        db_status = {"status": "unknown", "message": "Database check skipped"}
        if db:
            db_status = await self.check_database(db)
        
        # Check exchanges
        try:
            exchange_status = await self.check_exchanges()
        except AppException as e:
            logger.error(f"Exchange health check failed: {str(e)}")
            exchange_status = {
                "binance": {"status": False, "message": f"Check failed: {str(e)}"},
                "alpaca": {"status": False, "message": f"Check failed: {str(e)}"}
            }
        
        # Determine overall status
        overall_status = "healthy"
        if db and not db_status["status"]:
            overall_status = "unhealthy"
        
        exchange_failures = sum(1 for _, status in exchange_status.items() if not status["status"])
        if exchange_failures > 0:
            if exchange_failures == len(exchange_status):
                overall_status = "unhealthy"  # All exchanges failed
            else:
                overall_status = "degraded"   # Some exchanges failed
                
        # Check system resources
        if system_info["cpu_usage"] > 90 or system_info["memory_usage"] > 90:
            if overall_status == "healthy":
                overall_status = "degraded"
            
        return {
            "status": overall_status,
            "system": system_info,
            "database": db_status,
            "exchanges": exchange_status,
            "version": "1.0.0",  # Replace with actual version
            "timestamp": time.time()
        }


health_check = HealthCheck()

# Standalone health check function
@safe_execute_async
async def check_system_health() -> Dict[str, Any]:
    """
    Standalone function to check system health.
    
    This function can be used outside of the FastAPI context
    to check the health of the system.
    
    Returns:
        Dict containing health status information
    """
    from config.database import SessionLocal
    
    # Create a database session
    db = SessionLocal()
    try:
        return await health_check.get_health_status(db)
    finally:
        db.close()

@router.get("/health", summary="Get system health status")
@safe_execute_async
async def get_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get the health status of the system including:
    - System resources (CPU, memory, disk usage)
    - Database connection
    - Exchange connections
    - Overall system status
    """
    return await health_check.get_health_status(db)

@router.get("/health/liveness", summary="Liveness probe for Kubernetes")
@safe_execute_async
async def liveness_probe() -> Dict[str, str]:
    """
    Simple liveness probe that always returns success if the application is running.
    Used by Kubernetes to determine if the pod should be restarted.
    """
    return {"status": "alive"}

@router.get("/health/readiness", summary="Readiness probe for Kubernetes")
@safe_execute_async
async def readiness_probe(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Readiness probe that checks if the application is ready to receive traffic.
    Checks database connection and returns success only if database is available.
    """
    db_status = await health_check.check_database(db)
    if not db_status["status"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application is not ready: Database connection failed"
        )
    return {"status": "ready"}
