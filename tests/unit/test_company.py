"""Unit tests for CompanyService - testing business logic in isolation."""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.internal.company.entity import Company, CompanyCreate
from app.internal.company.service import CompanyService
from app.internal.user.entity import User


class TestCompanyService:
    """Test CompanyService business logic with mocked dependencies."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        return User(
            auth_id="auth0|test123",
            permissions=["create:company"],
        )

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return Mock()

    @pytest.fixture
    def service(self, mock_session, mock_user, mock_repository, monkeypatch):
        """Create a CompanyService with mocked repository."""
        service = CompanyService(session=mock_session, current_user=mock_user)
        # Replace the repository with our mock
        monkeypatch.setattr(service, "repository", mock_repository)
        return service

    def test_create_company_success(self, service, mock_repository):
        """Test successful company creation when name doesn't exist."""
        # Arrange
        company_data = CompanyCreate(
            name="Test Company Inc",
            nit="123456789",
            email="test@company.com",
            address="123 Main St",
            managed_by_accountant=True,
        )
        expected_company = Company(
            id=1,
            name="Test Company Inc",
            nit="123456789",
            email="test@company.com",
            address="123 Main St",
            managed_by_accountant=True,
            created_by="auth0|test123",
        )
        # Mock repository responses
        mock_repository.get_company_by_nit.return_value = (
            None  # No existing company
        )
        mock_repository.create.return_value = expected_company

        # Act
        result = service.create_company(company=company_data)

        # Assert
        assert result.id == 1
        assert result.name == "Test Company Inc"
        assert result.email == "test@company.com"
        assert result.address == "123 Main St"
        assert result.managed_by_accountant is True
        # Verify repository methods were called correctly
        mock_repository.get_company_by_nit.assert_called_once_with(
            nit="123456789"
        )
        mock_repository.create.assert_called_once_with(company=company_data)

    def test_create_company_duplicate_name(self, service, mock_repository):
        """Test that creating a company with duplicate name raises 409 error."""
        # Arrange
        company_data = CompanyCreate(
            name="Existing Company",
            nit="987654321",
            email="test@existing.com",
            address="456 Oak Ave",
        )
        existing_company = Company(
            id=1,
            name="Existing Company",
            nit="111111111",
            email="other@existing.com",
            address="789 Pine St",
            created_by="other_user",
        )
        # Mock: Company with same nit already exists
        mock_repository.get_company_by_nit.return_value = existing_company

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_company(company=company_data)

        # Verify error details
        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail).lower()
        # Verify create was never called
        mock_repository.create.assert_not_called()

    def test_update_company_success(self, service, mock_repository):
        """Test successful company update."""
        # Arrange
        company_id = 1
        existing_company = Company(
            id=1,
            name="Old Company Name",
            nit="123456789",
            email="old@company.com",
            address="Old Address",
            managed_by_accountant=False,
            created_by="auth0|test123",
        )
        company_update = Company(
            name="Updated Company Name",
            nit="123456789",
            managed_by_accountant=True,
        )
        updated_company = Company(
            id=1,
            name="Updated Company Name",
            nit="123456789",
            email="old@company.com",
            address="Old Address",
            managed_by_accountant=True,
            created_by="auth0|test123",
        )
        mock_repository.get_by_id.return_value = existing_company
        mock_repository.update.return_value = updated_company

        # Act
        result = service.update_company(
            company_id=company_id, company_update=company_update
        )

        # Assert
        assert result.name == "Updated Company Name"
        assert result.managed_by_accountant is True
        mock_repository.get_by_id.assert_called_once_with(company_id)
        mock_repository.update.assert_called_once_with(
            id=company_id, model=company_update
        )

    def test_update_company_not_found(self, service, mock_repository):
        """Test that updating non-existent company raises 404 error."""
        # Arrange
        company_id = 999
        company_update = Company(name="Updated Name", nit="123456789")
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.update_company(
                company_id=company_id, company_update=company_update
            )

        # Verify error details
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
        mock_repository.update.assert_not_called()

    def test_list_all_companies_no_filter(self, service, mock_repository):
        """Test listing all companies without filter."""
        # Arrange
        expected_companies = [
            Company(
                id=1,
                name="Company A",
                nit="111111111",
                email="a@company.com",
                address="Address A",
                managed_by_accountant=True,
                created_by="user1",
            ),
            Company(
                id=2,
                name="Company B",
                nit="222222222",
                email="b@company.com",
                address="Address B",
                managed_by_accountant=False,
                created_by="user2",
            ),
        ]
        mock_repository.get_count.return_value = 2
        mock_repository.get_all.return_value = expected_companies

        # Act
        result = service.list_all_companies(offset=0, limit=10)

        # Assert
        assert result.count == 2
        assert len(result.companies) == 2
        assert result.companies[0].name == "Company A"
        assert result.companies[1].name == "Company B"
        mock_repository.get_count.assert_called_once()
        mock_repository.get_all.assert_called_once_with(0, 10)
        mock_repository.get_by_managed_status.assert_not_called()

    def test_list_companies_filtered_by_managed_status_true(
        self, service, mock_repository
    ):
        """Test listing companies filtered by managed_by_accountant=True."""
        # Arrange
        managed_companies = [
            Company(
                id=1,
                name="Managed Company A",
                nit="333333333",
                email="a@managed.com",
                address="Address A",
                managed_by_accountant=True,
                created_by="user1",
            ),
            Company(
                id=3,
                name="Managed Company B",
                nit="555555555",
                email="b@managed.com",
                address="Address B",
                managed_by_accountant=True,
                created_by="user3",
            ),
        ]
        mock_repository.get_by_managed_status.return_value = managed_companies

        # Act
        result = service.list_all_companies(
            managed_by_accountant=True, offset=0, limit=10
        )

        # Assert
        assert result.count == 2
        assert len(result.companies) == 2
        assert all(c.managed_by_accountant is True for c in result.companies)
        mock_repository.get_by_managed_status.assert_called_once_with(
            managed_by_accountant=True, offset=0, limit=10
        )
        mock_repository.get_count.assert_not_called()
        mock_repository.get_all.assert_not_called()

    def test_list_companies_filtered_by_managed_status_false(
        self, service, mock_repository
    ):
        """Test listing companies filtered by managed_by_accountant=False."""
        # Arrange
        unmanaged_companies = [
            Company(
                id=2,
                name="Unmanaged Company",
                nit="444444444",
                email="c@unmanaged.com",
                address="Address C",
                managed_by_accountant=False,
                created_by="user2",
            ),
        ]
        mock_repository.get_by_managed_status.return_value = (
            unmanaged_companies
        )

        # Act
        result = service.list_all_companies(
            managed_by_accountant=False, offset=0, limit=10
        )

        # Assert
        assert result.count == 1
        assert len(result.companies) == 1
        assert result.companies[0].managed_by_accountant is False
        mock_repository.get_by_managed_status.assert_called_once_with(
            managed_by_accountant=False, offset=0, limit=10
        )
        mock_repository.get_count.assert_not_called()
        mock_repository.get_all.assert_not_called()

    def test_list_companies_filtered_empty_result(
        self, service, mock_repository
    ):
        """Test listing companies with filter that returns empty result."""
        # Arrange
        mock_repository.get_by_managed_status.return_value = []

        # Act
        result = service.list_all_companies(
            managed_by_accountant=True, offset=0, limit=10
        )

        # Assert
        assert result.count == 0
        assert len(result.companies) == 0
        mock_repository.get_by_managed_status.assert_called_once_with(
            managed_by_accountant=True, offset=0, limit=10
        )

    def test_get_company_by_id(self, service, mock_repository):
        """Test getting the company by id."""
        existing_company = Company(
            id=2,
            name="Unmanaged Company",
            nit="444444444",
            email="c@unmanaged.com",
            address="Address C",
            managed_by_accountant=False,
            created_by="user2",
        )

        mock_repository.get_by_id.return_value = existing_company

        result = service.get_by_id(2)

        assert result.id == 2
        assert result.managed_by_accountant is False

    def test_get_company_by_id_not_found(self, service, mock_repository):
        """Test that getting non-existent company raises 404 error."""
        # Arrange
        company_id = 999
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_by_id(id=company_id)

        # Verify error details
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
