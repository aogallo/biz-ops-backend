import os

from dotenv import load_dotenv
from pydantic import field_validator
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

    # Database Configuration
    DATABASE_URI: str = (
        "postgresql+psycopg2://user:password@localhost:5432/mydb"
    )

    # Optional configurations
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    @field_validator("AUTH0_ISSUER")
    def validate_auth0_issuer(cls, v):  # noqa: N805
        """Ensure AUTH0_ISSUER ends with a trailing slash."""
        if not v.endswith("/"):
            return f"{v}/"
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


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
