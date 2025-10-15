# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
```bash
# Start development server with hot reload
./run_dev.sh
# Or manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# Start with Docker Compose (includes PostgreSQL)
docker-compose up
```

### Production
```bash
# Start production server with gunicorn + uvicorn workers
./run_prod.sh
# Or manually:
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Testing
```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test types
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only

# Run single test file or function
pytest tests/unit/test_user_service.py
pytest tests/unit/test_user_service.py::TestUserService::test_register_user

# Test with Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Code Quality
```bash
# Lint and auto-fix issues
ruff check app/ --fix

# Format code
black app/

# Type checking
mypy app/

# Run all quality checks
ruff check app/ && black --check app/ && mypy app/

# Pre-commit hooks (runs automatically on commit)
pre-commit run --all-files
```

## Architecture

This is a FastAPI backend using **Domain-Driven Design (DDD)** with clear separation of concerns:

### Core Architecture Layers
- **Domain Layer** (`app/domain/`): Business entities and repository interfaces (ABC)
  - `entities/`: SQLModel database models with relationships
  - `repositories/`: Abstract repository interfaces
  - `builders/`: Entity builders for complex object construction

- **Infrastructure Layer** (`app/infrastructure/`): Data access implementations
  - `repositories/`: Concrete repository implementations inheriting from domain interfaces
  - `database.py`: SQLModel/SQLAlchemy database setup and session management

- **Application Layer** (`app/services/`): Business logic and orchestration
  - Services coordinate between repositories and implement business rules
  - RBAC service handles role-based access control

- **Presentation Layer** (`app/routes/`): FastAPI route handlers
  - Route handlers are thin, delegating to services
  - Use Pydantic schemas for request/response validation

### Key Patterns

**Repository Pattern**: All data access goes through repository interfaces defined in domain layer, implemented in infrastructure layer. Repositories use dependency injection and require a database session.

**Builder Pattern**: Complex entity construction uses builders (e.g., `InvoiceBuilder`, `VendorBuilder`) for clean object creation.

**Authentication & Authorization**:
- Auth0 JWT tokens for authentication via `verify_token()` dependency
- RBAC system with users, roles, and permissions
- Permission checking via `check_permission(resource, action)` decorator
- User auto-creation disabled (see `dependencies.py:144-153`)

**Entity Relationships**: Entities use SQLModel relationships with proper back_populates. All entities have standardized datetime fields (`created_at`, `updated_at`, `created_by`, `updated_by`).

### Configuration
- Environment-based configuration using Pydantic Settings (`app/core/config.py`)
- Required environment variables: `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`, `AUTH0_ISSUER`
- Database connection via `DATABASE_URI` with PostgreSQL + psycopg2

### Database
- PostgreSQL with SQLModel ORM (built on SQLAlchemy)
- Auto-creates tables on startup via `create_db_and_tables()`
- Session management through `SessionDep` dependency injection
- Connection health checks in health endpoints

### Testing Strategy
- Unit tests for services and repositories in `tests/unit/`
- Integration tests for routes in `tests/integration/`
- Test configuration in `pyproject.toml` with coverage reporting
- `conftest.py` provides shared fixtures for database and authentication

### Type Annotation Standards
IMPORTANT: Use Modern Type Syntax
NEVER use Optional[T] - always use X | None instead
