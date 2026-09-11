from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from ai_screener.market_data.providers import MarketDataProvider


class FakeCryptoProvider(MarketDataProvider):
    """Deterministic, network-free stand-in for CoinGeckoProvider.

    Returns data shaped exactly like CoinGeckoProvider.download_history()'s
    raw output ("datetime"/"open"/"high"/"low"/"close"/"volume" columns,
    volume always 0.0), so it can flow through the real
    CoinGeckoNormalizer -> Pipeline -> Repository layers in tests without
    touching the network.
    """

    def __init__(self, provider_name: str = "coingecko", num_days: int = 5) -> None:
        self._provider_name = provider_name
        self._num_days = num_days

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        start = (
            datetime.strptime(start_date, "%Y-%m-%d")
            if start_date
            else datetime(2025, 1, 1)
        )

        rows = []
        for i in range(self._num_days):
            day = start + timedelta(days=i)
            base = 40000.0 + i * 100

            rows.append(
                {
                    "datetime": day,
                    "open": base,
                    "high": base + 500,
                    "low": base - 500,
                    "close": base + 200,
                    "volume": 0.0,
                }
            )

        return pd.DataFrame(rows)

    def validate_symbol(self, symbol: str) -> bool:
        return True

    def health_check(self) -> bool:
        return True
