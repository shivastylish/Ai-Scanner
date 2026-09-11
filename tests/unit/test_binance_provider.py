from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ai_screener.market_data.providers.crypto.binance_provider import (
    BinanceProvider,
    _to_ms,
)


def test_provider_name_is_binance() -> None:
    assert BinanceProvider().provider_name == "binance"


def test_to_ms_converts_date_to_unix_milliseconds() -> None:
    assert _to_ms("2025-01-01") == int(
        datetime(2025, 1, 1, tzinfo=UTC).timestamp() * 1000
    )


def test_to_ms_end_of_day_pins_to_2359_59() -> None:
    end_of_day = _to_ms("2025-01-01", end_of_day=True)
    start_of_day = _to_ms("2025-01-01")

    assert end_of_day > start_of_day
    assert end_of_day - start_of_day == (23 * 3600 + 59 * 60 + 59) * 1000


@pytest.mark.live
def test_download_history_reaches_live_binance_api() -> None:
    provider = BinanceProvider()

    df = provider.download_history("BTCUSDT", start_date="2025-01-01")

    assert len(df) > 0
    assert set(["datetime", "open", "high", "low", "close", "volume"]).issubset(
        df.columns
    )
    assert df["volume"].gt(0).any()  # unlike CoinGecko, Binance has real volume


@pytest.mark.live
def test_health_check_reaches_live_binance_api() -> None:
    assert BinanceProvider().health_check() is True
