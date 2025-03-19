from functools import lru_cache
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    app_name: str = "Business operations"
    debug: bool = False
    database_url: str = ""
    api_prefix: str = "/api/v1"
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    auth0_domain: str = os.getenv("AUTH0_DOMAIN", "")
    auth0_audience: str = os.getenv("AUTH0_AUDIENCE", "")
    auth0_audience: str = os.getenv("AUTH0_AUDIENCE", "")
    auth0_issuer: str = os.getenv("AUTH0_ISSUER", "")
    algorithms: str = os.getenv("ALGORITHMS", "")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
