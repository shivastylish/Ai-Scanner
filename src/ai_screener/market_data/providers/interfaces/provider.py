from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class MarketDataProvider(ABC):
    """Base interface for all market data providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name."""

    @abstractmethod
    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """Download historical market data."""

    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """Validate a trading symbol."""

    @abstractmethod
    def health_check(self) -> bool:
        """Check provider availability."""