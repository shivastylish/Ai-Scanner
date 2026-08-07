from __future__ import annotations

from datetime import datetime

import pandas as pd

from ai_screener.market_data.providers import ProviderFactory
from ai_screener.market_data.services import MarketDataService


class StubRepository:
    def __init__(self) -> None:
        self.saved_frame: pd.DataFrame | None = None

    def save(self, df: pd.DataFrame) -> int:
        self.saved_frame = df.copy()
        return len(df)

    def count(self) -> int:
        return 0


class StubProvider:
    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "symbol": symbol,
                    "datetime": datetime(2025, 1, 1, 9, 15, 0),
                    "open": 100.0,
                    "high": 110.0,
                    "low": 95.0,
                    "close": 108.0,
                    "volume": 1200.0,
                    "asset_type": "equity",
                    "provider": "stub",
                    "exchange": "NSE",
                    "currency": "INR",
                    "created_at": datetime(2025, 1, 1, 9, 15, 0),
                    "updated_at": datetime(2025, 1, 1, 9, 15, 0),
                }
            ]
        )


def test_download_uses_repository_when_save_enabled(monkeypatch) -> None:
    repository = StubRepository()
    service = MarketDataService(repository=repository)

    monkeypatch.setattr(
        ProviderFactory,
        "get_provider",
        lambda asset_type: StubProvider(),
    )

    result = service.download(symbol="RELIANCE.NS")

    assert len(result) == 1
    assert repository.saved_frame is not None
    assert repository.saved_frame["symbol"].tolist() == ["RELIANCE.NS"]


def test_download_skips_repository_when_save_disabled(monkeypatch) -> None:
    repository = StubRepository()
    service = MarketDataService(repository=repository)

    monkeypatch.setattr(
        ProviderFactory,
        "get_provider",
        lambda asset_type: StubProvider(),
    )

    service.download(symbol="RELIANCE.NS", save=False)

    assert repository.saved_frame is None
