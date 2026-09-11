from __future__ import annotations

from datetime import datetime, time, timedelta

import pandas as pd

from ai_screener.core import get_logger
from ai_screener.market_data.normalization import NormalizerFactory
from ai_screener.market_data.pipeline import MarketDataPipeline
from ai_screener.market_data.providers import ProviderFactory
from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)

logger = get_logger(__name__)

_DATE_FORMAT = "%Y-%m-%d"


class MarketDataService:
    """Public entry point for market data.

    Callers never need to know whether data came from Yahoo, Binance,
    CoinGecko, or another provider, nor how it is validated or stored.
    The service orchestrates the full flow:

        Provider -> Normalizer -> Pipeline -> Repository -> Database
    """

    def __init__(self, repository: MarketDataRepository | None = None) -> None:
        self._repository = repository or MarketDataRepository()

    def download_history(
        self,
        symbol: str,
        asset_type: str = "equity",
        start_date: str | None = None,
        end_date: str | None = None,
        save: bool = True,
        provider_name: str | None = None,
    ) -> pd.DataFrame:
        """Download, normalize, validate, and (by default) persist history.

        When ``start_date`` is omitted and data already exists for this
        symbol, only the missing days after the latest stored bar are
        fetched, so repeated calls are cheap incremental refreshes rather
        than full re-downloads.

        ``provider_name`` picks a specific provider (e.g. "binance")
        instead of asset_type's default - needed once more than one
        provider can serve the same asset_type, which is the normal case
        for crypto (many exchanges) but not equities (one canonical
        source today).
        """

        provider = ProviderFactory.get_provider(asset_type, provider_name)

        resolved_start_date = start_date or self._resolve_incremental_start_date(
            symbol, asset_type, provider.provider_name
        )

        logger.info(
            "Downloading %s data for %s from %s (start=%s, end=%s)",
            asset_type,
            symbol,
            provider.provider_name,
            resolved_start_date,
            end_date,
        )

        raw = provider.download_history(
            symbol=symbol,
            start_date=resolved_start_date,
            end_date=end_date,
        )

        normalizer = NormalizerFactory.get_normalizer(provider.provider_name)
        normalized = normalizer.normalize(raw, symbol)

        processed = MarketDataPipeline.process(normalized)

        if save:
            inserted_count = self._repository.save(processed)
            logger.info("Persisted %d rows for %s", inserted_count, symbol)

        logger.info("Downloaded %d rows for %s", len(processed), symbol)

        return processed

    def get_history(
        self,
        symbol: str,
        asset_type: str = "equity",
        start_date: str | None = None,
        end_date: str | None = None,
        provider_name: str | None = None,
    ) -> pd.DataFrame:
        """Return persisted history for a symbol without touching a provider.

        This is the read path callers (indicators, scanner, dashboard,
        backtesting) should use instead of talking to the repository
        directly. Pass ``provider_name`` when the symbol isn't unique to
        one provider (see download_history's docstring).
        """

        return self._repository.get_history(
            symbol=symbol,
            asset_type=asset_type,
            start_date=_parse_date(start_date),
            end_date=_parse_date(end_date, end_of_day=True),
            provider=provider_name,
        )

    def get_row_count(self) -> int:
        return self._repository.count()

    def _resolve_incremental_start_date(
        self, symbol: str, asset_type: str, provider_name: str
    ) -> str | None:
        """Default start_date to the day after the latest stored bar, if any."""

        latest = self._repository.get_latest_datetime(
            symbol, asset_type, provider=provider_name
        )

        if latest is None:
            return None

        next_day = latest + timedelta(days=1)
        return next_day.strftime(_DATE_FORMAT)


def _parse_date(value: str | None, *, end_of_day: bool = False) -> datetime | None:
    """Parse a "YYYY-MM-DD" date into a naive datetime.

    Naive, matching the convention normalizers use for stored "datetime"
    values (see YahooNormalizer), since SQLite's DateTime column drops
    timezone info on storage.

    When ``end_of_day`` is set, the result is pinned to 23:59:59 so a
    date-only upper bound still includes every bar recorded that day,
    rather than only bars at exactly midnight.
    """

    if value is None:
        return None

    parsed = datetime.strptime(value, _DATE_FORMAT)

    if end_of_day:
        parsed = datetime.combine(parsed.date(), time(23, 59, 59))

    return parsed
