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

    DATABASE_URL: str = Field(default="sqlite:///data/ai_screener.db")

    DEFAULT_EQUITY_PROVIDER: str = "yahoo"
    DEFAULT_MUTUAL_FUND_PROVIDER: str = "mfapi"
    #: Used when a caller asks for asset_type="crypto" without naming a
    #: specific exchange (see ProviderFactory.get_provider). Individual
    #: exchanges are still reachable by name (provider_name="binance",
    #: etc.) regardless of this default.
    DEFAULT_CRYPTO_PROVIDER: str = "coingecko"

    ENABLE_YAHOO: bool = True
    ENABLE_MFAPI: bool = True
    ENABLE_COINGECKO: bool = True
    ENABLE_BINANCE: bool = True
    ENABLE_BYBIT: bool = True
    ENABLE_KUCOIN: bool = True
    #: Off by default: the free tier still requires an API key
    #: (COINMARKETCAP_API_KEY) that most installs won't have configured.
    ENABLE_COINMARKETCAP: bool = False

    COINMARKETCAP_API_KEY: str = Field(default="")

    JOURNAL_SCREENSHOTS_DIR: str = Field(default="data/journal_screenshots")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
