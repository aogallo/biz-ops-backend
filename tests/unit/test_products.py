"""Unit tests for ProductService - testing business logic in isolation."""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.domain.entities.product import Product, ProductCreate
from app.domain.entities.user import User
from app.services.product_service import ProductService


class TestProductService:
    """Test ProductService business logic with mocked dependencies."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        return User(
            auth_id="auth0|test123",
            permissions=["create:product"],
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
        """Create a ProductService with mocked repository."""
        service = ProductService(session=mock_session, current_user=mock_user)
        # Replace the repository with our mock
        monkeypatch.setattr(service, "repository", mock_repository)
        return service

    def test_create_product_success(self, service, mock_repository):
        """Test successful product creation when name doesn't exist."""
        # Arrange
        product_data = ProductCreate(
            name="Test Laptop",
            description="A high-performance laptop",
            price=999.99,
            stock=10,
        )
        expected_product = Product(
            id=1,
            name="Test Laptop",
            description="A high-performance laptop",
            price=999.99,
            stock=10,
            created_by="auth0|test123",
        )
        # Mock repository responses
        mock_repository.get_by_name.return_value = None  # No existing product
        mock_repository.create.return_value = expected_product

        # Act
        result = service.create_product(product_request=product_data)

        # Assert
        assert result.id == 1
        assert result.name == "Test Laptop"
        assert result.description == "A high-performance laptop"
        assert result.price == 999.99
        assert result.stock == 10
        # Verify repository methods were called correctly
        mock_repository.get_by_name.assert_called_once_with(name="Test Laptop")
        mock_repository.create.assert_called_once_with(product=product_data)

    def test_create_product_duplicate_name(self, service, mock_repository):
        """Test that creating a product
        with duplicate name raises 409 error."""
        # Arrange
        product_data = ProductCreate(
            name="Existing Product",
            description="A product",
            price=99.99,
            stock=5,
        )
        existing_product = Product(
            id=1,
            name="Existing Product",
            description="Already exists",
            price=99.99,
            stock=5,
            created_by="other_user",
        )
        # Mock: Product with same name already exists
        mock_repository.get_by_name.return_value = existing_product

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_product(product_request=product_data)

        # Verify error details
        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail).lower()
        # Verify create was never called
        mock_repository.create.assert_not_called()

    def test_list_all_products(self, service, mock_repository):
        """Test listing all products."""
        # Arrange
        expected_products = [
            Product(
                id=1,
                name="Product A",
                description="Description A",
                price=10.00,
                stock=5,
                created_by="user1",
            ),
            Product(
                id=2,
                name="Product B",
                description="Description B",
                price=20.00,
                stock=10,
                created_by="user2",
            ),
        ]
        mock_repository.get_all.return_value = expected_products

        # Act
        result = service.list_all_products()

        # Assert
        assert len(result) == 2
        assert result[0].name == "Product A"
        assert result[1].name == "Product B"
        mock_repository.get_all.assert_called_once()
