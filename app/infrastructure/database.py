# DB Connection: Uses SQLAlchemy async engine
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.exc import SQLAlchemyError
from typing import TYPE_CHECKING, Annotated
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    engine = create_engine(
        settings.DATABASE_URI,
        echo=settings.DEBUG,
        pool_pre_ping=True,  # Enable connection health checks
        pool_size=5,  # Limit connection pool size
        max_overflow=10,  # Allow some overflow for peak loads
    )
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise


def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


def get_session():
    try:
        with Session(engine) as session:
            yield session
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)}")
        raise


SessionDep = Annotated[Session, Depends(get_session)]
