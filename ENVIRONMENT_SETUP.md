# Environment Configuration Guide

This document explains how to set up environment variables for different environments.

## Overview

The application uses environment variables for configuration. Different environments (development, testing, production) require different configurations.

## Setup Instructions

### 1. Local Development

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env` with your actual values:

```bash
# Development values
API_TITLE=Business Operations API (Dev)
DEBUG=true
LOG_LEVEL=DEBUG

# Your Auth0 credentials
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://your-api-audience
AUTH0_ISSUER=https://your-tenant.auth0.com/

# Local PostgreSQL
DATABASE_URI=postgresql+psycopg2://user:password@localhost:5432/bizops_dev
```

### 2. Testing Environment

Create a `.env.test` file for running tests:

```bash
# Test Environment Configuration
API_TITLE=Business Operations API (Test)
DEBUG=true
LOG_LEVEL=DEBUG

# Auth0 Configuration (will be mocked in tests)
AUTH0_DOMAIN=test-tenant.auth0.com
AUTH0_AUDIENCE=https://test-api
AUTH0_ISSUER=https://test-tenant.auth0.com/
ALGORITHMS=RS256

# SQLite for unit tests
DATABASE_URI=sqlite:///./test.db
```

### 3. Production Environment

For production, use environment variables directly or a secrets manager (AWS Secrets Manager, Azure Key Vault, etc.).

**Never commit production credentials to version control!**

```bash
# Production values (use secure secrets management)
API_TITLE=Business Operations API
DEBUG=false
LOG_LEVEL=INFO

AUTH0_DOMAIN=prod-tenant.auth0.com
AUTH0_AUDIENCE=https://prod-api-audience
AUTH0_ISSUER=https://prod-tenant.auth0.com/

DATABASE_URI=postgresql+psycopg2://user:secure-password@prod-host:5432/bizops_prod
```

## Required Variables

The following environment variables are **required**:

- `AUTH0_DOMAIN`: Your Auth0 tenant domain
- `AUTH0_AUDIENCE`: API identifier from Auth0
- `AUTH0_ISSUER`: Auth0 issuer URL (usually domain with trailing slash)
- `DATABASE_URI`: PostgreSQL connection string

## Optional Variables

- `API_TITLE`: API title in documentation (default: "API")
- `API_VERSION`: API version (default: "1.0.0")
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: "INFO")
- `ALGORITHMS`: JWT algorithm (default: "RS256")
- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 8000)

## Environment Variable Loading

The application loads environment variables in the following order:

1. System environment variables
2. `.env` file (if present)
3. Default values in `app/core/config.py`

## Security Best Practices

1. **Never commit `.env` files** - They are in `.gitignore`
2. **Use `.env.example`** - Document required variables here
3. **Rotate secrets regularly** - Especially in production
4. **Use secrets management** - For production (AWS Secrets Manager, etc.)
5. **Limit access** - Only grant necessary permissions to production secrets

## Validation

The application validates required environment variables at startup. If required variables are missing, the application will fail to start with a clear error message.

See `app/core/config.py` for the validation logic.



