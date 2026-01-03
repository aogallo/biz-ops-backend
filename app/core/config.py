import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables at module import
load_dotenv()


class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "API"
    API_VERSION: str = "1.0.0"

    # Mock Authentication Mode
    # When True, Auth0 validation is skipped (useful for local dev/testing)
    USE_MOCK_AUTH: bool = False

    # Auth0 Configuration
    AUTH0_DOMAIN: str = ""
    AUTH0_AUDIENCE: str = ""
    AUTH0_ISSUER: str = ""
    ALGORITHMS: str = "RS256"

    # Feature Flags (for migration from Auth0 to self-hosted)
    ENABLE_AUTH0: bool = True
    ENABLE_SELF_HOSTED_AUTH: bool = True

    # JWT Configuration (self-hosted authentication)
    JWT_SECRET: str = ""  # Generate with: secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email Configuration (SMTP)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Business Ops"

    # OAuth Configuration
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""
    GITHUB_OAUTH_CLIENT_ID: str = ""
    GITHUB_OAUTH_CLIENT_SECRET: str = ""

    # Frontend URL (for email links and OAuth callbacks)
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    # Database Configuration
    DATABASE_URI: str = "sqlite:///./bizops_dev.db"

    # Optional configurations
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # CORS Configuration
    # Comma-separated list of allowed origins
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,http://localhost:8080"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


# Create a global settings instance
settings = Settings()

# Export settings for easy access
API_TITLE = settings.API_TITLE
API_VERSION = settings.API_VERSION
USE_MOCK_AUTH = settings.USE_MOCK_AUTH
AUTH0_DOMAIN = settings.AUTH0_DOMAIN
AUTH0_AUDIENCE = settings.AUTH0_AUDIENCE
AUTH0_ISSUER = settings.AUTH0_ISSUER
ALGORITHMS = settings.ALGORITHMS
DATABASE_URI = settings.DATABASE_URI
DEBUG = settings.DEBUG
LOG_LEVEL = settings.LOG_LEVEL

# Validate required environment variables
# Skip Auth0 validation if using mock authentication
if not USE_MOCK_AUTH:
    required_env_vars = ["AUTH0_DOMAIN", "AUTH0_AUDIENCE", "AUTH0_ISSUER"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        vars_str = ", ".join(missing_vars)
        raise ValueError(f"Missing required environment variables: {vars_str}")
