from dotenv import load_dotenv
import os
from pydantic import BaseSettings, Field, validator
from typing import Optional

# Load environment variables at module import
load_dotenv()


class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "API"
    API_VERSION: str = "1.0.0"
    
    # Auth0 Configuration
    AUTH0_DOMAIN: str = Field(..., env="AUTH0_DOMAIN")
    AUTH0_AUDIENCE: str = Field(..., env="AUTH0_AUDIENCE")
    AUTH0_ISSUER: str = Field(..., env="AUTH0_ISSUER")
    ALGORITHMS: str = Field(default="RS256", env="ALGORITHMS")
    
    # Database Configuration
    DATABASE_URI: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/mydb",
        env="DATABASE_URI"
    )
    
    # Optional configurations
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    @validator("AUTH0_ISSUER")
    def validate_auth0_issuer(cls, v):
        if not v.endswith("/"):
            return f"{v}/"
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a global settings instance
settings = Settings()

# Export settings for easy access
API_TITLE = settings.API_TITLE
API_VERSION = settings.API_VERSION
AUTH0_DOMAIN = settings.AUTH0_DOMAIN
AUTH0_AUDIENCE = settings.AUTH0_AUDIENCE
AUTH0_ISSUER = settings.AUTH0_ISSUER
ALGORITHMS = settings.ALGORITHMS
DATABASE_URI = settings.DATABASE_URI
DEBUG = settings.DEBUG
LOG_LEVEL = settings.LOG_LEVEL

# Validate required environment variables
required_env_vars = ["AUTH0_DOMAIN", "AUTH0_AUDIENCE", "AUTH0_ISSUER"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 