"""Pytest configuration and shared fixtures."""
import os
from typing import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.domain.entities.user import User
from app.infrastructure.database import get_session
from app.main import app


@pytest.fixture(name="engine")
def engine_fixture():
    """Create an in-memory SQLite database engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create a new database session for each test."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden dependencies."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="mock_verify_token")
def mock_verify_token_fixture():
    """Mock the JWT token verification."""
    mock_payload = {
        "sub": "auth0|test123",
        "email": "test@example.com",
        "picture": "https://example.com/avatar.jpg",
    }

    with patch("app.dependencies.verify_token", return_value=mock_payload):
        yield mock_payload


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """Create a test user in the database."""
    user = User(
        auth_id="auth0|test123",
        email="test@example.com",
        picture="https://example.com/avatar.jpg",
        created_by="test",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="mock_get_current_user")
def mock_get_current_user_fixture(test_user: User):
    """Mock the get_current_user dependency."""
    with patch("app.dependencies.get_current_user", return_value=test_user):
        yield test_user


@pytest.fixture(autouse=True)
def set_test_env():
    """Set environment variables for testing."""
    os.environ.setdefault("AUTH0_DOMAIN", "test.auth0.com")
    os.environ.setdefault("AUTH0_AUDIENCE", "https://test-api")
    os.environ.setdefault("AUTH0_ISSUER", "https://test.auth0.com/")
    os.environ.setdefault("DATABASE_URI", "sqlite:///:memory:")



