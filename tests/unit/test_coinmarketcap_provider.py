from __future__ import annotations

import pytest

from ai_screener.config.settings import settings
from ai_screener.core.exceptions import ProviderError
from ai_screener.market_data.providers.crypto.coinmarketcap_provider import (
    CoinMarketCapProvider,
    _extract_quotes,
)

_FABRICATED_PAYLOAD = {
    "data": {
        "BTC": [
            {
                "quotes": [
                    {
                        "time_open": "2025-01-01T00:00:00.000Z",
                        "quote": {
                            "USD": {
                                "open": 42000.0,
                                "high": 42500.0,
                                "low": 41800.0,
                                "close": 42300.0,
                                "volume": 1000.0,
                            }
                        },
                    }
                ]
            }
        ]
    }
}


def test_provider_name_is_coinmarketcap() -> None:
    assert CoinMarketCapProvider().provider_name == "coinmarketcap"


def test_extract_quotes_reads_the_documented_v2_shape() -> None:
    """Verified against CoinMarketCap's documented response shape only -
    see CoinMarketCapProvider's docstring for why this can't be verified
    against the live API in this environment."""

    quotes = _extract_quotes(_FABRICATED_PAYLOAD, "BTC")

    assert len(quotes) == 1
    assert quotes[0]["quote"]["USD"]["close"] == 42300.0


def test_extract_quotes_returns_empty_list_for_unknown_symbol() -> None:
    assert _extract_quotes(_FABRICATED_PAYLOAD, "UNKNOWN") == []


def test_download_history_without_api_key_raises_clearly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "COINMARKETCAP_API_KEY", "")

    with pytest.raises(ProviderError, match="COINMARKETCAP_API_KEY"):
        CoinMarketCapProvider().download_history("BTC")


@pytest.mark.live
@pytest.mark.skipif(
    not settings.COINMARKETCAP_API_KEY,
    reason="COINMARKETCAP_API_KEY not configured - see .env.example",
)
def test_download_history_reaches_live_coinmarketcap_api() -> None:
    provider = CoinMarketCapProvider()

    df = provider.download_history("BTC", start_date="2025-01-01")

    assert len(df) > 0
    assert set(["datetime", "open", "high", "low", "close", "volume"]).issubset(
        df.columns
    )
