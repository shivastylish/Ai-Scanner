from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ai_screener.market_data.providers.crypto.bybit_provider import (
    BybitProvider,
    _to_ms,
)


def test_provider_name_is_bybit() -> None:
    assert BybitProvider().provider_name == "bybit"


def test_to_ms_converts_date_to_unix_milliseconds() -> None:
    assert _to_ms("2025-01-01") == int(
        datetime(2025, 1, 1, tzinfo=UTC).timestamp() * 1000
    )


@pytest.mark.live
def test_download_history_reaches_live_bybit_api() -> None:
    provider = BybitProvider()

    df = provider.download_history("BTCUSDT", start_date="2025-01-01")

    assert len(df) > 0
    assert df["datetime"].is_monotonic_increasing
    assert set(["datetime", "open", "high", "low", "close", "volume"]).issubset(
        df.columns
    )


@pytest.mark.live
def test_health_check_reaches_live_bybit_api() -> None:
    assert BybitProvider().health_check() is True
