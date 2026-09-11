from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from ai_screener.market_data.providers.crypto.coingecko_provider import (
    CoinGeckoProvider,
    _resolve_days,
)


def _days_ago(n: int) -> str:
    return (datetime.now(UTC).date() - timedelta(days=n)).strftime("%Y-%m-%d")


class TestResolveDays:
    def test_defaults_to_30_when_no_start_date_given(self) -> None:
        assert _resolve_days(None) == 30

    @pytest.mark.parametrize(
        "days_back,expected_bucket",
        [
            (1, 1),
            (5, 7),
            (10, 14),
            (20, 30),
            (60, 90),
            (100, 180),
            (200, 365),
            (400, 365),  # beyond the largest bucket - clamps to it
        ],
    )
    def test_rounds_up_to_the_smallest_allowed_bucket(
        self, days_back: int, expected_bucket: int
    ) -> None:
        assert _resolve_days(_days_ago(days_back)) == expected_bucket


def test_provider_name_is_coingecko() -> None:
    assert CoinGeckoProvider().provider_name == "coingecko"


@pytest.mark.live
def test_download_history_reaches_live_coingecko_api() -> None:
    provider = CoinGeckoProvider()

    df = provider.download_history("bitcoin", start_date=_days_ago(7))

    assert len(df) > 0
    assert set(["datetime", "open", "high", "low", "close", "volume"]).issubset(
        df.columns
    )


@pytest.mark.live
def test_health_check_reaches_live_coingecko_api() -> None:
    assert CoinGeckoProvider().health_check() is True
