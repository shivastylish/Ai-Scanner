from __future__ import annotations

import pytest

from ai_screener.market_data.normalization.currency_utils import infer_quote_currency


@pytest.mark.parametrize(
    "symbol,expected",
    [
        ("BTCUSDT", "USDT"),
        ("BTC-USDT", "USDT"),
        ("BTC_USDT", "USDT"),
        ("BTC/USDT", "USDT"),
        ("ETHBUSD", "BUSD"),
        ("ETHUSDC", "USDC"),
        ("ETHBTC", "BTC"),
        ("ETHUSD", "USD"),
        ("SOMETHINGWEIRD", "USD"),  # no known suffix -> fallback
    ],
)
def test_infer_quote_currency(symbol: str, expected: str) -> None:
    assert infer_quote_currency(symbol) == expected
