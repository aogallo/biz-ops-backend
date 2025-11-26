"""Pytest configuration and shared fixtures."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.domain.entities.product import Product
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


@pytest.fixture(name="test_user")
def test_user_fixture() -> User:
    """Create a test user (not persisted to database)."""
    user = User(
        auth_id="auth0|test123",
        permissions=["read", "write"],
    )
    return user


@pytest.fixture(name="test_product")
def test_product_fixture(engine) -> Product:
    """Create a test product in the database."""
    # Use a new session from the same engine to ensure data persists
    with Session(engine) as session:
        product = Product(
            name="Test Product",
            description="A test product for integration tests",
            price=99.99,
            stock=10,
            created_by="auth0|test123",
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        # Return the product (it's now detached from session but data is in DB)
        return product


@pytest.fixture(name="mock_verify_token")
def mock_verify_token_fixture():
    """Mock the JWT token verification payload."""
    return {
        "sub": "auth0|test123",
        "email": "test@example.com",
        "picture": "https://example.com/avatar.jpg",
    }


@pytest.fixture(name="mock_get_current_user")
def mock_get_current_user_fixture(test_user: User):
    """Mock the get_current_user dependency."""
    return test_user


@pytest.fixture(name="client")
def client_fixture(engine) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database session only.

    Use authenticated_client for tests that need authentication.
    """

    def get_session_override():
        # Create a new session from the same engine
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="authenticated_client")
def authenticated_client_fixture(
    engine,
    mock_verify_token,
    mock_get_current_user,
) -> Generator[TestClient, None, None]:
    """Create a test client with authentication mocks applied.

    Use this fixture for tests that require authentication.
    """

    def get_session_override():
        # Create a new session from the same engine
        # shares data with test_product
        with Session(engine) as session:
            yield session

    # Override database session
    app.dependency_overrides[get_session] = get_session_override

    # Override authentication dependencies
    from app.dependencies import get_current_user, verify_token

    app.dependency_overrides[verify_token] = lambda: mock_verify_token
    app.dependency_overrides[get_current_user] = lambda: mock_get_current_user

    client = TestClient(app)
    yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
def clean_database(engine):
    """Clean database tables between tests."""
    # This runs before each test
    yield
    # This runs after each test - clear all data
    from sqlmodel import select

    with Session(engine) as session:
        # Delete all products (add other tables as needed)
        from app.domain.entities.product import Product

        products = session.exec(select(Product)).all()
        for product in products:
            session.delete(product)
        session.commit()


@pytest.fixture(autouse=True)
def set_test_env():
    """Set environment variables for testing."""
    os.environ.setdefault("AUTH0_DOMAIN", "test.auth0.com")
    os.environ.setdefault("AUTH0_AUDIENCE", "https://test-api")
    os.environ.setdefault("AUTH0_ISSUER", "https://test.auth0.com/")
    os.environ.setdefault("DATABASE_URI", "sqlite:///:memory:")
