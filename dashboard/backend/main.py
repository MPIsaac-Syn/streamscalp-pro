from fastapi import FastAPI
from .routes import trades, strategies  # Corrected import path
from config.database import init_db
import logging

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(trades.router, prefix="/trades", tags=["trades"])
app.include_router(strategies.router, prefix="/strategies", tags=["strategies"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and perform startup tasks"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization complete")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}