from __future__ import annotations

from datetime import datetime

import pandas as pd

from ai_screener.market_data.models.schema import STANDARD_COLUMNS
from ai_screener.market_data.normalization.coinmarketcap_normalizer import (
    CoinMarketCapNormalizer,
)


def test_normalize_maps_raw_ohlcv_into_the_standard_schema() -> None:
    raw = pd.DataFrame(
        [
            {
                "datetime": datetime(2025, 1, 1),
                "open": 42000.0,
                "high": 42500.0,
                "low": 41800.0,
                "close": 42300.0,
                "volume": 999.0,
            }
        ]
    )

    result = CoinMarketCapNormalizer().normalize(raw, "BTC")

    assert list(result.columns) == STANDARD_COLUMNS
    row = result.iloc[0]
    assert row["symbol"] == "BTC"
    assert row["provider"] == "coinmarketcap"
    assert row["currency"] == "USD"
