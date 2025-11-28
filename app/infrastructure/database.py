# DB Connection: Uses SQLAlchemy async engine
import logging
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    # SQLite doesn't support pool_size and max_overflow parameters
    # Use different configurations based on database type
    if settings.DATABASE_URI.startswith("sqlite"):
        from sqlmodel.pool import StaticPool

        engine = create_engine(
            settings.DATABASE_URI,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # PostgreSQL, MySQL, etc. support connection pooling
        engine = create_engine(
            settings.DATABASE_URI,
            echo=settings.DEBUG,
            pool_pre_ping=True,  # Enable connection health checks
            pool_size=5,  # Limit connection pool size
            max_overflow=10,  # Allow some overflow for peak loads
        )
except Exception as e:
    logger.error("Failed to create database engine: %s", str(e))
    raise


def create_db_and_tables():
    """Create the database tables"""
    try:
        SQLModel.metadata.create_all(engine)
    except SQLAlchemyError as e:
        logger.error("Failed to create database tables: %s", str(e))
        raise


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency to provide database session.

    Creates a new session for each request and ensures it's properly closed.
    """
    try:
        with Session(engine) as session:
            yield session
    except SQLAlchemyError as e:
        logger.error("Database session error: %s", str(e))
        raise


SessionDep = Annotated[Session, Depends(get_session)]
