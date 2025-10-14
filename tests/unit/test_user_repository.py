"""Unit tests for UserRepository."""
import pytest
from sqlmodel import Session

from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl


class TestUserRepository:
    """Test UserRepository implementation."""

    def test_create_user(self, session: Session):
        """Test creating a new user."""
        repo = UserRepositoryImpl(db=session)
        user = User(
            auth_id="auth0|12345",
            email="newuser@example.com",
            picture="https://example.com/pic.jpg",
            created_by="test",
        )

        created_user = repo.create_user(user)

        assert created_user.auth_id == "auth0|12345"
        assert created_user.email == "newuser@example.com"
        assert created_user.picture == "https://example.com/pic.jpg"

    def test_get_user_by_id(self, session: Session, test_user: User):
        """Test retrieving a user by ID."""
        repo = UserRepositoryImpl(db=session)

        found_user = repo.get_user_by_id(test_user.auth_id)

        assert found_user is not None
        assert found_user.auth_id == test_user.auth_id
        assert found_user.email == test_user.email

    def test_get_user_by_id_not_found(self, session: Session):
        """Test retrieving a non-existent user."""
        repo = UserRepositoryImpl(db=session)

        found_user = repo.get_user_by_id("nonexistent")

        assert found_user is None

    def test_get_user_by_email(self, session: Session, test_user: User):
        """Test retrieving a user by email."""
        repo = UserRepositoryImpl(db=session)

        found_user = repo.get_user_by_email(test_user.email)

        assert found_user is not None
        assert found_user.email == test_user.email
        assert found_user.auth_id == test_user.auth_id

    def test_get_all_users(self, session: Session, test_user: User):
        """Test retrieving all users."""
        repo = UserRepositoryImpl(db=session)

        # Create another user
        another_user = User(
            auth_id="auth0|67890",
            email="another@example.com",
            created_by="test",
        )
        repo.create_user(another_user)

        users = repo.get_all_users()

        assert len(users) >= 2
        auth_ids = [u.auth_id for u in users]
        assert test_user.auth_id in auth_ids
        assert another_user.auth_id in auth_ids



