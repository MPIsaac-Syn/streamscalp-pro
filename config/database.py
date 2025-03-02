"""
Database configuration module for StreamScalp Pro.
Provides database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.postgres_url,
    pool_pre_ping=True,  # Enables connection pool "pre-ping" feature
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.debug  # Log SQL queries in debug mode
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Dependency to get DB session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")

def init_db():
    """
    Initialize the database by creating all tables.
    Should be called during application startup.
    """
    from models.base import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
