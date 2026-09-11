from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from ai_screener.market_data.providers import MarketDataProvider


class FakeEquityProvider(MarketDataProvider):
    """Deterministic, network-free stand-in for YahooFinanceProvider.

    Returns data shaped exactly like YahooFinanceProvider.download_history()'s
    raw output (pre-normalization: "Date"/"Open"/"High"/... columns), so it
    can flow through the real YahooNormalizer -> Pipeline -> Repository
    layers in tests without touching the network.
    """

    def __init__(self, provider_name: str = "yahoo", num_days: int = 5) -> None:
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
            base = 100.0 + i

            rows.append(
                {
                    "Date": day,
                    "Open": base,
                    "High": base + 5,
                    "Low": base - 5,
                    "Close": base + 2,
                    "Volume": 1_000_000.0 + i * 1_000,
                }
            )

        return pd.DataFrame(rows)

    def validate_symbol(self, symbol: str) -> bool:
        return True

    def health_check(self) -> bool:
        return True
