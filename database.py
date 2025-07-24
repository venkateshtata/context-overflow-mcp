from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from contextlib import contextmanager
from models import Base
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./context_overflow.db")

# Create engine with proper SQLite configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Allow SQLite to be used in multiple threads
    },
    poolclass=StaticPool,  # Use static pool for SQLite
    echo=False  # Set to True for SQL query debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database by creating all tables"""
    try:
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def get_db() -> Session:
    """Get database session - for dependency injection"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

def close_database():
    """Close database connection"""
    try:
        engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

# Database health check
def check_database_health() -> bool:
    """Check if database is accessible"""
    try:
        with get_db_session() as db:
            # Simple query to test connection
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False