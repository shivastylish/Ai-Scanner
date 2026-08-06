from __future__ import annotations

import pandas as pd

from ai_screener.core import get_logger
from ai_screener.market_data.providers import ProviderFactory
from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)

logger = get_logger(__name__)


class MarketDataService:
    """Service responsible for orchestrating market data operations."""

    def __init__(self) -> None:
        self._repository = MarketDataRepository()

    def download(
        self,
        symbol: str,
        asset_type: str = "equity",
        start_date: str | None = None,
        end_date: str | None = None,
        save: bool = True,
    ) -> pd.DataFrame:

        logger.info(
            "Downloading %s data for %s",
            asset_type,
            symbol,
        )

        provider = ProviderFactory.get_provider(asset_type)

        df = provider.download_history(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )

        if save:
            self._repository.save(df)

        logger.info(
            "Downloaded %d rows for %s",
            len(df),
            symbol,
        )

        return df

    def get_row_count(self) -> int:
        return self._repository.count()