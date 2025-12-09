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

## Adding New Features

### Creating a New Domain Module

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
   ```

2. **Define entity** (see `app/internal/product/entity.py` for reference)
   - Create `{Domain}Base` with shared fields
   - Create `{Domain}Create` (excludes id, timestamps)
   - Create `{Domain}` with `table=True`

3. **Define schema** (see `app/internal/product/schema.py` for reference)
   - **MUST inherit from `BaseModel`** with explicit serialization aliases
   - Add `model_config = ConfigDict(from_attributes=True, populate_by_name=True)`
   - Use `Field(serialization_alias="camelCase")` for snake_case fields
   - Define `{Domain}Create`, `{Domain}Response`

4. **Implement repository** (see `app/internal/product/repository_impl.py`)
   - Implement abstract methods from base repository
   - Use `self.current_user.auth_id` for audit fields

5. **Implement service** (see `app/internal/product/service.py`)
   - Business logic, validation, exception handling

6. **Create routes** (see `app/internal/product/routes.py`)
   - Define APIRouter with tags
   - Use `SessionDep` and `get_current_user` dependencies
   - Set `response_model` on all endpoints

7. **Register routes** in `app/main.py`:
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
