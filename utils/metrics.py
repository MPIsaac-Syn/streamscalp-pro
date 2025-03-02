from fastapi import APIRouter, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST, start_http_server
import time
import psutil
import asyncio
from typing import Dict, Any

from utils.logger import setup_logger

# Configure logging
logger = setup_logger("metrics")

# Create router
router = APIRouter(tags=["metrics"])

# Define metrics
REQUEST_COUNT = Counter(
    "streamscalp_request_count", 
    "Number of requests received",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "streamscalp_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)

ACTIVE_STRATEGIES = Gauge(
    "streamscalp_active_strategies",
    "Number of active trading strategies"
)

ORDER_COUNT = Counter(
    "streamscalp_order_count",
    "Number of orders placed",
    ["exchange", "symbol", "side", "status"]
)

TRADE_COUNT = Counter(
    "streamscalp_trade_count",
    "Number of trades executed",
    ["exchange", "symbol", "side"]
)

TRADE_VOLUME = Counter(
    "streamscalp_trade_volume",
    "Total volume of trades in base currency",
    ["exchange", "symbol", "side"]
)

TRADE_VALUE = Counter(
    "streamscalp_trade_value",
    "Total value of trades in quote currency",
    ["exchange", "symbol", "side"]
)

SYSTEM_CPU_USAGE = Gauge(
    "streamscalp_system_cpu_usage",
    "System CPU usage percentage"
)

SYSTEM_MEMORY_USAGE = Gauge(
    "streamscalp_system_memory_usage",
    "System memory usage percentage"
)

EXCHANGE_LATENCY = Histogram(
    "streamscalp_exchange_latency_seconds",
    "Exchange API latency in seconds",
    ["exchange", "operation"]
)

# Middleware to track request metrics
class MetricsMiddleware:
    async def __call__(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        
        # Record request latency
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(latency)
        
        # Record request count
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()
        
        return response

# Background task to update system metrics
async def update_system_metrics():
    while True:
        try:
            SYSTEM_CPU_USAGE.set(psutil.cpu_percent(interval=1))
            SYSTEM_MEMORY_USAGE.set(psutil.virtual_memory().percent)
            await asyncio.sleep(15)  # Update every 15 seconds
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
            await asyncio.sleep(60)  # Retry after a minute if there's an error

# Start a standalone metrics server
async def start_metrics_server(port=9090):
    """
    Start a standalone Prometheus metrics server.
    
    This function starts a separate HTTP server that exposes Prometheus metrics
    on the specified port. This is useful when running the application without FastAPI
    or when you want to expose metrics on a different port.
    
    Args:
        port: The port to expose metrics on (default: 9090)
    """
    try:
        logger.info(f"Starting metrics server on port {port}")
        start_http_server(port)
        # Keep the server running
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour (or any long duration)
    except Exception as e:
        logger.error(f"Error starting metrics server: {e}")
        raise

# Helper functions to record metrics
def record_order(exchange: str, symbol: str, side: str, status: str):
    """Record a new order"""
    try:
        ORDER_COUNT.labels(
            exchange=exchange,
            symbol=symbol,
            side=side,
            status=status
        ).inc()
    except Exception as e:
        logger.error(f"Error recording order metric: {e}")

def record_trade(exchange: str, symbol: str, side: str, quantity: float, price: float):
    """Record a new trade"""
    try:
        TRADE_COUNT.labels(
            exchange=exchange,
            symbol=symbol,
            side=side
        ).inc()
        
        TRADE_VOLUME.labels(
            exchange=exchange,
            symbol=symbol,
            side=side
        ).inc(quantity)
        
        TRADE_VALUE.labels(
            exchange=exchange,
            symbol=symbol,
            side=side
        ).inc(quantity * price)
    except Exception as e:
        logger.error(f"Error recording trade metric: {e}")

def record_exchange_latency(exchange: str, operation: str, latency: float):
    """Record exchange API latency"""
    try:
        EXCHANGE_LATENCY.labels(
            exchange=exchange,
            operation=operation
        ).observe(latency)
    except Exception as e:
        logger.error(f"Error recording exchange latency metric: {e}")

def update_active_strategies(count: int):
    """Update the number of active strategies"""
    try:
        ACTIVE_STRATEGIES.set(count)
    except Exception as e:
        logger.error(f"Error updating active strategies metric: {e}")

# Endpoint to expose metrics
@router.get("/metrics", summary="Get Prometheus metrics")
async def get_metrics():
    """
    Expose Prometheus metrics for monitoring.
    
    This endpoint returns metrics in the Prometheus text format,
    which can be scraped by a Prometheus server.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Initialize metrics system
def init_metrics(app=None):
    """
    Initialize metrics system.
    
    Args:
        app: FastAPI application instance (optional)
    """
    if app:
        # Add middleware if app is provided
        app.add_middleware(MetricsMiddleware)
        
        # Start background task to update system metrics
        @app.on_event("startup")
        async def start_metrics_background_task():
            asyncio.create_task(update_system_metrics())
            logger.info("Metrics background task started")
    else:
        # Just start the background task for system metrics
        asyncio.create_task(update_system_metrics())
        logger.info("Metrics background task started (standalone mode)")
