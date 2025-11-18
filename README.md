# Business Operations Backend API

[![CI/CD](https://github.com/aogallo/biz-ops-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/aogallo/biz-ops-backend/actions)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, production-ready FastAPI application for business operations management with PostgreSQL database, Auth0 authentication, and comprehensive RBAC (Role-Based Access Control).

## 🚀 Features

- **FastAPI Framework**: Modern, fast, async Python web framework
- **PostgreSQL Database**: Robust relational database with SQLModel ORM
- **Auth0 Integration**: Enterprise-grade authentication and authorization
- **RBAC System**: Fine-grained role-based access control
- **Domain-Driven Design**: Clean architecture with clear separation of concerns
- **Type Safety**: Full type hints with mypy validation
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Code Quality**: Automated linting, formatting, and pre-commit hooks
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- **Docker Support**: Containerized application with Docker Compose
- **API Documentation**: Auto-generated OpenAPI (Swagger) and ReDoc documentation

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Docker & Docker Compose (optional, for containerized development)
- Auth0 account (for authentication)

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115+
- **ORM**: SQLModel 0.0.24
- **Database**: PostgreSQL with psycopg2
- **Authentication**: Auth0 + PyJWT
- **Testing**: pytest, pytest-asyncio, httpx
- **Code Quality**: ruff, black, mypy
- **Development**: uvicorn, gunicorn
- **Containerization**: Docker, Docker Compose

## 📁 Project Structure

```
biz-ops-backend/
├── app/
│   ├── core/              # Core configuration and utilities
│   │   ├── config.py      # Environment configuration with Pydantic
│   │   ├── security.py    # Security utilities
│   │   ├── logging_config.py  # Logging setup
│   │   └── exceptions.py  # Custom exception classes
│   ├── domain/            # Domain layer (business logic)
│   │   ├── entities/      # SQLModel entities (database models)
│   │   └── repositories/  # Repository interfaces (ABC)
│   ├── infrastructure/    # Infrastructure layer (data access)
│   │   ├── database.py    # Database connection and session management
│   │   └── repositories/  # Repository implementations
│   ├── services/          # Application services (business logic)
│   ├── routes/            # API routes/endpoints
│   ├── schemas/           # Pydantic schemas (API models)
│   ├── dependencies.py    # FastAPI dependencies
│   └── main.py            # Application entry point
├── tests/
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── conftest.py        # Pytest fixtures
├── .github/
│   └── workflows/         # GitHub Actions CI/CD
├── docker-compose.yml     # Docker Compose for local development
├── Dockerfile             # Production Docker image
├── pyproject.toml         # Python project configuration
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd biz-ops-backend
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (for testing and code quality)
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
vim .env  # or use your preferred editor
```

Required environment variables:

```bash
# Auth0 Configuration (Required for production, optional for dev with mock auth)
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://your-api-audience
AUTH0_ISSUER=https://your-tenant.auth0.com/

# Development Mode - Mock Authentication (Optional, for local testing)
# Set to true to bypass Auth0 and use /api/dev/token endpoint
USE_MOCK_AUTH=true

# Database Configuration
DATABASE_URI=postgresql+psycopg2://user:password@localhost:5432/bizops_dev

# API Configuration
API_TITLE=Business Operations API
DEBUG=true
LOG_LEVEL=DEBUG
```

**Quick Tip for Development:** Set `USE_MOCK_AUTH=true` to skip Auth0 setup during local development. You can use the `/api/dev/token` endpoint to get test tokens instantly. See [Development Authentication](#development-authentication-mock-mode) for details.

See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for detailed environment configuration guide.

### 5. Set Up Database

```bash
# Make sure PostgreSQL is running
# Create database
createdb bizops_dev

# The application will automatically create tables on startup
```

### 6. Run the Development Server

**Option A: Using the development script (recommended)**

```bash
./run_dev.sh
```

**Option B: Using uvicorn directly**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

**Option C: Using Docker Compose**

```bash
docker-compose up
```

The API will be available at:

- **API**: http://localhost:8000
- **Swagger Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🐳 Docker Development

### Build and Run with Docker Compose

```bash
# Start all services (database + API)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

### Build Docker Image Manually

```bash
# Build the image
docker build -t bizops-api:latest .

# Run the container
docker run -p 8000:8000 --env-file .env bizops-api:latest
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_user_service.py

# Specific test function
pytest tests/unit/test_user_service.py::TestUserService::test_register_user
```

### Run Tests with Docker

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🎨 Code Quality

### Linting

```bash
# Run ruff (fast Python linter)
ruff check app/

# Auto-fix issues
ruff check app/ --fix
```

### Formatting

```bash
# Check formatting
black --check app/

# Format code
black app/
```

### Type Checking

```bash
# Run mypy
mypy app/
```

### Run All Checks

```bash
# Run all quality checks
ruff check app/ && black --check app/ && mypy app/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks before commits:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

The hooks will automatically:

- Fix trailing whitespace
- Check YAML/JSON syntax
- Run ruff linter
- Format code with black
- Run type checking with mypy

## 📚 API Documentation

### Endpoints

#### Health Check

- `GET /` - Basic health check
- `GET /health` - Detailed health check

#### Users

- `GET /users/` - List all users (requires authentication)

#### Vendors

- `GET /vendors/` - List all vendors (requires authentication)

### Authentication

All protected endpoints require a valid Auth0 JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/users/
```

#### Development Authentication (Mock Mode)

For local development and testing, you can use mock authentication to bypass Auth0 token validation. This eliminates the need to manually extract tokens from Auth0.

**Enable Mock Mode:**

Add to your `.env` file:

```bash
USE_MOCK_AUTH=true
```

**Get a Development Token:**

```bash
# Get a mock JWT token
curl -X POST http://localhost:8000/api/dev/token \
  -H "Content-Type: application/json" \
  -d '{
    "auth_id": "dev_user",
    "email": "dev@example.com"
  }'
```

Response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "user": {
    "auth_id": "dev_user",
    "email": "dev@example.com",
    "picture": "https://via.placeholder.com/150"
  }
}
```

**Use the Token in Postman:**

1. Copy the `access_token` value
2. In Postman, go to the Authorization tab
3. Select "Bearer Token" type
4. Paste the token
5. Make requests to any protected endpoint

**Verify Authentication:**

```bash
curl -X GET http://localhost:8000/api/dev/whoami \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Important Notes:**

- `/api/dev/*` endpoints are **only available** when `USE_MOCK_AUTH=true`
- Mock tokens bypass Auth0 validation completely
- **Never use mock mode in production** - the endpoints return 404 when disabled
- The dev user is automatically created in the database on first token request
- Mock tokens are valid for 7 days by default

### Interactive Documentation

Visit these URLs when the server is running:

- **Swagger UI**: http://localhost:8000/docs

  - Interactive API documentation
  - Try out endpoints directly in the browser
- **ReDoc**: http://localhost:8000/redoc

  - Alternative API documentation
  - Clean, responsive design

## 🚢 Production Deployment

### Using Gunicorn + Uvicorn Workers

```bash
# Run production server
./run_prod.sh
```

Or manually:

```bash
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --log-level info
```

### Environment Configuration

For production:

1. **Never use DEBUG=true**
2. **Use a strong SECRET_KEY**
3. **Use environment variables or secrets manager** (AWS Secrets Manager, Azure Key Vault)
4. **Enable HTTPS** with proper certificates
5. **Set up database connection pooling**
6. **Configure proper logging** (consider ELK stack or cloud logging)
7. **Set up monitoring** (Prometheus, DataDog, New Relic)

### Docker Production Deployment

```bash
# Build production image
docker build -t bizops-api:latest .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  --env-file .env.prod \
  --name bizops-api \
  bizops-api:latest
```

## 🔒 Security

- **Authentication**: Auth0 JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Input Validation**: Pydantic models validate all input
- **SQL Injection Prevention**: SQLModel/SQLAlchemy parameterized queries
- **Environment Variables**: Sensitive data in .env (never committed)
- **HTTPS**: Use reverse proxy (nginx) for SSL/TLS in production

## 🤝 Contributing

### Development Workflow

1. Create a feature branch

   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests and quality checks

   ```bash
   pytest
   ruff check app/
   black app/
   mypy app/
   ```
4. Commit your changes

   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

   Pre-commit hooks will run automatically.
5. Push and create a pull request

   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style Guidelines

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for public functions/classes
- Keep functions focused and small
- Add tests for new features
- Update documentation as needed

### Commit Message Convention

Follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## 📝 Environment Variables Reference

| Variable           | Required | Default | Description                                    |
| ------------------ | -------- | ------- | ---------------------------------------------- |
| `AUTH0_DOMAIN`   | ✅*      | -       | Auth0 tenant domain                            |
| `AUTH0_AUDIENCE` | ✅*      | -       | Auth0 API identifier                           |
| `AUTH0_ISSUER`   | ✅*      | -       | Auth0 issuer URL                               |
| `USE_MOCK_AUTH`  | ❌       | false   | Enable mock auth (dev only, bypasses Auth0)    |
| `DATABASE_URI`   | ✅       | -       | PostgreSQL connection string                   |
| `API_TITLE`      | ❌       | "API"   | API title in docs                              |
| `API_VERSION`    | ❌       | "1.0.0" | API version                                    |
| `DEBUG`          | ❌       | false   | Enable debug mode                              |
| `LOG_LEVEL`      | ❌       | "INFO"  | Logging level                                  |
| `ALGORITHMS`     | ❌       | "RS256" | JWT algorithm                                  |

\* Required only when `USE_MOCK_AUTH=false` (production mode)

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Check connection
psql -U your_user -d bizops_dev
```

### Module Import Errors

```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Auth0 Token Issues

- Verify Auth0 configuration in .env
- Check token expiration
- Ensure audience and issuer match Auth0 settings

## 📄 License

[Your License Here]

## 👥 Authors

[Your Team/Name Here]

## 🔗 Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Auth0 Documentation](https://auth0.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Happy Coding! 🚀**
