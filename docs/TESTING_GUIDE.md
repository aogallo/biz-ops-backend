# Testing Guide

This guide provides comprehensive instructions for writing unit and integration tests for the biz-ops-backend application. It follows best practices and the Builder pattern as described in [refactoring.guru](https://refactoring.guru/design-patterns/builder/python/example).

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Unit Testing](#unit-testing)
   - [Testing Builders](#testing-builders)
   - [Testing Services](#testing-services)
   - [Testing Repositories](#testing-repositories)
4. [Integration Testing](#integration-testing)
   - [Testing API Routes](#testing-api-routes)
5. [Testing Patterns](#testing-patterns)
6. [Testing Checklist](#testing-checklist)
7. [Examples](#examples)

## Overview

We use `pytest` as our testing framework. Tests run against an **in-memory SQLite database** for speed and isolation, while production and staging environments use PostgreSQL.

### Test vs Production Databases

| Environment | Database | Configuration |
|------------|----------|---------------|
| **Tests** (local & CI) | SQLite in-memory | `sqlite:///:memory:` |
| **Development** | SQLite file | `sqlite:///bizops_dev.db` |
| **Staging** | PostgreSQL | Connection string from env |
| **Production** | PostgreSQL | Connection string from env |

**Why SQLite for tests?**
- ✅ Fast (in-memory, no disk I/O)
- ✅ Isolated (each test run gets fresh database)
- ✅ No setup required (no Docker, no PostgreSQL server)
- ✅ Works identically in local and CI environments
- ✅ Deterministic (same behavior every time)

### Test Structure

We use `pytest` as our testing framework with the following structure:

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (isolated components)
│   ├── test_*_builder.py
│   ├── test_*_service.py
│   └── test_*_repository.py
└── integration/             # Integration tests (full stack)
    └── test_*_routes.py
```

## Test Structure

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_invoice_builder.py

# Run specific test class or method
uv run pytest tests/unit/test_invoice_builder.py::TestInvoiceBuilder::test_create_invoice_with_header

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/
```

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
class TestSomethingRoutes:
    pass
```

## Unit Testing

Unit tests focus on testing individual components in isolation.

### Testing Builders

Builders follow the Builder pattern from [refactoring.guru](https://refactoring.guru/design-patterns/builder/python/example). They should:
- Start with an empty constructor
- Use builder methods to set fields
- Validate required fields in the `build()` method

#### Example: Testing a Builder

```python
"""Unit tests for CustomerBuilder."""

from datetime import datetime
import pytest
from app.domain.builders.customer_builder import CustomerBuilder


class TestCustomerBuilder:
    """Test CustomerBuilder following the pure builder pattern."""

    def test_create_customer_with_all_fields(self):
        """Test creating a customer with all fields set."""
        customer = (
            CustomerBuilder()
            .with_name("Acme Corp")
            .with_nit("12345678-9")
            .with_email("contact@acme.com")
            .with_phone("555-1234")
            .with_address("123 Main St")
            .with_created_by("test_user")
            .build()
        )

        assert customer.name == "Acme Corp"
        assert customer.nit == "12345678-9"
        assert customer.email == "contact@acme.com"
        assert customer.phone == "555-1234"
        assert customer.address == "123 Main St"
        assert customer.created_by == "test_user"

    def test_create_customer_with_required_fields_only(self):
        """Test creating a customer with only required fields."""
        customer = (
            CustomerBuilder()
            .with_name("Basic Corp")
            .with_nit("98765432-1")
            .with_created_by("test_user")
            .build()
        )

        assert customer.name == "Basic Corp"
        assert customer.nit == "98765432-1"
        assert customer.created_by == "test_user"

    def test_customer_missing_required_fields(self):
        """Test that missing required fields raise ValueError."""
        # Test missing name
        with pytest.raises(ValueError, match="Customer name is required"):
            CustomerBuilder().build()

        # Test missing nit
        with pytest.raises(ValueError, match="NIT is required"):
            CustomerBuilder().with_name("Test Corp").build()

        # Test missing created_by
        with pytest.raises(ValueError, match="Created by is required"):
            (
                CustomerBuilder()
                .with_name("Test Corp")
                .with_nit("12345678-9")
                .build()
            )

    def test_customer_invalid_email(self):
        """Test that invalid email raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            (
                CustomerBuilder()
                .with_name("Test Corp")
                .with_nit("12345678-9")
                .with_email("not-an-email")
                .with_created_by("test_user")
                .build()
            )

    def test_create_with_convenience_method(self):
        """Test using convenience classmethod."""
        customer = (
            CustomerBuilder.create_with_basic_info(
                name="Quick Corp",
                nit="11111111-1",
                created_by="test_user",
            )
            .with_email("quick@corp.com")
            .build()
        )

        assert customer.name == "Quick Corp"
        assert customer.nit == "11111111-1"
        assert customer.email == "quick@corp.com"
```

### Testing Simple Entities (Without Builders)

Not all entities need builders. Simple entities can be tested by directly creating instances.

#### Example: Testing Category Entity

```python
"""Unit tests for Category entity."""

import pytest
from datetime import datetime

from app.domain.entities.category import Category, CategoryCreate


class TestCategory:
    """Test Category entity."""

    def test_create_category(self):
        """Test creating a category with all fields."""
        category = Category(
            id=1,
            name="Electronics",
            created_by="test@example.com",
            created_at=datetime.now(),
        )

        assert category.id == 1
        assert category.name == "Electronics"
        assert category.created_by == "test@example.com"
        assert category.created_at is not None

    def test_category_create_schema(self):
        """Test CategoryCreate schema validation."""
        category_data = CategoryCreate(name="Books")

        assert category_data.name == "Books"

    def test_category_name_required(self):
        """Test that category name is required."""
        with pytest.raises(ValueError):
            CategoryCreate()  # Missing required 'name' field

    def test_category_equality(self):
        """Test category comparison."""
        cat1 = Category(
            id=1,
            name="Sports",
            created_by="test@example.com",
        )
        cat2 = Category(
            id=1,
            name="Sports",
            created_by="test@example.com",
        )

        # Categories with same ID should be considered equal
        assert cat1.id == cat2.id
```

#### Example: Testing Product Entity

```python
"""Unit tests for Product entity."""

import pytest
from datetime import datetime

from app.domain.entities.product import Product, ProductCreate


class TestProduct:
    """Test Product entity."""

    def test_create_product_with_all_fields(self):
        """Test creating a product with all fields."""
        product = Product(
            id=1,
            name="Laptop",
            description="High-performance laptop",
            price=999.99,
            stock=5,
            category_id=1,
            created_by="test@example.com",
        )

        assert product.id == 1
        assert product.name == "Laptop"
        assert product.description == "High-performance laptop"
        assert product.price == 999.99
        assert product.stock == 5
        assert product.category_id == 1

    def test_create_product_with_defaults(self):
        """Test creating a product with default values."""
        product = Product(
            name="Mouse",
            price=19.99,
            created_by="test@example.com",
        )

        assert product.name == "Mouse"
        assert product.price == 19.99
        assert product.stock == 0  # Default value
        assert product.description is None  # Optional field
        assert product.category_id is None  # Optional field

    def test_product_create_schema(self):
        """Test ProductCreate schema."""
        product_data = ProductCreate(
            name="Keyboard",
            description="Mechanical keyboard",
            price=79.99,
            stock=10,
        )

        assert product_data.name == "Keyboard"
        assert product_data.price == 79.99
        assert product_data.stock == 10

    @pytest.mark.parametrize(
        "name,price,expected_valid",
        [
            ("Valid Product", 10.00, True),
            ("", 10.00, False),  # Empty name
            ("Valid Product", -5.00, False),  # Negative price
            ("Valid Product", 0, True),  # Zero price is valid
        ],
    )
    def test_product_validation(self, name, price, expected_valid):
        """Test product validation for different inputs."""
        if expected_valid:
            product = ProductCreate(name=name, price=price)
            assert product.name == name
            assert product.price == price
        else:
            with pytest.raises((ValueError, Exception)):
                ProductCreate(name=name, price=price)
```

### Testing Services

Services contain business logic and should be tested with mocked dependencies.

#### Example: Testing CustomerService

```python
"""Unit tests for CustomerService."""

from unittest.mock import Mock, MagicMock
import pytest
from fastapi import HTTPException

from app.services.customer_service import CustomerService
from app.domain.entities.customer import Customer, CustomerCreate
from app.domain.entities.user import User


class TestCustomerService:
    """Test CustomerService business logic."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        return User(
            id=1,
            auth_id="auth0|test123",
            email="test@example.com",
            created_by="test",
        )

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return Mock()

    @pytest.fixture
    def service(self, mock_user, mock_repository, monkeypatch):
        """Create a CustomerService with mocked repository."""
        service = CustomerService(current_user=mock_user)
        # Replace the repository with our mock
        monkeypatch.setattr(service, "repository", mock_repository)
        return service

    def test_create_customer_success(self, service, mock_repository):
        """Test successful customer creation."""
        # Arrange
        customer_data = CustomerCreate(
            name="Test Corp",
            nit="12345678-9",
            email="test@corp.com",
        )
        expected_customer = Customer(
            id=1,
            name="Test Corp",
            nit="12345678-9",
            email="test@corp.com",
            created_by="test",
        )
        mock_repository.get_by_nit.return_value = None
        mock_repository.create.return_value = expected_customer

        # Act
        result = service.create_customer(customer_data)

        # Assert
        assert result.id == 1
        assert result.name == "Test Corp"
        mock_repository.get_by_nit.assert_called_once_with("12345678-9")
        mock_repository.create.assert_called_once_with(customer_data)

    def test_create_customer_duplicate_nit(self, service, mock_repository):
        """Test that creating a customer with duplicate NIT raises error."""
        # Arrange
        customer_data = CustomerCreate(
            name="Duplicate Corp",
            nit="12345678-9",
            email="dupe@corp.com",
        )
        existing_customer = Customer(
            id=1,
            name="Existing Corp",
            nit="12345678-9",
            email="existing@corp.com",
            created_by="test",
        )
        mock_repository.get_by_nit.return_value = existing_customer

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_customer(customer_data)

        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail).lower()
        mock_repository.create.assert_not_called()

    def test_list_all_customers(self, service, mock_repository):
        """Test listing all customers."""
        # Arrange
        expected_customers = [
            Customer(id=1, name="Corp A", nit="11111111-1", created_by="test"),
            Customer(id=2, name="Corp B", nit="22222222-2", created_by="test"),
        ]
        mock_repository.get_all_customers.return_value = expected_customers

        # Act
        result = service.list_all_customers()

        # Assert
        assert len(result) == 2
        assert result[0].name == "Corp A"
        assert result[1].name == "Corp B"
        mock_repository.get_all_customers.assert_called_once()
```

#### Example: Testing Simple Service (CategoryService)

```python
"""Unit tests for CategoryService."""

from unittest.mock import Mock
import pytest
from sqlmodel import Session

from app.services.category_service import CategoryService
from app.domain.entities.category import Category, CategoryCreate


class TestCategoryService:
    """Test CategoryService business logic."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return Mock()

    @pytest.fixture
    def service(self, mock_repository, monkeypatch):
        """Create a CategoryService with mocked repository."""
        service = CategoryService()
        monkeypatch.setattr(service, "_category_repo", mock_repository)
        return service

    def test_create_category_success(self, service, mock_repository):
        """Test successful category creation."""
        # Arrange
        category_data = CategoryCreate(name="Electronics")
        expected_category = Category(
            id=1,
            name="Electronics",
            created_by="system",
        )
        mock_repository.create.return_value = expected_category

        # Act
        result = service.create_category(category_data)

        # Assert
        assert result.id == 1
        assert result.name == "Electronics"
        mock_repository.create.assert_called_once_with(category_data)

    def test_create_category_with_special_characters(self, service, mock_repository):
        """Test creating a category with special characters in name."""
        # Arrange
        category_data = CategoryCreate(name="Books & Magazines")
        expected_category = Category(
            id=2,
            name="Books & Magazines",
            created_by="system",
        )
        mock_repository.create.return_value = expected_category

        # Act
        result = service.create_category(category_data)

        # Assert
        assert result.name == "Books & Magazines"
```

#### Example: Testing ProductService

```python
"""Unit tests for ProductService."""

from unittest.mock import Mock, MagicMock
import pytest
from fastapi import HTTPException

from app.services.product_service import ProductService
from app.domain.entities.product import Product, ProductCreate
from app.domain.entities.user import User


class TestProductService:
    """Test ProductService business logic."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        return User(
            id=1,
            auth_id="auth0|test123",
            email="test@example.com",
            created_by="test",
        )

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return Mock()

    @pytest.fixture
    def service(self, mock_user, mock_repository, monkeypatch):
        """Create a ProductService with mocked repository."""
        service = ProductService(current_user=mock_user)
        monkeypatch.setattr(service, "_product_repo", mock_repository)
        return service

    def test_create_product_success(self, service, mock_repository):
        """Test successful product creation."""
        # Arrange
        product_data = ProductCreate(
            name="Laptop",
            description="High-end laptop",
            price=1299.99,
            stock=5,
        )
        expected_product = Product(
            id=1,
            name="Laptop",
            description="High-end laptop",
            price=1299.99,
            stock=5,
            created_by="test@example.com",
        )
        mock_repository.create.return_value = expected_product

        # Act
        result = service.create_product(product_data)

        # Assert
        assert result.id == 1
        assert result.name == "Laptop"
        assert result.price == 1299.99
        assert result.stock == 5
        mock_repository.create.assert_called_once_with(product_data)

    def test_list_products(self, service, mock_repository):
        """Test listing all products."""
        # Arrange
        expected_products = [
            Product(
                id=1,
                name="Laptop",
                price=1299.99,
                stock=5,
                created_by="test@example.com",
            ),
            Product(
                id=2,
                name="Mouse",
                price=29.99,
                stock=50,
                created_by="test@example.com",
            ),
        ]
        mock_repository.get_all.return_value = expected_products

        # Act
        result = service.list_products()

        # Assert
        assert len(result) == 2
        assert result[0].name == "Laptop"
        assert result[1].name == "Mouse"
        mock_repository.get_all.assert_called_once()

    def test_get_product_by_id_found(self, service, mock_repository):
        """Test getting a product by ID when it exists."""
        # Arrange
        expected_product = Product(
            id=1,
            name="Laptop",
            price=1299.99,
            stock=5,
            created_by="test@example.com",
        )
        mock_repository.get_by_id.return_value = expected_product

        # Act
        result = service.get_product(1)

        # Assert
        assert result.id == 1
        assert result.name == "Laptop"
        mock_repository.get_by_id.assert_called_once_with(1)

    def test_get_product_by_id_not_found(self, service, mock_repository):
        """Test getting a non-existent product raises error."""
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_product(999)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    def test_update_product_stock(self, service, mock_repository):
        """Test updating product stock."""
        # Arrange
        product = Product(
            id=1,
            name="Laptop",
            price=1299.99,
            stock=5,
            created_by="test@example.com",
        )
        mock_repository.get_by_id.return_value = product
        mock_repository.update.return_value = product

        # Act
        result = service.update_product_stock(1, 10)

        # Assert
        assert result.stock == 10
        mock_repository.update.assert_called_once()

    @pytest.mark.parametrize(
        "stock_change,expected_stock",
        [
            (5, 10),   # Increase stock
            (-3, 2),   # Decrease stock
            (0, 5),    # No change
        ],
    )
    def test_adjust_stock(self, service, mock_repository, stock_change, expected_stock):
        """Test adjusting product stock by various amounts."""
        # Arrange
        product = Product(
            id=1,
            name="Laptop",
            price=1299.99,
            stock=5,
            created_by="test@example.com",
        )
        mock_repository.get_by_id.return_value = product

        # Act
        service.adjust_stock(1, stock_change)

        # Assert
        assert product.stock == expected_stock
```


### Testing Repositories

Repositories handle data access and should be tested with a real database session (in-memory for tests).

#### Example: Testing AccountRepository

```python
"""Unit tests for AccountRepositoryImpl."""

import pytest
from sqlmodel import Session

from app.domain.entities.account import Account, AccountCreate
from app.domain.entities.user import User
from app.infrastructure.repositories.account_respository_impl import (
    AccountRepositoryImpl,
)


@pytest.mark.unit
class TestAccountRepository:
    """Test AccountRepositoryImpl data access."""

    @pytest.fixture
    def test_user(self, session: Session) -> User:
        """Create a test user."""
        user = User(
            auth_id="auth0|test123",
            email="test@example.com",
            created_by="test",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @pytest.fixture
    def repository(self, test_user: User) -> AccountRepositoryImpl:
        """Create an AccountRepository instance."""
        return AccountRepositoryImpl(current_user=test_user)

    def test_create_account(self, repository, session):
        """Test creating a new account."""
        # Arrange
        account_data = AccountCreate(
            account_number="1001",
            name="Cash",
            type="asset",
            description="Cash account",
        )

        # Act
        result = repository.create(account_data)
        session.commit()
        session.refresh(result)

        # Assert
        assert result.id is not None
        assert result.account_number == "1001"
        assert result.name == "Cash"
        assert result.type == "asset"
        assert result.created_by == "test@example.com"

    def test_get_account_by_number(self, repository, session, test_user):
        """Test retrieving account by number."""
        # Arrange
        account = Account(
            account_number="1002",
            name="Bank",
            type="asset",
            created_by=test_user.email,
        )
        session.add(account)
        session.commit()

        # Act
        result = repository.get_account_by_number("1002")

        # Assert
        assert result is not None
        assert result.account_number == "1002"
        assert result.name == "Bank"

    def test_get_account_by_number_not_found(self, repository):
        """Test that non-existent account returns None."""
        # Act
        result = repository.get_account_by_number("9999")

        # Assert
        assert result is None

    def test_get_all_accounts(self, repository, session, test_user):
        """Test retrieving all accounts."""
        # Arrange
        accounts = [
            Account(
                account_number="2001",
                name="Account 1",
                type="asset",
                created_by=test_user.email,
            ),
            Account(
                account_number="2002",
                name="Account 2",
                type="liability",
                created_by=test_user.email,
            ),
        ]
        for account in accounts:
            session.add(account)
        session.commit()

        # Act
        result = repository.get_all()

        # Assert
        assert len(result) >= 2
        account_numbers = [acc.account_number for acc in result]
        assert "2001" in account_numbers
        assert "2002" in account_numbers
```

#### Example: Testing CategoryRepository (Simple Entity)

```python
"""Unit tests for CategoryRepositoryImpl."""

import pytest
from sqlmodel import Session

from app.domain.entities.category import Category, CategoryCreate
from app.infrastructure.repositories.category_repository_impl import (
    CategoryRepositoryImpl,
)


@pytest.mark.unit
class TestCategoryRepository:
    """Test CategoryRepositoryImpl data access."""

    @pytest.fixture
    def repository(self) -> CategoryRepositoryImpl:
        """Create a CategoryRepository instance."""
        return CategoryRepositoryImpl()

    def test_create_category(self, repository, session):
        """Test creating a new category."""
        # Arrange
        category_data = CategoryCreate(name="Electronics")

        # Act
        result = repository.create(category_data)
        session.commit()
        session.refresh(result)

        # Assert
        assert result.id is not None
        assert result.name == "Electronics"
        assert result.created_at is not None

    def test_get_category_by_id(self, repository, session):
        """Test retrieving category by ID."""
        # Arrange
        category = Category(name="Books", created_by="system")
        session.add(category)
        session.commit()
        session.refresh(category)

        # Act
        result = repository.get_by_id(category.id)

        # Assert
        assert result is not None
        assert result.id == category.id
        assert result.name == "Books"

    def test_get_category_by_id_not_found(self, repository):
        """Test that non-existent category returns None."""
        # Act
        result = repository.get_by_id(99999)

        # Assert
        assert result is None

    def test_get_all_categories(self, repository, session):
        """Test retrieving all categories."""
        # Arrange
        categories = [
            Category(name="Electronics", created_by="system"),
            Category(name="Books", created_by="system"),
            Category(name="Clothing", created_by="system"),
        ]
        for category in categories:
            session.add(category)
        session.commit()

        # Act
        result = repository.get_all()

        # Assert
        assert len(result) >= 3
        category_names = [cat.name for cat in result]
        assert "Electronics" in category_names
        assert "Books" in category_names
        assert "Clothing" in category_names

    def test_update_category(self, repository, session):
        """Test updating a category."""
        # Arrange
        category = Category(name="Old Name", created_by="system")
        session.add(category)
        session.commit()
        session.refresh(category)

        # Act
        category.name = "New Name"
        category.updated_by = "admin"
        result = repository.update(category)
        session.commit()
        session.refresh(result)

        # Assert
        assert result.name == "New Name"
        assert result.updated_by == "admin"
        assert result.updated_at is not None

    def test_delete_category(self, repository, session):
        """Test deleting a category."""
        # Arrange
        category = Category(name="To Delete", created_by="system")
        session.add(category)
        session.commit()
        category_id = category.id

        # Act
        repository.delete(category_id)
        session.commit()

        # Assert
        result = repository.get_by_id(category_id)
        assert result is None

    def test_unique_category_name_constraint(self, repository, session):
        """Test that duplicate category names are not allowed."""
        # Arrange
        category1 = Category(name="Unique", created_by="system")
        session.add(category1)
        session.commit()

        # Act & Assert
        with pytest.raises(Exception):  # Database integrity error
            category2 = Category(name="Unique", created_by="system")
            session.add(category2)
            session.commit()
```

#### Example: Testing ProductRepository

```python
"""Unit tests for ProductRepositoryImpl."""

import pytest
from sqlmodel import Session

from app.domain.entities.product import Product, ProductCreate
from app.domain.entities.category import Category
from app.domain.entities.user import User
from app.infrastructure.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)


@pytest.mark.unit
class TestProductRepository:
    """Test ProductRepositoryImpl data access."""

    @pytest.fixture
    def test_category(self, session: Session) -> Category:
        """Create a test category."""
        category = Category(name="Electronics", created_by="system")
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    @pytest.fixture
    def test_user(self, session: Session) -> User:
        """Create a test user."""
        user = User(
            auth_id="auth0|test123",
            email="test@example.com",
            created_by="test",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @pytest.fixture
    def repository(self, test_user: User) -> ProductRepositoryImpl:
        """Create a ProductRepository instance."""
        return ProductRepositoryImpl(current_user=test_user)

    def test_create_product(self, repository, session, test_category):
        """Test creating a new product."""
        # Arrange
        product_data = ProductCreate(
            name="Laptop",
            description="High-end laptop",
            price=1299.99,
            stock=5,
        )

        # Act
        result = repository.create(product_data)
        session.commit()
        session.refresh(result)

        # Assert
        assert result.id is not None
        assert result.name == "Laptop"
        assert result.price == 1299.99
        assert result.stock == 5
        assert result.created_by == "test@example.com"

    def test_get_product_by_id(self, repository, session, test_user):
        """Test retrieving product by ID."""
        # Arrange
        product = Product(
            name="Mouse",
            price=29.99,
            stock=50,
            created_by=test_user.email,
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        # Act
        result = repository.get_by_id(product.id)

        # Assert
        assert result is not None
        assert result.id == product.id
        assert result.name == "Mouse"
        assert result.price == 29.99

    def test_get_products_by_category(self, repository, session, test_category, test_user):
        """Test retrieving products by category."""
        # Arrange
        products = [
            Product(
                name="Laptop",
                price=1299.99,
                stock=5,
                category_id=test_category.id,
                created_by=test_user.email,
            ),
            Product(
                name="Monitor",
                price=399.99,
                stock=10,
                category_id=test_category.id,
                created_by=test_user.email,
            ),
        ]
        for product in products:
            session.add(product)
        session.commit()

        # Act
        result = repository.get_by_category(test_category.id)

        # Assert
        assert len(result) >= 2
        product_names = [p.name for p in result]
        assert "Laptop" in product_names
        assert "Monitor" in product_names

    def test_get_products_in_stock(self, repository, session, test_user):
        """Test retrieving only products that are in stock."""
        # Arrange
        products = [
            Product(name="In Stock 1", price=10.00, stock=5, created_by=test_user.email),
            Product(name="Out of Stock", price=20.00, stock=0, created_by=test_user.email),
            Product(name="In Stock 2", price=30.00, stock=10, created_by=test_user.email),
        ]
        for product in products:
            session.add(product)
        session.commit()

        # Act
        result = repository.get_in_stock()

        # Assert
        assert len(result) >= 2
        for product in result:
            assert product.stock > 0

    def test_search_products_by_name(self, repository, session, test_user):
        """Test searching products by name."""
        # Arrange
        products = [
            Product(name="Gaming Laptop", price=1500.00, created_by=test_user.email),
            Product(name="Office Laptop", price=800.00, created_by=test_user.email),
            Product(name="Desktop PC", price=1200.00, created_by=test_user.email),
        ]
        for product in products:
            session.add(product)
        session.commit()

        # Act
        result = repository.search_by_name("Laptop")

        # Assert
        assert len(result) >= 2
        for product in result:
            assert "Laptop" in product.name
```


## Integration Testing

Integration tests verify that the entire system works together, from HTTP request to database.

### Testing API Routes

Integration tests use the FastAPI TestClient and test fixtures from `conftest.py`.

#### Example: Testing Customer Routes

```python
"""Integration tests for customer routes."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.domain.entities.customer import Customer
from app.domain.entities.user import User


@pytest.mark.integration
class TestCustomerRoutes:
    """Integration tests for /customers endpoints."""

    def __init__(self) -> None:
        self.API_PREFIX = "/api/v1"

    @pytest.fixture
    def test_customer(self, session: Session, test_user: User) -> Customer:
        """Create a test customer in the database."""
        customer = Customer(
            name="Test Corp",
            nit="12345678-9",
            email="test@corp.com",
            phone="555-1234",
            address="123 Test St",
            created_by=test_user.email,
        )
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return customer

    def test_create_customer_unauthorized(self, client: TestClient):
        """Test that creating a customer without auth fails."""
        response = client.post(
            f"{self.API_PREFIX}/customers/",
            json={
                "name": "Unauthorized Corp",
                "nit": "99999999-9",
            },
        )

        assert response.status_code == 403

    def test_create_customer_success(
        self,
        client: TestClient,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test creating a customer with valid authentication."""
        response = client.post(
            f"{self.API_PREFIX}/customers/",
            json={
                "name": "New Corp",
                "nit": "11111111-1",
                "email": "new@corp.com",
                "phone": "555-5678",
                "address": "456 New Ave",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Corp"
        assert data["nit"] == "11111111-1"
        assert data["email"] == "new@corp.com"
        assert "id" in data
        assert "created_at" in data

    def test_create_customer_duplicate_nit(
        self,
        client: TestClient,
        test_customer: Customer,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test that creating a customer with duplicate NIT fails."""
        response = client.post(
            f"{self.API_PREFIX}/customers/",
            json={
                "name": "Duplicate Corp",
                "nit": test_customer.nit,
                "email": "duplicate@corp.com",
            },
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_create_customer_invalid_data(
        self,
        client: TestClient,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test that invalid customer data returns validation error."""
        response = client.post(
            f"{self.API_PREFIX}/customers/",
            json={
                "name": "",  # Empty name
                "nit": "invalid",
            },
        )

        assert response.status_code == 422

    def test_list_customers_unauthorized(self, client: TestClient):
        """Test that listing customers without auth fails."""
        response = client.get(f"{self.API_PREFIX}/customers/")

        assert response.status_code == 403

    def test_list_customers_success(
        self,
        client: TestClient,
        test_customer: Customer,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test listing customers with valid authentication."""
        response = client.get(f"{self.API_PREFIX}/customers/")

        assert response.status_code == 200
        customers = response.json()
        assert isinstance(customers, list)
        assert len(customers) >= 1

        # Verify customer structure
        first_customer = customers[0]
        assert "id" in first_customer
        assert "name" in first_customer
        assert "nit" in first_customer
        assert "email" in first_customer
        assert "created_at" in first_customer

    def test_get_customer_by_id_success(
        self,
        client: TestClient,
        test_customer: Customer,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test getting a specific customer by ID."""
        response = client.get(
            f"{self.API_PREFIX}/customers/{test_customer.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_customer.id
        assert data["name"] == test_customer.name
        assert data["nit"] == test_customer.nit

    def test_get_customer_by_id_not_found(
        self,
        client: TestClient,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test getting a non-existent customer returns 404."""
        response = client.get(f"{self.API_PREFIX}/customers/99999")

        assert response.status_code == 404

    def test_update_customer_success(
        self,
        client: TestClient,
        test_customer: Customer,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test updating a customer."""
        response = client.put(
            f"{self.API_PREFIX}/customers/{test_customer.id}",
            json={
                "name": "Updated Corp",
                "email": "updated@corp.com",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Corp"
        assert data["email"] == "updated@corp.com"
        assert data["nit"] == test_customer.nit  # Unchanged

    def test_delete_customer_success(
        self,
        client: TestClient,
        test_customer: Customer,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test deleting a customer."""
        response = client.delete(
            f"{self.API_PREFIX}/customers/{test_customer.id}"
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"{self.API_PREFIX}/customers/{test_customer.id}"
        )
        assert get_response.status_code == 404
```

#### Example: Testing Account Routes

```python
"""Integration tests for account routes."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.domain.entities.account import Account
from app.domain.entities.user import User


@pytest.mark.integration
class TestAccountRoutes:
    """Integration tests for /accounts endpoints."""

    def __init__(self) -> None:
        self.API_PREFIX = "/api/v1"

    @pytest.fixture
    def test_account(self, session: Session, test_user: User) -> Account:
        """Create a test account in the database."""
        account = Account(
            account_number="1001",
            name="Cash",
            type="asset",
            description="Cash account",
            created_by=test_user.email,
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        return account

    def test_create_account_success(
        self,
        client: TestClient,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test creating an account with valid authentication."""
        response = client.post(
            f"{self.API_PREFIX}/accounts/",
            json={
                "account_number": "2001",
                "name": "Bank Account",
                "type": "asset",
                "description": "Main bank account",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["account_number"] == "2001"
        assert data["name"] == "Bank Account"
        assert data["type"] == "asset"
        assert "id" in data

    def test_create_account_duplicate_number(
        self,
        client: TestClient,
        test_account: Account,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test that creating an account with duplicate number fails."""
        response = client.post(
            f"{self.API_PREFIX}/accounts/",
            json={
                "account_number": test_account.account_number,
                "name": "Duplicate Account",
                "type": "asset",
            },
        )

        assert response.status_code == 409

    def test_list_accounts_success(
        self,
        client: TestClient,
        test_account: Account,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test listing all accounts."""
        response = client.get(f"{self.API_PREFIX}/accounts/")

        assert response.status_code == 200
        accounts = response.json()
        assert isinstance(accounts, list)
        assert len(accounts) >= 1

        # Verify account structure
        first_account = accounts[0]
        assert "id" in first_account
        assert "account_number" in first_account
        assert "name" in first_account
        assert "type" in first_account
```

#### Example: Testing Category Routes (Simple CRUD)

```python
"""Integration tests for category routes."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.domain.entities.category import Category


@pytest.mark.integration
class TestCategoryRoutes:
    """Integration tests for /categories endpoints."""

    def __init__(self) -> None:
        self.API_PREFIX = "/api/v1"

    @pytest.fixture
    def test_category(self, session: Session) -> Category:
        """Create a test category in the database."""
        category = Category(name="Electronics", created_by="system")
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    def test_create_category_unauthorized(self, client: TestClient):
        """Test that creating a category without auth fails."""
        response = client.post(
            f"{self.API_PREFIX}/categories/",
            json={"name": "Books"},
        )

        assert response.status_code == 403

    def test_create_category_success(
        self,
        client: TestClient,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test creating a category with valid authentication."""
        response = client.post(
            f"{self.API_PREFIX}/categories/",
            json={"name": "Sports"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Sports"
        assert "id" in data
        assert "created_at" in data

    def test_create_category_duplicate_name(
        self,
        client: TestClient,
        test_category: Category,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test that creating a category with duplicate name fails."""
        response = client.post(
            f"{self.API_PREFIX}/categories/",
            json={"name": test_category.name},
        )

        assert response.status_code == 409

    def test_create_category_empty_name(
        self,
        client: TestClient,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test that empty category name fails validation."""
        response = client.post(
            f"{self.API_PREFIX}/categories/",
            json={"name": ""},
        )

        assert response.status_code == 422

    def test_list_categories_success(
        self,
        client: TestClient,
        test_category: Category,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test listing all categories."""
        response = client.get(f"{self.API_PREFIX}/categories/")

        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) >= 1

        # Verify structure
        first_category = categories[0]
        assert "id" in first_category
        assert "name" in first_category
        assert "created_at" in first_category

    def test_get_category_by_id_success(
        self,
        client: TestClient,
        test_category: Category,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test getting a specific category by ID."""
        response = client.get(
            f"{self.API_PREFIX}/categories/{test_category.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == test_category.name

    def test_get_category_by_id_not_found(
        self,
        client: TestClient,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test getting a non-existent category returns 404."""
        response = client.get(f"{self.API_PREFIX}/categories/99999")

        assert response.status_code == 404

    def test_update_category_success(
        self,
        client: TestClient,
        test_category: Category,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test updating a category name."""
        response = client.put(
            f"{self.API_PREFIX}/categories/{test_category.id}",
            json={"name": "Updated Electronics"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Electronics"
        assert data["id"] == test_category.id

    def test_delete_category_success(
        self,
        client: TestClient,
        test_category: Category,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test deleting a category."""
        response = client.delete(
            f"{self.API_PREFIX}/categories/{test_category.id}"
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"{self.API_PREFIX}/categories/{test_category.id}"
        )
        assert get_response.status_code == 404
```

#### Example: Testing Product Routes with Filters

```python
"""Integration tests for product routes."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.domain.entities.product import Product
from app.domain.entities.category import Category
from app.domain.entities.user import User


@pytest.mark.integration
class TestProductRoutes:
    """Integration tests for /products endpoints."""

    def __init__(self) -> None:
        self.API_PREFIX = "/api/v1"

    @pytest.fixture
    def test_category(self, session: Session) -> Category:
        """Create a test category."""
        category = Category(name="Electronics", created_by="system")
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    @pytest.fixture
    def test_product(
        self, session: Session, test_user: User, test_category: Category
    ) -> Product:
        """Create a test product in the database."""
        product = Product(
            name="Test Laptop",
            description="A test laptop",
            price=999.99,
            stock=10,
            category_id=test_category.id,
            created_by=test_user.email,
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        return product

    def test_create_product_unauthorized(self, client: TestClient):
        """Test that creating a product without auth fails."""
        response = client.post(
            f"{self.API_PREFIX}/products/",
            json={
                "name": "Unauthorized Product",
                "price": 99.99,
                "stock": 5,
            },
        )

        assert response.status_code == 403

    def test_create_product_success(
        self,
        client: TestClient,
        test_category: Category,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test creating a product with valid authentication."""
        response = client.post(
            f"{self.API_PREFIX}/products/",
            json={
                "name": "Gaming Mouse",
                "description": "RGB gaming mouse",
                "price": 59.99,
                "stock": 25,
                "category_id": test_category.id,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Gaming Mouse"
        assert data["price"] == 59.99
        assert data["stock"] == 25
        assert "id" in data

    def test_create_product_without_optional_fields(
        self,
        client: TestClient,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test creating a product without optional fields."""
        response = client.post(
            f"{self.API_PREFIX}/products/",
            json={
                "name": "Simple Product",
                "price": 19.99,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Simple Product"
        assert data["price"] == 19.99
        assert data["stock"] == 0  # Default value
        assert data["description"] is None

    def test_create_product_invalid_price(
        self,
        client: TestClient,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test that negative price fails validation."""
        response = client.post(
            f"{self.API_PREFIX}/products/",
            json={
                "name": "Invalid Product",
                "price": -10.00,
                "stock": 5,
            },
        )

        assert response.status_code == 422

    def test_list_products_success(
        self,
        client: TestClient,
        test_product: Product,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test listing all products."""
        response = client.get(f"{self.API_PREFIX}/products/")

        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) >= 1

        # Verify structure
        first_product = products[0]
        assert "id" in first_product
        assert "name" in first_product
        assert "price" in first_product
        assert "stock" in first_product

    def test_list_products_filter_by_category(
        self,
        client: TestClient,
        test_product: Product,
        test_category: Category,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test filtering products by category."""
        response = client.get(
            f"{self.API_PREFIX}/products/",
            params={"category_id": test_category.id},
        )

        assert response.status_code == 200
        products = response.json()
        assert len(products) >= 1
        for product in products:
            assert product["category_id"] == test_category.id

    def test_list_products_filter_in_stock(
        self,
        client: TestClient,
        test_product: Product,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test filtering products that are in stock."""
        response = client.get(
            f"{self.API_PREFIX}/products/",
            params={"in_stock": True},
        )

        assert response.status_code == 200
        products = response.json()
        for product in products:
            assert product["stock"] > 0

    def test_search_products_by_name(
        self,
        client: TestClient,
        test_product: Product,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test searching products by name."""
        response = client.get(
            f"{self.API_PREFIX}/products/search",
            params={"query": "Laptop"},
        )

        assert response.status_code == 200
        products = response.json()
        assert len(products) >= 1
        assert "Laptop" in products[0]["name"]

    def test_get_product_by_id_success(
        self,
        client: TestClient,
        test_product: Product,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test getting a specific product by ID."""
        response = client.get(
            f"{self.API_PREFIX}/products/{test_product.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == test_product.name
        assert data["price"] == test_product.price

    def test_update_product_success(
        self,
        client: TestClient,
        test_product: Product,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test updating a product."""
        response = client.put(
            f"{self.API_PREFIX}/products/{test_product.id}",
            json={
                "name": "Updated Laptop",
                "price": 1199.99,
                "stock": 15,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Laptop"
        assert data["price"] == 1199.99
        assert data["stock"] == 15

    def test_update_product_partial(
        self,
        client: TestClient,
        test_product: Product,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test partial update of a product."""
        original_name = test_product.name
        response = client.patch(
            f"{self.API_PREFIX}/products/{test_product.id}",
            json={"stock": 20},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == original_name  # Unchanged
        assert data["stock"] == 20  # Changed

    def test_delete_product_success(
        self,
        client: TestClient,
        test_product: Product,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test deleting a product."""
        response = client.delete(
            f"{self.API_PREFIX}/products/{test_product.id}"
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"{self.API_PREFIX}/products/{test_product.id}"
        )
        assert get_response.status_code == 404

    def test_bulk_create_products(
        self,
        client: TestClient,
        test_category: Category,
        mock_verify_token,
        mock_get_current_user,
    ):
        """Test creating multiple products at once."""
        products_data = [
            {"name": "Product 1", "price": 10.00, "stock": 5},
            {"name": "Product 2", "price": 20.00, "stock": 10},
            {"name": "Product 3", "price": 30.00, "stock": 15},
        ]

        response = client.post(
            f"{self.API_PREFIX}/products/bulk",
            json=products_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data) == 3
        assert all("id" in product for product in data)
```


## Testing Patterns

### Arrange-Act-Assert (AAA) Pattern

Always structure tests using the AAA pattern:

```python
def test_example(self):
    """Test description."""
    # Arrange - Set up test data and expectations
    customer_data = CustomerCreate(name="Test", nit="12345678-9")

    # Act - Execute the functionality being tested
    result = service.create_customer(customer_data)

    # Assert - Verify the results
    assert result.name == "Test"
    assert result.nit == "12345678-9"
```

### Mocking Dependencies

Use `unittest.mock` for mocking external dependencies:

```python
from unittest.mock import Mock, patch, MagicMock

# Mock a repository method
mock_repository = Mock()
mock_repository.get_by_id.return_value = expected_value

# Patch a dependency
with patch('app.services.some_service.SomeDependency') as mock_dep:
    mock_dep.return_value = mock_value
    # Test code here
```

### Testing Exceptions

Test both success and error cases:

```python
def test_error_case(self):
    """Test that error is raised for invalid input."""
    with pytest.raises(HTTPException) as exc_info:
        service.do_something_invalid()

    assert exc_info.value.status_code == 400
    assert "error message" in str(exc_info.value.detail)
```

### Parametrized Tests

Use `@pytest.mark.parametrize` for testing multiple scenarios:

```python
@pytest.mark.parametrize(
    "account_type,expected_category",
    [
        ("asset", "current_assets"),
        ("liability", "current_liabilities"),
        ("equity", "shareholder_equity"),
    ],
)
def test_categorize_account(account_type, expected_category):
    """Test account categorization for different types."""
    result = categorize_account(account_type)
    assert result == expected_category
```

## Testing Checklist

When adding a new entity (e.g., Customer, Account), ensure you have:

### Unit Tests

- [ ] **Builder Tests** (if applicable)
  - [ ] Test creating entity with all fields
  - [ ] Test creating entity with required fields only
  - [ ] Test missing required fields raise ValueError
  - [ ] Test field validation (email format, ranges, etc.)
  - [ ] Test convenience methods

- [ ] **Service Tests**
  - [ ] Test create operation (success case)
  - [ ] Test create operation (duplicate/conflict case)
  - [ ] Test list/get all operation
  - [ ] Test get by ID operation (found)
  - [ ] Test get by ID operation (not found)
  - [ ] Test update operation
  - [ ] Test delete operation
  - [ ] Test business logic validation

- [ ] **Repository Tests**
  - [ ] Test create operation
  - [ ] Test find by ID
  - [ ] Test find by unique field
  - [ ] Test get all
  - [ ] Test update
  - [ ] Test delete
  - [ ] Test query filters

### Integration Tests

- [ ] **API Route Tests**
  - [ ] Test unauthorized access (401/403)
  - [ ] Test authorized access (200/201)
  - [ ] Test CREATE endpoint
    - [ ] Success case
    - [ ] Validation errors (422)
    - [ ] Duplicate/conflict (409)
  - [ ] Test LIST endpoint
  - [ ] Test GET by ID endpoint
    - [ ] Found case
    - [ ] Not found case (404)
  - [ ] Test UPDATE endpoint
  - [ ] Test DELETE endpoint
  - [ ] Test response structure matches schema

### Coverage Goals

- Aim for **80%+ code coverage** overall
- Critical business logic should have **100% coverage**
- All error paths should be tested

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
   - Good: `test_create_customer_with_duplicate_nit_raises_conflict`
   - Bad: `test_customer_error`

2. **One Assertion Per Concept**: Each test should verify one specific behavior
   - Multiple assertions are OK if testing the same concept

3. **Independent Tests**: Tests should not depend on each other
   - Use fixtures for shared setup
   - Clean up after tests

4. **Fast Tests**: Unit tests should run in milliseconds
   - Use mocks to avoid slow operations
   - Integration tests can be slower but should still be reasonably fast

5. **Clear Failure Messages**: Use descriptive assertions
   ```python
   # Good
   assert result.status == "active", f"Expected active status, got {result.status}"

   # OK
   assert result.status == "active"
   ```

6. **Test Data**: Use realistic but minimal test data
   - Avoid production data in tests
   - Use factories or builders for complex objects

7. **DRY Principle**: Extract common test setup into fixtures
   ```python
   @pytest.fixture
   def sample_customer(self):
       return Customer(name="Test Corp", nit="12345678-9")
   ```

## Running Tests in CI/CD

Tests are automatically run in CI/CD pipelines. Ensure:

- All tests pass before merging PRs
- Coverage reports are generated
- Integration tests use isolated test databases

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    uv run pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running tests from project root
   ```bash
   cd /path/to/biz-ops-backend
   uv run pytest
   ```

2. **Database Errors**: Check that test fixtures are properly setting up in-memory database
   ```python
   # In conftest.py
   SQLModel.metadata.create_all(engine)
   ```

3. **Authentication Errors**: Ensure mock fixtures are being used
   ```python
   def test_something(
       client: TestClient,
       mock_verify_token,  # Don't forget this
       mock_get_current_user,  # And this
   ):
       # Test code
   ```

4. **Fixture Not Found**: Check fixture scope and availability
   ```python
   @pytest.fixture(scope="function")  # or "session", "module"
   def my_fixture():
       pass
   ```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Builder Pattern Guide](https://refactoring.guru/design-patterns/builder/python/example)
- [SQLModel Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/)

## Test Database Configuration

### How Test Database Works

Tests use an in-memory SQLite database that is automatically configured in `tests/conftest.py`:

```python
# Environment variables are set BEFORE app import
os.environ["DATABASE_URI"] = "sqlite:///:memory:"

# Engine fixture uses the app's engine (configured with test DATABASE_URI)
@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    from app.infrastructure import database as db_module
    SQLModel.metadata.create_all(db_module.engine)
    return db_module.engine
```

**Key points:**
1. Environment variables MUST be set before importing the app
2. The app's engine is automatically configured with SQLite when tests run
3. Tables are created automatically via `SQLModel.metadata.create_all()`
4. All fixtures share the same engine for data consistency

### Database Fixtures

**`engine`** - Session-scoped SQLite engine
- Created once per test session
- Shared across all tests for performance
- Tables created automatically

**`session`** - Function-scoped database session
- New session for each test
- Automatically rolls back after test

**`client`** - Test client without authentication
- Uses test database
- For testing unauthorized access (403 errors)

**`authenticated_client`** - Test client with authentication mocks
- Uses test database
- Authentication dependencies overridden
- For testing authorized endpoints

**`clean_database`** - Auto-cleanup fixture
- Runs after each test
- Deletes all data for test isolation
- Ensures tests don't affect each other

### Creating Test Data

#### Option 1: Using Fixtures (Recommended)

```python
@pytest.fixture
def test_customer(session: Session) -> Customer:
    """Create a test customer in the database."""
    customer = Customer(
        name="Test Corp",
        nit="12345678-9",
        created_by="test@example.com",
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

def test_something(test_customer: Customer):
    assert test_customer.id is not None
```

#### Option 2: Creating Data in Test

```python
def test_something(engine):
    """Test with inline data creation."""
    from sqlmodel import Session

    with Session(engine) as session:
        customer = Customer(name="Test", nit="12345678-9", created_by="test")
        session.add(customer)
        session.commit()

    # Use customer in test
    ...
```

#### Option 3: Via API (Integration Tests)

```python
def test_something(authenticated_client: TestClient):
    """Test using API to create data."""
    # Create via API
    response = authenticated_client.post(
        "/api/v1/customers/",
        json={"name": "Test Corp", "nit": "12345678-9"},
    )
    assert response.status_code == 201

    customer_id = response.json()["id"]
    # Use customer_id in further tests
    ...
```

### Handling Different Database Types

The app automatically detects the database type and configures the engine appropriately:

```python
# In app/infrastructure/database.py
if settings.DATABASE_URI.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        settings.DATABASE_URI,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        settings.DATABASE_URI,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
```

This ensures:
- ✅ Tests use SQLite (fast, no pooling needed)
- ✅ Production uses PostgreSQL (with connection pooling)
- ✅ No code changes needed between environments

### CI/CD Configuration

GitHub Actions workflow (`.github/workflows/test.yml`) ensures:

1. **Environment variables are set** before running tests
2. **SQLite is used** (no PostgreSQL setup needed)
3. **All dependencies installed** via `uv`
4. **Coverage reports generated** and uploaded

```yaml
# Key workflow steps:
- Set environment: DATABASE_URI=sqlite:///:memory:
- Install dependencies: uv sync && uv pip install -r requirements.txt
- Run tests: uv run pytest tests/ --cov=app
```

### Troubleshooting Database Issues

**Problem:** Tests fail with "relation does not exist" or "table not found"
```
Solution: Ensure conftest.py sets DATABASE_URI before importing app
```

**Problem:** Tests try to connect to PostgreSQL instead of SQLite
```
Solution: Check that environment variable is set at the TOP of conftest.py
```

**Problem:** Data from one test appears in another test
```
Solution: clean_database fixture should run after each test
```

**Problem:** Fixture can't find test data
```
Solution: Ensure fixtures use the same engine (check engine fixture scope)
```

## Summary

This guide provides a comprehensive framework for testing the biz-ops-backend application. Follow these patterns and checklists when adding new features to ensure high-quality, maintainable code.

### Quick Checklist for New Tests

- [ ] Uses `pytest` fixtures from `conftest.py`
- [ ] Tests are isolated (don't depend on each other)
- [ ] Uses SQLite in-memory database (via fixtures)
- [ ] Follows AAA pattern (Arrange-Act-Assert)
- [ ] Has descriptive test names
- [ ] Covers both success and error cases
- [ ] Achieves >80% code coverage
- [ ] Passes in both local and CI environments

For questions or improvements to this guide, please create an issue or PR in the repository.
