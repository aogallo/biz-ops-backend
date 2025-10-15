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
    logger.error(f"Failed to create database engine: {str(e)}")
    raise


def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {str(e)}")
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
    try:
        with Session(engine) as session:
            # Set the session in the context
            db_token = db_context.set(session)
            try:
                yield session
            finally:
                # Reset the context
                db_context.reset(db_token)
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)}")
        raise


# Dependency to get the current session from context
def get_current_session() -> Session:
    return context.db


SessionDep = Annotated[Session, Depends(get_current_session)]
