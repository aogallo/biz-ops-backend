import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TextHealthCheckRoutes:
    """Integration tests for /health check endpoints."""

    def test_health_check(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
