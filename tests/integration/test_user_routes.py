"""Integration tests for user routes."""

import pytest
from fastapi.testclient import TestClient

from app.domain.entities.user import User


@pytest.mark.integration
class TestUserRoutes:
    """Integration tests for /users endpoints."""

    def test_read_users_unauthorized(self, client: TestClient):
        """Test that reading users without auth token fails."""
        response = client.get("/users/")

        assert response.status_code == 403

    def test_read_users_success(
        self,
        client: TestClient,
        test_user: User,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test reading users with valid authentication."""
        response = client.get("/users/")

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1

        # Verify user structure
        first_user = users[0]
        assert "auth_id" in first_user
        assert "email" in first_user
        assert "created_at" in first_user

    def test_health_check(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
