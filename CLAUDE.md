# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Business Operations Backend API built with FastAPI and PostgreSQL. This is an accounting/business operations system handling invoices, customers, products, journal entries, and financial reports.

**Key Technologies:**
- FastAPI 0.115+ (async Python web framework)
- SQLModel/SQLAlchemy (ORM)
- PostgreSQL (primary database)
- Auth0 (authentication with JWT)
- Python 3.12+
- uv (fast Python package installer)
- Ruff (fast Python linter and formatter)

## Essential Commands

### Development Workflow

```bash
# Activate virtual environment (always do this first)
source .venv/bin/activate

# Install/update dependencies (use uv, not pip!)
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_products.py

# Run specific test function
pytest tests/unit/test_products.py::TestProductService::test_create_product

# Run only unit or integration tests
pytest tests/unit/
pytest tests/integration/
```

### Code Quality

```bash
# Format code (Ruff format replaces Black - faster and compatible)
ruff format app/ tests/

# Check formatting without modifying files
ruff format --check app/

# Lint code (must pass before commits)
ruff check app/

# Auto-fix linting issues
ruff check app/ --fix

# Type checking
mypy app/

# Run all quality checks
ruff format --check app/ && ruff check app/ && mypy app/

# Pre-commit hooks (runs automatically on commit)
pre-commit run --all-files
```

**Important:** This project uses **Ruff format** instead of Black. Ruff is a modern, faster alternative that's fully compatible with Black's formatting style.

### Database

```bash
# Create database (PostgreSQL must be running)
createdb bizops_dev

# Check database connection
psql postgresql://postgres:123@localhost:5432/bizops_dev

# Tables are auto-created on application startup via SQLModel.metadata.create_all()
```

## Architecture

### Module Structure Pattern

The codebase uses a **modular domain-driven design**. Each business domain lives in `app/internal/{domain}/` with this structure:

```
app/internal/{domain}/
├── entity.py          # SQLModel database models (snake_case)
├── schema.py          # Pydantic API schemas (camelCase via Field serialization_alias)
├── repository.py      # Abstract repository interface
├── repository_impl.py # Concrete repository implementation
├── service.py         # Business logic layer
└── routes.py          # FastAPI route handlers
```

**Current domains:** account, category, company, customer, invoice, journal, product, report, user

### Layer Responsibilities

**1. Entity Layer** (`entity.py`)
- SQLModel classes for database tables
- Use snake_case field names (PostgreSQL convention)
- Pattern: `{Domain}Base`, `{Domain}Create`, `{Domain}` (table=True)
- Includes relationships between entities

**2. Schema Layer** (`schema.py`)
- Pydantic models for API requests/responses
- **Use explicit `Field(serialization_alias="...")` for camelCase conversion**
- All schemas inherit from `BaseModel` with explicit field aliases
- Frontend sends camelCase JSON → automatically converted to snake_case
- Pattern: `{Domain}Create`, `{Domain}Update`, `{Domain}Response`

**3. Repository Layer** (`repository.py` + `repository_impl.py`)
- Abstract base defines interface, implementation handles DB operations
- Uses SQLModel/SQLAlchemy queries
- Takes `Session` and `User` in constructor
- All creates/updates automatically set `created_by`/`updated_by` from `current_user.auth_id`

**4. Service Layer** (`service.py`)
- Business logic and validation
- Orchestrates repository calls
- Handles complex operations (e.g., invoice creation with journal entries)
- Raises domain exceptions from `app.core.exceptions`

**5. Routes Layer** (`routes.py`)
- FastAPI route definitions
- Uses dependency injection: `SessionDep`, `get_current_user`
- **Always set `response_model`** for automatic schema validation
- Routes registered in `app/main.py` with `/api/v1` prefix

### Critical Patterns

**CamelCase Conversion Flow:**
```python
# Frontend sends:    {"firstName": "John", "lastName": "Doe"}
# Schema receives:   first_name="John", last_name="Doe"
# Entity saves:      first_name="John", last_name="Doe"
# Database column:   first_name, last_name
# Response returns:  {"firstName": "John", "lastName": "Doe"}

# Schema definition using explicit serialization_alias:
from pydantic import BaseModel, ConfigDict, Field

class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    first_name: str = Field(serialization_alias="firstName")
    last_name: str = Field(serialization_alias="lastName")
```

