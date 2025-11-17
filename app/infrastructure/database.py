# DB Connection: Uses SQLAlchemy async engine
import logging
from contextvars import ContextVar
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.domain.entities.user import User

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
    logger.error("Failed to create database engine: %s", str(e))
    raise


def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
    except SQLAlchemyError as e:
        logger.error("Failed to create database tables: %s", str(e))
        raise


# Create context variables to store the current session and user
db_context: ContextVar[Session | None] = ContextVar("db_context", default=None)
user_context: ContextVar[User | None] = ContextVar(
    "user_context", default=None
)


class RequestContext:
    @property
    def current_user(self) -> User:
        user = user_context.get()
        if user is None:
            raise RuntimeError("No authenticated user found in context")
        return user

    @property
    def db(self) -> Session:
        session = db_context.get()
        if session is None:
            raise RuntimeError("No database session found in context")
        return session


# Create a global context instance
context = RequestContext()


def get_session():
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


def get_current_session() -> Session:
    """
    Get a database session outside of FastAPI dependency injection.
    
    Use this when you need a session in repository __init__ methods.
    Note: Sessions created this way should be managed manually.
    """
    return Session(engine)


SessionDep = Annotated[Session, Depends(get_current_session)]
