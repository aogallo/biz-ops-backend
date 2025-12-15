"""Integration tests for company routes."""

import pytest
from fastapi.testclient import TestClient

from app.internal.company.entity import Company


@pytest.mark.integration
class TestCompanyRoutes:
    """Integration tests for /companies endpoints."""

    API_PREFIX = "/api/v1"

    def test_read_companies_unauthorized(self, client: TestClient):
        """Test that reading companies without auth token fails."""
        # client fixture has NO auth - should get 403
        response = client.get(f"{self.API_PREFIX}/companies")

        print(f"\nUnauthorized test - Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]

    def test_create_company_success(
        self,
        authenticated_client: TestClient,
    ):
        """Test creating a company with valid authentication."""
        # Use a unique name for each test run
        import time

        unique_name = f"Test Company {time.time()}"

        # Create a company via API
        company_data = {
            "name": unique_name,
            "nit": f"{int(time.time())}",
            "email": "test@company.com",
            "address": "123 Test Street",
            "managedByAccountant": True,
        }

        response = authenticated_client.post(
            f"{self.API_PREFIX}/companies",
            json=company_data,
        )

        print(f"\nCreate company - Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}\n"
            f"Response: {response.text}"
        )

        data = response.json()
        assert data["name"] == unique_name
        assert data["email"] == "test@company.com"
        assert data["address"] == "123 Test Street"
        assert data["managedByAccountant"] is True
        assert "id" in data

    def test_read_companies_success(
        self,
        authenticated_client: TestClient,
        engine,  # Need engine to create company
    ):
        """Test reading companies with valid authentication."""
        # Create companies directly in the database
        from sqlmodel import Session

        with Session(engine) as session:
            company1 = Company(
                name="Test Company 1",
                nit="111111111",
                email="company1@test.com",
                address="123 Main St",
                managed_by_accountant=True,
                created_by="auth0|test123",
            )
            company2 = Company(
                name="Test Company 2",
                nit="222222222",
                email="company2@test.com",
                address="456 Oak Ave",
                managed_by_accountant=False,
                created_by="auth0|test123",
            )
            session.add(company1)
            session.add(company2)
            session.commit()

        # Now read companies via API
        response = authenticated_client.get(f"{self.API_PREFIX}/companies")

        print(f"\nAuthenticated test - Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}\n"
            f"Response: {response.text}"
        )

        data = response.json()

        # The response is wrapped in CompanyListResponse
        assert "companies" in data, (
            f"Expected 'companies' key in response: {data}"
        )
        assert "pagination" in data, (
            f"Expected 'pagination' key in response: {data}"
        )

        companies = data["companies"]
        pagination = data["pagination"]
        assert isinstance(companies, list)
        assert len(companies) >= 2, (
            f"Expected at least 2 companies, got {len(companies)}"
        )
        assert pagination["total"] >= 2

        # Verify company structure (check any company in the list)
        first_company = companies[0]
        assert "name" in first_company
        assert "email" in first_company
        assert "managedByAccountant" in first_company
        assert isinstance(first_company["name"], str)
        assert isinstance(first_company["email"], str)
        assert isinstance(first_company["managedByAccountant"], bool)

    def test_read_companies_filtered_by_managed_true(
        self,
        authenticated_client: TestClient,
        engine,
    ):
        """Test reading companies filtered by managed_by_accountant=true."""
        from sqlmodel import Session

        with Session(engine) as session:
            company1 = Company(
                name="Managed Company 1",
                nit="333333333",
                email="managed1@test.com",
                address="123 Main St",
                managed_by_accountant=True,
                created_by="auth0|test123",
            )
            company2 = Company(
                name="Unmanaged Company",
                nit="444444444",
                email="unmanaged@test.com",
                address="456 Oak Ave",
                managed_by_accountant=False,
                created_by="auth0|test123",
            )
            company3 = Company(
                name="Managed Company 2",
                nit="555555555",
                email="managed2@test.com",
                address="789 Pine Rd",
                managed_by_accountant=True,
                created_by="auth0|test123",
            )
            session.add_all([company1, company2, company3])
            session.commit()

        # Filter by managed_by_accountant=true
        response = authenticated_client.get(
            f"{self.API_PREFIX}/companies?managed_by_accountant=true"
        )

        print(
            f"\nFiltered (managed=true) test - Status: {response.status_code}"
        )
        print(f"Response: {response.json()}\n")

        assert response.status_code == 200

        data = response.json()
        companies = data["companies"]
        pagination = data["pagination"]

        # Should only return managed companies
        assert pagination["total"] == 2
        assert len(companies) == 2
        assert all(c["managedByAccountant"] is True for c in companies)

    def test_read_companies_filtered_by_managed_false(
        self,
        authenticated_client: TestClient,
        engine,
    ):
        """Test reading companies filtered by managed_by_accountant=false."""
        from sqlmodel import Session

        with Session(engine) as session:
            company1 = Company(
                name="Managed Company",
                nit="666666666",
                email="managed@test.com",
                address="123 Main St",
                managed_by_accountant=True,
                created_by="auth0|test123",
            )
            company2 = Company(
                name="Unmanaged Company 1",
                nit="777777777",
                email="unmanaged1@test.com",
                address="456 Oak Ave",
                managed_by_accountant=False,
                created_by="auth0|test123",
            )
            company3 = Company(
                name="Unmanaged Company 2",
                nit="888888888",
                email="unmanaged2@test.com",
                address="789 Pine Rd",
                managed_by_accountant=False,
                created_by="auth0|test123",
            )
            session.add_all([company1, company2, company3])
            session.commit()

        # Filter by managed_by_accountant=false
        response = authenticated_client.get(
            f"{self.API_PREFIX}/companies?managed_by_accountant=false"
        )

        print(
            f"\nFiltered (managed=false) test - Status: {response.status_code}"
        )
        print(f"Response: {response.json()}\n")

        assert response.status_code == 200

        data = response.json()
        companies = data["companies"]
        pagination = data["pagination"]

        # Should only return unmanaged companies
        assert pagination["total"] == 2
        assert len(companies) == 2
        assert all(c["managedByAccountant"] is False for c in companies)

    def test_update_company_success(
        self,
        authenticated_client: TestClient,
        engine,
    ):
        """Test updating a company with valid authentication."""
        from sqlmodel import Session

        # Create a company to update
        with Session(engine) as session:
            company = Company(
                name="Original Company Name",
                nit="999999999",
                email="original@test.com",
                address="123 Original St",
                managed_by_accountant=False,
                created_by="auth0|test123",
            )
            session.add(company)
            session.commit()
            session.refresh(company)
            company_id = company.id

        # Update the company
        update_data = {
            "name": "Updated Company Name",
            "managedByAccountant": True,
        }

        response = authenticated_client.patch(
            f"{self.API_PREFIX}/companies/{company_id}",
            json=update_data,
        )

        print(f"\nUpdate company - Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}\n"
            f"Response: {response.text}"
        )

        data = response.json()
        assert data["id"] == company_id
        assert data["name"] == "Updated Company Name"
        assert data["managedByAccountant"] is True
        # Email should remain unchanged
        assert data["email"] == "original@test.com"

    def test_update_company_not_found(
        self,
        authenticated_client: TestClient,
    ):
        """Test updating a non-existent company returns 404."""
        update_data = {
            "name": "Updated Name",
        }

        response = authenticated_client.patch(
            f"{self.API_PREFIX}/companies/99999",
            json=update_data,
        )

        print(
            f"\nUpdate non-existent company - Status: {response.status_code}"
        )
        print(f"Response: {response.json()}\n")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_company_partial_update(
        self,
        authenticated_client: TestClient,
        engine,
    ):
        """Test partial update of company fields."""
        from sqlmodel import Session

        # Create a company
        with Session(engine) as session:
            company = Company(
                name="Original Name",
                nit="000000000",
                email="original@test.com",
                address="123 Original St",
                managed_by_accountant=False,
                created_by="auth0|test123",
            )
            session.add(company)
            session.commit()
            session.refresh(company)
            company_id = company.id

        # Update only managed_by_accountant field
        update_data = {
            "managedByAccountant": True,
        }

        response = authenticated_client.patch(
            f"{self.API_PREFIX}/companies/{company_id}",
            json=update_data,
        )

        assert response.status_code == 200

        data = response.json()
        # Only managedByAccountant should change
        assert data["managedByAccountant"] is True
        # Other fields should remain unchanged
        assert data["name"] == "Original Name"
        assert data["email"] == "original@test.com"
        assert data["address"] == "123 Original St"