**Complete Schema Example:**
```python
"""Product API schemas for requests and responses."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """Schema for creating a new product."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    description: str | None = None
    price: float
    stock: int = 0


class ProductResponse(BaseModel):
    """Schema for product response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    description: str | None
    price: float
    stock: int
    created_by: str = Field(serialization_alias="createdBy")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_by: str | None = Field(serialization_alias="updatedBy")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")
```

**Schema ↔ Entity Conversion:**
```python
# Schema → Entity (use model_dump())
from app.internal.product.schema import ProductCreate
from app.internal.product.entity import ProductCreate as ProductEntityCreate

schema_data = ProductCreate(name="Laptop", price=999.99)
entity_data = ProductEntityCreate(**schema_data.model_dump())

# Entity → Schema (from_attributes=True handles this)
from app.internal.product.schema import ProductResponse
product_entity = repository.get_by_id(1)
response = ProductResponse.model_validate(product_entity)
```

**Authentication Flow:**
```python
# Routes must use these dependencies for protected endpoints
from app.database import SessionDep
from app.dependencies import get_current_user
from app.internal.user.entity import User

@router.post("/resource")
async def create_resource(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    data: ResourceCreate,
):
    # current_user.auth_id is the Auth0 sub claim
    # current_user.permissions is list of Auth0 permissions
    ...
```

### Database Session Management

- **SessionDep**: Type alias for `Annotated[Session, Depends(get_session)]`
- Use in route parameters for automatic session injection
- Sessions auto-commit/rollback in dependency
- Connection pooling configured (pool_size=10, max_overflow=20)

### Exception Handling

Global exception handlers defined in `app/main.py`:
- `AppException` → 400 Bad Request
- `NotFoundError` → 404 Not Found
- `AuthenticationError` → 401 Unauthorized
- `AuthorizationError` → 403 Forbidden
- `RequestValidationError` → 422 Unprocessable Entity
- `SQLAlchemyError` → 500 Internal Server Error

Use these from `app.core.exceptions` in service layer.

## Test-Driven Development (TDD)

**CRITICAL REQUIREMENT:** This project follows Test-Driven Development practices. All new features and updates to existing features MUST follow TDD workflow.

### TDD Workflow

When implementing a new feature or updating an existing feature, follow this strict workflow:

1. **Write Tests First**
   - Write unit tests for the service layer before implementing the business logic
   - Write integration tests for the routes before implementing the endpoints
   - Tests should cover all expected behaviors, edge cases, and error conditions
   - Aim for 100% code coverage of new implementation

2. **Run Tests (They Should Fail)**
   - Execute the tests to verify they fail (red phase)
   - Failing tests confirm that tests are actually testing new functionality

3. **Implement Minimum Code**
   - Write the minimum amount of code needed to make the tests pass
   - Focus on making tests green, not on perfect implementation

4. **Run Tests Again (They Should Pass)**
   - Execute tests to verify they now pass (green phase)
   - All tests must pass before proceeding

5. **Refactor**
   - Improve code quality while keeping tests green
   - Apply design patterns, remove duplication, improve readability
   - Re-run tests after each refactoring step

6. **Verify Coverage**
   - Run coverage report: `pytest --cov=app --cov-report=term-missing`
   - Ensure 100% coverage of new/modified lines
   - Add tests for any uncovered lines

### Coverage Requirements

**MANDATORY:** Each new implementation or feature update must have:
- **100% unit test coverage** for all new lines in service layer
- **100% integration test coverage** for all new/modified API endpoints
- Tests for success cases, error cases, and edge cases
- Tests for validation logic and business rules

**Example TDD Flow:**
```bash
# 1. Create test file first
touch tests/unit/test_new_feature.py
touch tests/integration/test_new_feature_routes.py

# 2. Write failing tests
# Edit test files with expected behavior

# 3. Run tests (should fail)
pytest tests/unit/test_new_feature.py -v
# Expected: FAILED (tests fail because implementation doesn't exist)

# 4. Implement feature
# Edit service.py, routes.py, etc.

# 5. Run tests again (should pass)
pytest tests/unit/test_new_feature.py -v
# Expected: PASSED

# 6. Check coverage
pytest tests/unit/test_new_feature.py --cov=app.internal.feature.service --cov-report=term-missing
# Expected: 100% coverage

# 7. Run all tests to ensure no regressions
pytest
```

