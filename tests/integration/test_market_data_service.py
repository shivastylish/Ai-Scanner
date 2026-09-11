from __future__ import annotations

import pytest

from ai_screener.market_data.providers.bootstrap import (
    register_default_providers,
)
from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)
from ai_screener.market_data.services import (
    MarketDataService,
)


def test_download_history_persists_through_the_full_stack(
    service: MarketDataService,
    repository: MarketDataRepository,
) -> None:
    """End-to-end: fake provider -> real normalizer -> real pipeline ->
    real repository -> in-memory database. No network, no writes to the
    real dev database."""

    df = service.download_history(
        symbol="RELIANCE.NS",
        start_date="2025-01-01",
    )

    assert len(df) > 0
    assert service.get_row_count() == len(df)
    assert repository.count() == len(df)


@pytest.mark.live
def test_download_history_reaches_live_yahoo_finance() -> None:
    """The one true network-dependent check. Excluded from the default
    test run (see the `live` pytest marker); run manually with:

        uv run pytest -m live

    Deliberately does not persist (save=False), so it never writes into
    the real dev database - it only verifies connectivity through the
    provider -> normalizer -> pipeline chain.
    """

    register_default_providers()

    service = MarketDataService()

    df = service.download_history(
        symbol="RELIANCE.NS",
        start_date="2025-01-01",
        end_date="2025-01-10",
        save=False,
    )

    assert len(df) > 0
