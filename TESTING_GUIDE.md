# Testing Guide

This guide explains the testing strategy and how to write and run tests for the Business Operations API.

## Testing Philosophy

Our testing strategy follows the testing pyramid:

1. **Unit Tests** (70%): Test individual components in isolation
2. **Integration Tests** (20%): Test component interactions
3. **End-to-End Tests** (10%): Test complete user workflows

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── unit/                 # Unit tests (isolated components)
│   ├── test_user_repository.py
│   ├── test_user_service.py
│   └── test_vendor_service.py
└── integration/          # Integration tests (API endpoints)
    ├── test_user_routes.py
    └── test_vendor_routes.py
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

View the HTML coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Tests marked as slow
pytest -m slow

# Exclude slow tests
pytest -m "not slow"
```

### Run Specific Tests

```bash
# Specific file
pytest tests/unit/test_user_service.py

# Specific class
pytest tests/unit/test_user_service.py::TestUserService

# Specific test
pytest tests/unit/test_user_service.py::TestUserService::test_register_user

# Tests matching a pattern
pytest -k "user"
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Verbose mode
pytest -v

# Very verbose (show all test details)
pytest -vv
```

## Writing Tests

### Unit Tests

Unit tests test individual components in isolation using mocks.

**Example: Testing a Service**

```python
from unittest.mock import Mock
from app.services.user_service import UserService
from app.domain.entities.user import User, UserCreate

def test_register_user():
    # Arrange - Set up test data and mocks
    mock_repo = Mock()
    mock_user = User(
        auth_id="auth0|123",
        email="test@example.com",
        created_by="system"
    )
    mock_repo.create_user.return_value = mock_user
    
    service = UserService(mock_repo)
    user_data = UserCreate(
        auth_id="auth0|123",
        email="test@example.com"
    )
    
    # Act - Execute the function
    result = service.register_user(user_data)
    
    # Assert - Verify the results
    assert result.auth_id == "auth0|123"
    assert result.email == "test@example.com"
    mock_repo.create_user.assert_called_once()
```

### Integration Tests

Integration tests test API endpoints with a real database (SQLite in-memory).

**Example: Testing an Endpoint**

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
def test_read_users(client: TestClient, test_user, mock_verify_token, mock_get_current_user):
    # Act
    response = client.get("/users/")
    
    # Assert
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1
```

## Fixtures

Fixtures provide reusable test data and setup. They are defined in `conftest.py`.

### Available Fixtures

#### `engine`
Provides an in-memory SQLite database engine.

```python
def test_something(engine):
    # Use engine for database operations
    pass
```

#### `session`
Provides a database session for tests.

```python
def test_create_user(session):
    user = User(auth_id="test", email="test@example.com", created_by="test")
    session.add(user)
    session.commit()
```

#### `client`
Provides a TestClient for API testing.

```python
def test_endpoint(client):
    response = client.get("/users/")
    assert response.status_code == 200
```

#### `test_user`
Creates a test user in the database.

```python
def test_with_user(test_user):
    assert test_user.email == "test@example.com"
```

#### `mock_verify_token`
Mocks Auth0 token verification.

```python
def test_authenticated_endpoint(client, mock_verify_token):
    response = client.get("/users/")
    # Token verification is mocked
```

### Creating Custom Fixtures

Add fixtures to `conftest.py`:

```python
@pytest.fixture(name="test_vendor")
def test_vendor_fixture(session: Session) -> Vendor:
    """Create a test vendor in the database."""
    vendor = Vendor(
        name="Test Vendor",
        email="vendor@example.com",
        created_by="test"
    )
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor
```

## Test Markers

Use markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_unit_something():
    pass

@pytest.mark.integration
def test_integration_something():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

Run tests by marker:
```bash
pytest -m unit
pytest -m "unit or integration"
pytest -m "not slow"
```

## Mocking

### Mocking External Services

```python
from unittest.mock import patch, Mock

@patch('app.dependencies.verify_token')
def test_with_mocked_auth(mock_verify):
    mock_verify.return_value = {"sub": "test_user"}
    # Test code here
```

### Mocking Database

```python
from unittest.mock import Mock

def test_service_with_mock_repo():
    mock_repo = Mock()
    mock_repo.get_user_by_id.return_value = None
    
    service = UserService(mock_repo)
    result = service.get_user("123")
    
    assert result is None
    mock_repo.get_user_by_id.assert_called_with("123")
```

## Test Database Strategy

### Unit Tests
- Use SQLite in-memory database
- Fast, isolated tests
- Reset between tests

### Integration Tests
- Option 1: SQLite in-memory (current)
- Option 2: PostgreSQL with Docker

For PostgreSQL integration tests:

```bash
# Start test database
docker-compose -f docker-compose.test.yml up -d test-db

# Run tests
pytest tests/integration/

# Stop database
docker-compose -f docker-compose.test.yml down
```

## Coverage Goals

- **Overall**: ≥ 80%
- **Critical paths**: ≥ 90%
- **Services**: ≥ 85%
- **Repositories**: ≥ 80%
- **Routes**: ≥ 75%

Check coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

## Best Practices

### 1. Test Naming

```python
# Good
def test_create_user_with_valid_data():
    pass

def test_create_user_with_duplicate_email_raises_error():
    pass

# Bad
def test_user():
    pass

def test1():
    pass
```

### 2. Arrange-Act-Assert Pattern

```python
def test_something():
    # Arrange - Set up test data
    user_data = UserCreate(auth_id="123", email="test@example.com")
    
    # Act - Execute the function
    result = service.create_user(user_data)
    
    # Assert - Verify the outcome
    assert result.auth_id == "123"
```

### 3. One Assert Per Test (when possible)

```python
# Good
def test_user_email():
    user = create_user()
    assert user.email == "test@example.com"

def test_user_auth_id():
    user = create_user()
    assert user.auth_id == "auth0|123"

# Acceptable for related assertions
def test_user_creation():
    user = create_user()
    assert user.email == "test@example.com"
    assert user.auth_id is not None
    assert user.created_at is not None
```

### 4. Use Descriptive Assertions

```python
# Good
assert len(users) == 2, f"Expected 2 users, got {len(users)}"

# Bad
assert len(users) == 2
```

### 5. Test Edge Cases

```python
def test_with_empty_string():
    pass

def test_with_none_value():
    pass

def test_with_very_long_input():
    pass

def test_with_special_characters():
    pass
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main/develop branches

CI runs:
1. Linting (ruff)
2. Formatting check (black)
3. Type checking (mypy)
4. Unit tests
5. Integration tests
6. Coverage report

See `.github/workflows/ci.yml` for details.

## Troubleshooting

### Tests Failing Locally But Passing in CI

- Check Python version matches CI
- Ensure dependencies are up to date
- Check for environment-specific issues

### Database Errors in Tests

```python
# Make sure to use the session fixture
def test_something(session):  # ✅ Correct
    pass

def test_something():  # ❌ No session
    pass
```

### Import Errors

```bash
# Run tests from project root
cd /path/to/biz-ops-backend
pytest

# NOT from tests directory
cd tests  # ❌ Wrong
pytest
```

### Fixture Not Found

Check that fixture is defined in:
- `conftest.py` in the same directory
- `conftest.py` in a parent directory
- Imported from pytest plugins

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLModel Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)



