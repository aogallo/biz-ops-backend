# Quick Start Guide

Get the Business Operations API up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.12+)
python3 --version

# Check PostgreSQL (need 14+)
psql --version

# Check Docker (optional)
docker --version
```

## Option 1: Local Development (Fastest)

### 1. Set Up Environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Auth0 credentials and database URI
# Minimum required:
# - AUTH0_DOMAIN
# - AUTH0_AUDIENCE
# - AUTH0_ISSUER
# - DATABASE_URI
```

### 3. Set Up Database

```bash
# Create database
createdb bizops_dev

# Tables will be created automatically on first run
```

### 4. Run the Server

```bash
# Option A: Use the dev script (recommended)
./run_dev.sh

# Option B: Run directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the API

- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## Option 2: Docker (Easiest)

### 1. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Auth0 credentials
```

### 2. Start Everything

```bash
# Start database and API
docker-compose up -d

# View logs
docker-compose logs -f app
```

### 3. Access the API

Same URLs as Option 1!

## Next Steps

### 1. Install Pre-commit Hooks

```bash
pre-commit install
```

### 2. Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### 3. Check Code Quality

```bash
# Lint
ruff check app/

# Format
black app/

# Type check
mypy app/

# Or run all at once
ruff check app/ && black --check app/ && mypy app/
```

### 4. Explore the Code

```
app/
├── main.py           ← Start here!
├── routes/           ← API endpoints
├── services/         ← Business logic
├── domain/
│   ├── entities/     ← Database models
│   └── repositories/ ← Data access interfaces
└── schemas/          ← API request/response models
```

## Common Commands

### Development

```bash
# Start dev server with auto-reload
./run_dev.sh

# Run tests
pytest -v

# Run specific test
pytest tests/unit/test_user_service.py -v

# Check code before commit
pre-commit run --all-files
```

### Docker

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build
```

### Database

```bash
# Connect to database
psql -U your_user -d bizops_dev

# Check tables
psql -U your_user -d bizops_dev -c "\dt"

# Drop database (careful!)
dropdb bizops_dev
createdb bizops_dev
```

## Troubleshooting

### "ModuleNotFoundError"

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Database connection failed"

```bash
# Check PostgreSQL is running
pg_isready

# Check DATABASE_URI in .env
# Should be: postgresql+psycopg2://user:password@localhost:5432/dbname
```

### "Auth0 authentication failed"

- Verify AUTH0_DOMAIN, AUTH0_AUDIENCE, AUTH0_ISSUER in .env
- Make sure values don't have trailing/leading spaces
- AUTH0_ISSUER should end with "/"

### "Port already in use"

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

## Getting Help

1. **Check documentation**:
   - [README.md](README.md) - Complete guide
   - [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing info
   - [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - Environment config

2. **Check logs**:
   ```bash
   # Local development logs are in terminal

   # Docker logs
   docker-compose logs app
   ```

3. **Enable debug mode**:
   ```bash
   # In .env
   DEBUG=true
   LOG_LEVEL=DEBUG
   ```

## What's Next?

- **Add your features**: Create routes, services, and entities
- **Write tests**: Follow examples in `tests/`
- **Update docs**: Keep README.md current
- **Deploy**: See README.md production section

---

**You're ready to develop! 🚀**

For detailed information, see [README.md](README.md)
