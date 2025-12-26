"""Unit tests for BusinessPartnerService - testing business logic in isolation."""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.internal.business_partner.entity import BusinessPartner, BusinessPartnerCreate
from app.internal.business_partner.service import BusinessPartnerService
from app.internal.business_partner.service_schemas import BusinessPartnerListServiceResponse
from app.internal.user.entity import User


class TestBusinessPartnerService:
    """Test BusinessPartnerService business logic with mocked dependencies."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        mock = Mock(spec=User)
        mock.auth_id = "auth0|test123"
        mock.auth0_user_id = "auth0|test123"
        mock.organization_id = uuid4()
        mock.permissions = ["create:customer"]
        return mock

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
        """Create a BusinessPartnerService with mocked repository."""
        # Service extracts organization_id from mock_user.organization_id
        service = BusinessPartnerService(
            session=mock_session,
            current_user=mock_user,
            organization_id=mock_user.organization_id
        )
        monkeypatch.setattr(service, "repository", mock_repository)
        return service

    def test_list_all_customers_returns_service_response(
        self, service, mock_repository
    ):
        """Test listing all customers returns BusinessPartnerListServiceResponse."""
        # Arrange
        expected_customers = [
            BusinessPartner(
                id=uuid4(),
                name="BusinessPartner A",
                nit="12345",
                email="a@example.com",
                organization_id=uuid4(),
                created_by="user1",
            ),
            BusinessPartner(
                id=uuid4(),
                name="BusinessPartner B",
                nit="67890",
                email="b@example.com",
                organization_id=uuid4(),
                created_by="user2",
            ),
        ]
        mock_repository.get_all.return_value = expected_customers
        mock_repository.get_count.return_value = 2

        # Act
        result: BusinessPartnerListServiceResponse = service.list_all_customers(
            offset=0, limit=10
        )

        # Assert - Pydantic model with attribute access
        assert isinstance(result, BusinessPartnerListServiceResponse)
        assert result.count == 2
        assert len(result.customers) == 2
        assert result.customers[0].name == "BusinessPartner A"
        assert result.customers[1].name == "BusinessPartner B"
        mock_repository.get_all.assert_called_once_with(
            offset=0, limit=10
        )
        mock_repository.get_count.assert_called_once()

    def test_list_all_customers_validates_response(
        self, service, mock_repository
    ):
        """Test that service response validates data structure."""
        # Arrange
        mock_repository.get_all.return_value = []
        mock_repository.get_count.return_value = 0

        # Act
        result = service.list_all_customers(offset=0, limit=10)

        # Assert - Pydantic ensures structure
        assert result.count == 0
        assert result.customers == []

    def test_service_response_is_immutable(self, service, mock_repository):
        """Test that service response cannot be modified (frozen)."""
        # Arrange
        mock_repository.get_all.return_value = []
        mock_repository.get_count.return_value = 0

        # Act
        result = service.list_all_customers(offset=0, limit=10)

        # Assert - frozen=True prevents modification
        with pytest.raises(
            (ValidationError, AttributeError)
        ):  # Pydantic frozen model raises one of these
            result.count = 999

    def test_list_all_customers_with_pagination(
        self, service, mock_repository
    ):
        """Test pagination parameters are passed correctly."""
        # Arrange
        mock_repository.get_all.return_value = []
        mock_repository.get_count.return_value = 0

        # Act
        result = service.list_all_customers(offset=20, limit=5)

        # Assert
        assert result.count == 0
        assert result.customers == []
        mock_repository.get_all.assert_called_once_with(
            offset=20, limit=5
        )

    def test_create_customer_success(self, service, mock_repository):
        """Test creating a customer successfully."""
        # Arrange
        customer_create = BusinessPartnerCreate(
            name="New BusinessPartner",
            nit="11111",
            email="new@example.com",
            address="123 Main St",
            is_vendor=False,
            is_customer=True,
        )
        created_customer = BusinessPartner(
            id=uuid4(),
            name="New BusinessPartner",
            nit="11111",
            email="new@example.com",
            address="123 Main St",
            organization_id=uuid4(),
            is_vendor=False,
            is_customer=True,
            created_by="auth0|test123",
        )
        mock_repository.get_by_nit.return_value = None
        mock_repository.create.return_value = created_customer

        # Act
        result = service.create_customer(customer_create)

        # Assert
        assert result == created_customer
        mock_repository.get_by_nit.assert_called_once_with("11111")
        mock_repository.create.assert_called_once_with(customer_create)

    def test_create_customer_duplicate_nit_raises_conflict(
        self, service, mock_repository
    ):
        """Test creating a customer with duplicate NIT raises 409 Conflict."""
        # Arrange
        customer_create = BusinessPartnerCreate(
            name="Duplicate BusinessPartner",
            nit="12345",
            email="duplicate@example.com",
            is_vendor=False,
            is_customer=True,
        )
        existing_customer = BusinessPartner(
            id=uuid4(),
            name="Existing BusinessPartner",
            nit="12345",
            email="existing@example.com",
            organization_id=uuid4(),
            is_vendor=False,
            is_customer=True,
            created_by="user1",
        )
        mock_repository.get_by_nit.return_value = existing_customer

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_customer(customer_create)

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "BusinessPartner already exists"
        mock_repository.get_by_nit.assert_called_once_with("12345")
        mock_repository.create.assert_not_called()
