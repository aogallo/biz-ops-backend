"""Unit tests for UserService."""

from unittest.mock import Mock

import pytest

from app.domain.entities.user import User, UserCreate
from app.services.user_service import UserService


class TestUserService:
    """Test UserService business logic."""

    def test_register_user(self):
        """Test user registration."""
        # Arrange
        mock_repo = Mock()
        mock_user = User(
            auth_id="auth0|12345",
            email="test@example.com",
            picture="https://example.com/pic.jpg",
            created_by="system",
        )
        mock_repo.create_user.return_value = mock_user

        service = UserService(mock_repo)
        user_data = UserCreate(
            auth_id="auth0|12345",
            email="test@example.com",
            picture="https://example.com/pic.jpg",
        )

        # Act
        result = service.register_user(user_data)

        # Assert
        assert result.auth_id == "auth0|12345"
        assert result.email == "test@example.com"
        mock_repo.create_user.assert_called_once()

    def test_get_user(self):
        """Test getting a user by auth_id."""
        # Arrange
        mock_repo = Mock()
        mock_user = User(
            auth_id="auth0|12345",
            email="test@example.com",
            created_by="system",
        )
        mock_repo.get_user_by_id.return_value = mock_user

        service = UserService(mock_repo)

        # Act
        result = service.get_user("auth0|12345")

        # Assert
        assert result is not None
        assert result.auth_id == "auth0|12345"
        mock_repo.get_user_by_id.assert_called_once_with("auth0|12345")

    def test_get_user_not_found(self):
        """Test getting a non-existent user."""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_user_by_id.return_value = None

        service = UserService(mock_repo)

        # Act
        result = service.get_user("nonexistent")

        # Assert
        assert result is None
        mock_repo.get_user_by_id.assert_called_once_with("nonexistent")

    def test_list_users(self):
        """Test listing all users."""
        # Arrange
        mock_repo = Mock()
        mock_users = [
            User(
                auth_id="auth0|1",
                email="user1@example.com",
                created_by="system",
            ),
            User(
                auth_id="auth0|2",
                email="user2@example.com",
                created_by="system",
            ),
        ]
        mock_repo.get_all_users.return_value = mock_users

        service = UserService(mock_repo)

        # Act
        result = service.list_users()

        # Assert
        assert len(result) == 2
        assert result[0].auth_id == "auth0|1"
        assert result[1].auth_id == "auth0|2"
        mock_repo.get_all_users.assert_called_once()
