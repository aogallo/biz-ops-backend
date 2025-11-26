# Testing Philosophy

## Core Principle

**Unit Testing = Business Logic**
**Integration Testing = Endpoints**

---

## Unit Tests (`tests/unit/`)

### Purpose
Test **business logic** in complete isolation without external dependencies.

### What to Test
- ✅ **Services** - Business logic with mocked repositories
- ✅ **Builders** - Object construction patterns
- ✅ **Repositories** - Data access logic with mocked database
- ✅ **Entities** - Domain models and validation
- ✅ **Utilities** - Helper functions and transformations

### Key Characteristics
- 🔒 **No database** - All database calls are mocked
- 🔒 **No external APIs** - All external services are mocked
- ⚡ **Lightning fast** - Tests run in milliseconds
- 🎯 **Focused** - Test one component at a time
- 🧪 **Predictable** - Same input = same output, always

### Example: Testing a Service

```python
"""Unit test - ProductService business logic."""
from unittest.mock import Mock
import pytest
from fastapi import HTTPException

from app.services.product_service import ProductService
from app.domain.entities.product import Product, ProductCreate

class TestProductService:
    @pytest.fixture
    def mock_repository(self):
        """Mock the database layer."""
        return Mock()

    @pytest.fixture
    def service(self, mock_user, mock_repository, monkeypatch):
        """Inject mocked repository into service."""
        service = ProductService(current_user=mock_user)
        monkeypatch.setattr(service, "repository", mock_repository)
        return service

    def test_create_product_success(self, service, mock_repository):
        """Test business logic: product creation succeeds when name is unique."""
        # Arrange - Setup mocks
        product_data = ProductCreate(name="Laptop", price=999.99, stock=10)
        mock_repository.get_by_name.return_value = None  # No duplicate
        mock_repository.create.return_value = Product(id=1, name="Laptop", ...)

        # Act - Execute business logic
        result = service.create_product(product_request=product_data)

        # Assert - Verify behavior
        assert result.id == 1
        mock_repository.get_by_name.assert_called_once_with(name="Laptop")
        mock_repository.create.assert_called_once()

    def test_create_product_duplicate_name(self, service, mock_repository):
        """Test business logic: 409 error when product name already exists."""
        # Arrange
        product_data = ProductCreate(name="Existing", price=99.99, stock=5)
        mock_repository.get_by_name.return_value = Product(id=1, name="Existing", ...)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_product(product_request=product_data)

        assert exc_info.value.status_code == 409
        mock_repository.create.assert_not_called()  # Should not create
```

**Why this is a good unit test:**
1. ✅ Tests business logic (duplicate name check)
2. ✅ No database access (repository is mocked)
3. ✅ Fast (runs in < 1ms)
4. ✅ Predictable (no external dependencies)
5. ✅ Verifies service behavior, not database operations

---

## Integration Tests (`tests/integration/`)

### Purpose
Test **endpoints** end-to-end with real database interactions.

### What to Test
- ✅ **API Routes** - Full HTTP request → response cycle
- ✅ **Authentication** - Token validation and authorization
- ✅ **Request Validation** - Schema validation and error handling
- ✅ **Response Formatting** - JSON serialization and status codes
- ✅ **Database Integration** - Real CRUD operations
- ✅ **Error Handling** - 4xx and 5xx error responses

### Key Characteristics
- 🔌 **Real database** - Uses SQLite in-memory (fast, isolated)
- 🌐 **Full HTTP** - TestClient makes real HTTP requests
- 🔐 **Mocked auth** - Authentication is mocked for convenience
- 🧹 **Clean slate** - Database cleared between tests
- 📊 **End-to-end** - Tests the complete stack

### Example: Testing an Endpoint

