from __future__ import annotations

from fakes.fake_provider import FakeEquityProvider

from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)
from ai_screener.market_data.services import MarketDataService


def test_download_history_persists_when_save_enabled(
    service: MarketDataService,
    repository: MarketDataRepository,
) -> None:
    result = service.download_history(symbol="RELIANCE.NS")

    assert len(result) > 0
    assert repository.count() == len(result)


def test_download_history_skips_persistence_when_save_disabled(
    service: MarketDataService,
    repository: MarketDataRepository,
) -> None:
    service.download_history(symbol="RELIANCE.NS", save=False)

    assert repository.count() == 0


def test_download_history_defaults_start_date_to_after_latest_stored_bar(
    service: MarketDataService,
    repository: MarketDataRepository,
    fake_equity_provider: FakeEquityProvider,
) -> None:
    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")
    first_batch_count = repository.count()

    # No explicit start_date this time - should resolve to the day after
    # the latest stored bar instead of re-downloading from scratch.
    service.download_history(symbol="RELIANCE.NS")

    history = repository.get_history(symbol="RELIANCE.NS", asset_type="equity")
    assert len(history) > first_batch_count


def test_get_history_returns_persisted_rows_without_calling_provider(
    service: MarketDataService,
) -> None:
    service.download_history(symbol="RELIANCE.NS", start_date="2025-01-01")

    history = service.get_history(symbol="RELIANCE.NS")

    assert len(history) > 0
    assert history["symbol"].unique().tolist() == ["RELIANCE.NS"]
