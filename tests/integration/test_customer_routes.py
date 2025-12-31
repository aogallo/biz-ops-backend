"""Integration tests for customer routes."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.internal.business_partner.entity import BusinessPartner


@pytest.mark.integration
class TestBusinessPartnerRoutes:
    """Integration tests for /customers endpoints."""

    API_PREFIX = "/api/v1"

    def test_list_customers_unauthorized(self, client: TestClient):
        """Test that listing customers without auth token fails."""
        # client fixture has NO auth - should get 403
        response = client.get(f"{self.API_PREFIX}/customers")

        print(f"\nUnauthorized test - Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]

    def test_list_customers_success(
        self,
        authenticated_client: TestClient,
        engine,
        test_user,
    ):
        """Test listing customers with valid authentication."""
        # Create customers in the test_user's organization
        with Session(engine) as session:
            customer1 = BusinessPartner(
                name="Test BusinessPartner 1",
                nit="12345",
                email="customer1@example.com",
                address="123 Main St",
                organization_id=test_user.organization_id,
                is_vendor=False,
                is_customer=True,
                created_by="auth0|test123",
            )
            customer2 = BusinessPartner(
                name="Test BusinessPartner 2",
                nit="67890",
                email="customer2@example.com",
                address="456 Oak Ave",
                organization_id=test_user.organization_id,
                is_vendor=False,
                is_customer=True,
                created_by="auth0|test123",
            )
            session.add_all([customer1, customer2])
            session.commit()

        # Now list customers via API
        response = authenticated_client.get(f"{self.API_PREFIX}/customers")

        print(f"\nList customers - Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}\n"
            f"Response: {response.text}"
        )

        data = response.json()

        # Verify response structure
        assert "customers" in data, (
            f"Expected 'customers' key in response: {data}"
        )
        assert "pagination" in data, (
            f"Expected 'pagination' key in response: {data}"
        )

        # Verify pagination metadata
        pagination = data["pagination"]
        assert pagination["total"] == 2
        assert pagination["pageSize"] == 10
        assert pagination["pageIndex"] == 0

        # Verify customer data
        customers = data["customers"]
        assert len(customers) == 2
        assert customers[0]["name"] == "Test BusinessPartner 1"
        assert customers[0]["email"] == "customer1@example.com"
        assert customers[1]["name"] == "Test BusinessPartner 2"

    def test_list_customers_empty_result(
        self, authenticated_client: TestClient
    ):
        """Test listing customers when database is empty."""
        response = authenticated_client.get(f"{self.API_PREFIX}/customers")

        assert response.status_code == 200
        data = response.json()

        assert "customers" in data
        assert "pagination" in data
        assert data["customers"] == []
        assert data["pagination"]["total"] == 0

    def test_list_customers_pagination(
        self,
        authenticated_client: TestClient,
        engine,
        test_user,
    ):
        """Test customer list pagination."""
        # Create 15 customers in the test_user's organization
        with Session(engine) as session:
            customers = [
                BusinessPartner(
                    name=f"BusinessPartner {i}",
                    nit=f"{10000 + i}",
                    email=f"customer{i}@example.com",
                    organization_id=test_user.organization_id,
                    is_vendor=False,
                    is_customer=True,
                    created_by="auth0|test123",
                )
                for i in range(15)
            ]
            session.add_all(customers)
            session.commit()

        # Test first page (limit 10)
        response = authenticated_client.get(
            f"{self.API_PREFIX}/customers?page=1&limit=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["customers"]) == 10
        assert data["pagination"]["total"] == 15
        assert data["pagination"]["pageSize"] == 10
        assert data["pagination"]["pageIndex"] == 0

        # Test second page
        response = authenticated_client.get(
            f"{self.API_PREFIX}/customers?page=2&limit=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["customers"]) == 5  # Remaining 5 customers
        assert data["pagination"]["total"] == 15
        assert data["pagination"]["pageIndex"] == 1

        # Test custom page size
        response = authenticated_client.get(
            f"{self.API_PREFIX}/customers?page=1&limit=5"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["customers"]) == 5
        assert data["pagination"]["total"] == 15
        assert data["pagination"]["pageSize"] == 5