### Testing Standards

**Unit Tests (`tests/unit/`):**
- Test business logic in isolation
- Mock external dependencies (database, repositories, external services)
- Focus on service layer methods
- Test all code paths (if/else, try/except, loops)
- Test validation logic and error handling
- Naming: `test_{method_name}_{scenario}` (e.g., `test_create_product_success`, `test_create_product_duplicate_name`)

**Integration Tests (`tests/integration/`):**
- Test API endpoints end-to-end
- Use test database (SQLite in-memory)
- Test HTTP status codes, response schemas, error responses
- Test authentication/authorization
- Test query parameters and filters
- Naming: `test_{endpoint}_{scenario}` (e.g., `test_create_company_success`, `test_list_companies_filtered_by_managed_status`)

**Before Committing:**
- ✅ All tests must pass: `pytest`
- ✅ Coverage must be 100% for new code: `pytest --cov=app --cov-report=term-missing`
- ✅ Pre-commit hooks must pass (includes ruff format, ruff check, mypy)

### Example: Adding a New Feature with TDD

**Scenario: Add filtering by status to products endpoint**

```python
# Step 1: Write unit test first (tests/unit/test_products.py)
def test_list_products_filtered_by_status_active(service, mock_repository):
    """Test listing products filtered by active status."""
    active_products = [
        Product(id=1, name="Active Product", status="active"),
    ]
    mock_repository.get_by_status.return_value = active_products

    result = service.list_products(status="active")

    assert len(result) == 1
    assert result[0].status == "active"
    mock_repository.get_by_status.assert_called_once_with("active")

# Step 2: Run test (it fails - method doesn't exist)
# $ pytest tests/unit/test_products.py::test_list_products_filtered_by_status_active
# FAILED - AttributeError: 'ProductService' has no attribute 'list_products'

# Step 3: Implement minimum code in service.py
def list_products(self, status: str | None = None):
    if status:
        return self.repository.get_by_status(status)
    return self.repository.get_all()

# Step 4: Run test again (it passes)
# $ pytest tests/unit/test_products.py::test_list_products_filtered_by_status_active
# PASSED

# Step 5: Add integration test
# tests/integration/test_product_routes.py
def test_list_products_filtered_by_status(authenticated_client, engine):
    # ... create test data ...
    response = authenticated_client.get("/api/v1/products?status=active")
    assert response.status_code == 200
    assert all(p["status"] == "active" for p in response.json()["products"])

# Step 6: Verify coverage
# $ pytest tests/unit/test_products.py --cov=app.internal.product.service --cov-report=term-missing
# Coverage: 100%
```

**NO EXCEPTIONS:** Do not commit code without tests. Do not implement features before writing tests.

## Adding New Features

