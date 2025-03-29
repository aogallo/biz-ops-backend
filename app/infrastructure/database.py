# DB Connection: Uses SQLAlchemy async engine
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

logger = logging.getLogger(__name__)

# postgresql+asyncpg://user:password@localhost:5432/mydb
DATABASE_URI = os.getenv("DATABASE_URI", "")

if DATABASE_URI == "":
    raise Exception("Database configuration is missing. Please set DATABASE_URI environment variable.")

try:
    engine = create_engine(
        DATABASE_URI,
        echo=True,
        pool_pre_ping=True,  # Enable connection health checks
        pool_size=5,  # Limit connection pool size
        max_overflow=10  # Allow some overflow for peak loads
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

SessionDep: Session = Depends(get_session)
