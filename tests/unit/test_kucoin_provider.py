from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ai_screener.market_data.providers.crypto.kucoin_provider import (
    KuCoinProvider,
    _to_seconds,
)


def test_provider_name_is_kucoin() -> None:
    assert KuCoinProvider().provider_name == "kucoin"


def test_to_seconds_converts_date_to_unix_seconds() -> None:
    assert _to_seconds("2025-01-01") == int(
        datetime(2025, 1, 1, tzinfo=UTC).timestamp()
    )


@pytest.mark.live
def test_download_history_reaches_live_kucoin_api() -> None:
    provider = KuCoinProvider()

    df = provider.download_history("BTC-USDT", start_date="2025-01-01")

    assert len(df) > 0
    assert df["datetime"].is_monotonic_increasing

    # Sanity check on KuCoin's unusual [time, open, close, high, low, ...]
    # column order (see the provider's docstring): if the mapping were
    # wrong, high/low would routinely fall inside the open/close range
    # instead of bracketing it.
    assert (df["high"] >= df[["open", "close"]].max(axis=1)).all()
    assert (df["low"] <= df[["open", "close"]].min(axis=1)).all()


@pytest.mark.live
def test_health_check_reaches_live_kucoin_api() -> None:
    assert KuCoinProvider().health_check() is True