**⚠️ IMPORTANT:** Before adding any new feature, review the [Test-Driven Development (TDD)](#test-driven-development-tdd) section above. All feature development MUST follow TDD workflow: write tests first, then implement.

### Creating a New Domain Module

**Follow TDD Workflow:**
1. Create test files first (`tests/unit/test_{domain}.py`, `tests/integration/test_{domain}_routes.py`)
2. Write failing tests for expected behavior
3. Implement features to make tests pass
4. Verify 100% test coverage

**Implementation Steps:**

1. **Create directory structure:**
   ```bash
   mkdir app/internal/{domain}
   touch app/internal/{domain}/__init__.py
   touch app/internal/{domain}/entity.py
   touch app/internal/{domain}/schema.py
   touch app/internal/{domain}/repository.py
   touch app/internal/{domain}/repository_impl.py
   touch app/internal/{domain}/service.py
   touch app/internal/{domain}/routes.py
   # CREATE TESTS FIRST (TDD)
   touch tests/unit/test_{domain}.py
   touch tests/integration/test_{domain}_routes.py
   ```

2. **Write tests first (TDD Red Phase)**
   - Write unit tests in `tests/unit/test_{domain}.py`
   - Write integration tests in `tests/integration/test_{domain}_routes.py`
   - Run tests to verify they fail

3. **Define entity** (see `app/internal/product/entity.py` for reference)
   - Create `{Domain}Base` with shared fields
   - Create `{Domain}Create` (excludes id, timestamps)
   - Create `{Domain}` with `table=True`

4. **Define schema** (see `app/internal/product/schema.py` for reference)
   - **MUST inherit from `BaseModel`** with explicit serialization aliases
   - Add `model_config = ConfigDict(from_attributes=True, populate_by_name=True)`
   - Use `Field(alias="camelCase", serialization_alias="camelCase")` for snake_case fields
   - Define `{Domain}Create`, `{Domain}Update`, `{Domain}Response`

5. **Implement repository** (see `app/internal/product/repository_impl.py`)
   - Implement abstract methods from base repository
   - Use `self.current_user.auth_id` for audit fields

6. **Implement service** (see `app/internal/product/service.py`)
   - Business logic, validation, exception handling
   - Run unit tests after each method implementation

7. **Create routes** (see `app/internal/product/routes.py`)
   - Define APIRouter with tags
   - Use `SessionDep` and `get_current_user` dependencies
   - Set `response_model` and appropriate `status_code` on all endpoints
   - Run integration tests after each endpoint implementation

8. **Register routes** in `app/main.py`:
   ```python
   from app.internal.{domain} import routes as {domain}_routes
   app.include_router(router={domain}_routes.router, prefix=API_V1_PREFIX)
   ```

### Important Implementation Notes

**For complex domain models (e.g., Invoice with InvoiceDetails):**
- See `app/internal/invoice/` for reference implementation
- Handle nested creates in service layer
- Use transactions for multi-table operations
- Consider using `relationship()` for SQLModel relationships

**For reports/PDF generation:**
- See `app/internal/report/` module
- Uses ReportLab for PDF generation
- Service layer handles data aggregation
- Routes return FileResponse with appropriate headers

**For journal entries (accounting):**
- Double-entry bookkeeping: debits = credits
- Automatically created from invoice operations
- See `app/internal/invoice/service.py` for integration

## Testing

**Test Structure:**
- Unit tests: `tests/unit/` (test services, business logic)
- Integration tests: `tests/integration/` (test API endpoints)
- Fixtures in `tests/conftest.py`

**Key fixtures:**
- `client`: TestClient for API testing
- `session`: Database session
- `mock_user`: User for authentication bypass

**Testing authenticated endpoints:**
```python
# Patch get_current_user dependency
from app.dependencies import get_current_user
from app.internal.user.entity import User

def override_get_current_user():
    return User(auth_id="test_user", permissions=[])

app.dependency_overrides[get_current_user] = override_get_current_user
```

## Environment Configuration

**Required variables** (in `.env`):
```bash
DATABASE_URI=postgresql://user:pass@localhost:5432/bizops_dev
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://your-api-audience
AUTH0_ISSUER=https://your-tenant.auth0.com/
```

**Optional variables:**
```bash
DEBUG=true
LOG_LEVEL=DEBUG
USE_MOCK_AUTH=false  # Set to true to bypass Auth0 validation
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

Configuration loaded via Pydantic Settings in `app/core/config.py`.

## Modern Tooling Stack

This project uses modern Python tooling for improved performance and developer experience:

### uv - Fast Package Installer

**Why uv instead of pip?**
- 10-100x faster than pip
- More reliable dependency resolution
- Built-in virtual environment support
- Better caching and parallel downloads

**Usage:**
```bash
# Install packages
uv pip install package-name

# Install from requirements
uv pip install -r requirements.txt

# Sync dependencies (installs all + dev)
uv sync --all-extras
```

**Important:** The virtual environment (`.venv`) is managed by uv. Always use `uv pip` instead of `pip` for consistency.

### Ruff - Fast Python Linter and Formatter

**Why Ruff instead of Black/Flake8/isort?**
- 10-100x faster than Black
- Replaces multiple tools (Black, Flake8, isort, pyupgrade)
- Fully compatible with Black's formatting style
- Written in Rust for maximum performance
- Single tool for linting and formatting

**Configuration:**
- Line length: 79 (configured in `pyproject.toml`)
- Target version: Python 3.12
- Linting rules: pycodestyle, pyflakes, isort, flake8-bugbear

**When to use what:**
- `ruff format`: Format code (replaces `black`)
- `ruff check`: Lint code (replaces `flake8`, `isort`, etc.)
- `ruff check --fix`: Auto-fix linting issues

### CI/CD Integration

The GitHub Actions workflow (`.github/workflows/ci.yml`) uses these tools:
1. Installs dependencies from `requirements-dev.txt` (ensures version consistency)
2. Runs Ruff linting with GitHub annotations
3. Runs Ruff format check (replaces Black check)
4. Runs MyPy type checking

**Key difference from old setup:**
- ❌ Old: `pip install black ruff mypy` (installs latest versions, inconsistent)
- ✅ New: `pip install -r requirements-dev.txt` (uses pinned versions, consistent)

### Pre-commit Hooks

Pre-commit automatically runs quality checks before each commit:
- File cleanup (trailing whitespace, end-of-file)
- Config validation (YAML, JSON, TOML)
- Ruff linting (with auto-fix)
- Ruff formatting
- MyPy type checking

**Setup:**
```bash
# Install pre-commit hooks (one-time setup)
pre-commit install

# Run manually
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

## Common Gotchas

1. **Always use explicit `Field(serialization_alias="...")` for snake_case fields** in API schemas. Don't rely on CamelCaseSchema inheritance.

2. **Use `model_dump()` not `dict()`** when converting Pydantic models to dicts

3. **Repository constructors take `Session` and `User`** - pass `current_user` from route dependency

4. **Audit fields** (`created_by`, `updated_by`) are automatically set by repositories from `current_user.auth_id`

5. **All API routes use `/api/v1` prefix** - registered in main.py

6. **PostgreSQL vs SQLite**: The engine configuration auto-detects database type. Use PostgreSQL for production.

7. **Mypy errors on entities**: `table=True` syntax causes mypy warnings - disabled in pyproject.toml for entity files

8. **Type annotations**: Use Python 3.12+ union syntax (`str | None`) not `Optional[str]`

9. **Package management**: Always use `uv pip install` instead of `pip install` for faster, more reliable package installation. The virtual environment is managed by uv.

10. **Code formatting**: Use `ruff format` instead of `black`. Ruff is faster and maintains Black compatibility while providing additional features.

11. **Schema serialization**: Always use explicit `Field(serialization_alias="camelCase")` instead of relying on `CamelCaseSchema` base class. This makes field naming explicit and follows Pydantic v2 best practices.

## Schema Best Practices

### Creating a New Schema

**Template for a basic schema:**
```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ResourceCreate(BaseModel):
    """Schema for creating a new resource."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # Simple fields (no snake_case, no alias needed)
    name: str
    description: str | None = None

    # Snake_case fields (need serialization_alias)
    some_field: str = Field(serialization_alias="someField")


class ResourceResponse(BaseModel):
    """Schema for resource response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    description: str | None
    some_field: str = Field(serialization_alias="someField")

    # Standard audit fields (always use these aliases)
    created_by: str = Field(serialization_alias="createdBy")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_by: str | None = Field(serialization_alias="updatedBy")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")
```

### When to Use serialization_alias

**Use `Field(serialization_alias="...")` when:**
- Field name contains underscore (snake_case) like `created_by`, `date_birth`, `account_number`
- You need the API to return camelCase but store as snake_case

**Don't use serialization_alias when:**
- Field name is already camelCase or single word (e.g., `name`, `email`, `id`)
- Field doesn't need different naming in API vs database

## Key Files to Reference

- `docs/API_SCHEMA_ENTITY_GUIDE.md` - Comprehensive guide for creating endpoints
- `docs/QUICK_REFERENCE.md` - Quick templates and patterns
- `app/dependencies.py` - Auth0 JWT verification and user extraction
- `app/database.py` - Database engine and session management
- `app/internal/product/schema.py` - Simple, clean schema example
- `app/internal/invoice/schema.py` - Complex domain example with nested entities
- `app/internal/report/schemas.py` - Reference implementation for serialization pattern

## Git Workflow

**Main branches:**
- `develop` - main development branch (use for PRs)
- `main` - production branch

**Pre-commit hooks** automatically run:
- Trailing whitespace removal
- YAML/JSON validation
- Ruff linting
- Ruff formatting (replaces Black)
- Mypy type checking

## API Documentation

When server is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
