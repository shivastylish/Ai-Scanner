from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "AI Screener"
    APP_VERSION: str = "0.2.0-dev"
    ENVIRONMENT: str = Field(default="development")

    LOG_LEVEL: str = Field(default="INFO")

    DATABASE_URL: str = Field(
        default="sqlite:///data/ai_screener.db"
    )

    DEFAULT_EQUITY_PROVIDER: str = "yahoo"
    DEFAULT_MUTUAL_FUND_PROVIDER: str = "mfapi"

    ENABLE_YAHOO: bool = True
    ENABLE_MFAPI: bool = True
    ENABLE_COINGECKO: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()