```python
"""Integration test - Product API endpoints."""
from fastapi.testclient import TestClient

class TestProductRoutes:
    def test_create_product_success(self, authenticated_client: TestClient):
        """Test endpoint: POST /products returns 201 with valid data."""
        # Arrange
        product_data = {
            "name": "Test Laptop",
            "description": "A laptop",
            "price": 999.99,
            "stock": 10,
        }

        # Act - Make real HTTP request
        response = authenticated_client.post(
            "/api/v1/products",
            json=product_data,
        )

        # Assert - Check HTTP response
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Laptop"
        assert data["id"] is not None  # Saved to database

    def test_create_product_duplicate_name(self, authenticated_client: TestClient):
        """Test endpoint: POST /products returns 409 for duplicate name."""
        # Arrange - Create first product
        product_data = {"name": "Duplicate", "price": 99.99, "stock": 5}
        authenticated_client.post("/api/v1/products", json=product_data)

        # Act - Try to create duplicate
        response = authenticated_client.post("/api/v1/products", json=product_data)

        # Assert - Check error response
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_create_product_unauthenticated(self, client: TestClient):
        """Test endpoint: POST /products returns 403 without auth."""
        # Act - Make request without authentication
        response = client.post(
            "/api/v1/products",
            json={"name": "Test", "price": 99.99, "stock": 5},
        )

        # Assert - Check authentication required
        assert response.status_code == 403
```

**Why this is a good integration test:**
1. ✅ Tests the endpoint, not the service
2. ✅ Uses real database (data is actually saved)
3. ✅ Tests HTTP layer (status codes, JSON formatting)
4. ✅ Tests authentication flow
5. ✅ Tests end-to-end integration

---

## Comparison Table

| Aspect | Unit Tests | Integration Tests |
|--------|-----------|-------------------|
| **Location** | `tests/unit/` | `tests/integration/` |
| **Tests** | Business logic | Endpoints |
| **Database** | ❌ Mocked | ✅ Real (SQLite) |
| **HTTP** | ❌ No HTTP | ✅ Full HTTP cycle |
| **Speed** | ⚡ < 1ms | 🐢 ~50-200ms |
| **Dependencies** | 🔒 All mocked | 🔌 Real (except auth) |
| **Focus** | Logic correctness | Integration correctness |
| **Example** | Service methods | API routes |

---

## When to Write Each Type

### Write Unit Tests For:
```python
✅ Service.create_customer()     # Business logic
✅ Builder.build()               # Object construction
✅ Repository.find_by_email()    # Data access logic
✅ validate_nit()                # Helper functions
✅ calculate_total()             # Calculations
```

### Write Integration Tests For:
```python
✅ POST /api/v1/customers        # Create endpoint
✅ GET /api/v1/customers/:id     # Read endpoint
✅ PUT /api/v1/customers/:id     # Update endpoint
✅ DELETE /api/v1/customers/:id  # Delete endpoint
✅ POST /api/v1/customers (401)  # Auth error
✅ POST /api/v1/customers (422)  # Validation error
```

---

## Benefits of This Approach

### Fast Feedback Loop
- Unit tests run in **milliseconds** → Instant feedback during development
- Integration tests run in **seconds** → Quick validation of endpoints
- Can run unit tests on every save in your IDE

### Clear Test Boundaries
- **Unit tests fail** → Bug in business logic (service, builder, etc.)
- **Integration tests fail** → Bug in integration (routing, auth, serialization)
- Easy to identify where the problem is

### Better Coverage
- **Unit tests** catch logic errors (edge cases, validations, calculations)
- **Integration tests** catch integration errors (wrong status code, bad JSON)
- Together they provide comprehensive coverage

### Maintainability
- Unit tests are **isolated** → Easy to understand and modify
- Integration tests are **realistic** → Catch real-world problems
- Clear separation makes tests easier to maintain

---

## Test Execution

```bash
# Run only unit tests (fast, for development)
uv run pytest tests/unit/ -v

# Run only integration tests (slower, for validation)
uv run pytest tests/integration/ -v

# Run all tests (complete validation)
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/test_product_service.py -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=term-missing
```

---

## Current Test Status

```
✅ 3 unit tests       (tests/unit/test_products.py)
✅ 3 integration tests (tests/integration/test_product_routes.py)
✅ 62% code coverage
✅ ProductService: 100% coverage
✅ All tests pass in < 1 second
```

---

## Quick Reference

**Before writing a test, ask:**

> "Am I testing **WHAT** it does (business logic) or **HOW** it's accessed (endpoint)?"

- **WHAT** → Unit test with mocks
- **HOW** → Integration test with real database

**Remember:**
- 🧠 **Unit** = Pure logic, no side effects
- 🔌 **Integration** = Full stack, real interactions

---

## Resources

- Full guide: `docs/TESTING_GUIDE.md`
- Test fixtures: `tests/conftest.py`
- Test plan: `fix-builder-pattern.plan.md`
- CI/CD workflow: `.github/workflows/test.yml`
