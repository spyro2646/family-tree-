from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_secret_key: SecretStr
    database_url: str = "postgresql+asyncpg://familyroots:familyroots@localhost:5432/familyroots"
    access_token_ttl_minutes: int = 15


@lru_cache
def get_settings() -> Settings:
    return Settings()
