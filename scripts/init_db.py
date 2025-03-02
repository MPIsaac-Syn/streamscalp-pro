"""
Database initialization script for StreamScalp Pro.
This script creates all database tables based on the SQLAlchemy models.
"""
import sys
import os
import logging
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.database import init_db
from models.base import Base
from models.strategy import Strategy
from models.order import Order
from models.trade import Trade

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database by creating all tables."""
    logger.info("Starting database initialization")
    
    # Initialize database
    init_db()
    
    logger.info("Database initialization completed successfully")

if __name__ == "__main__":
    main()
