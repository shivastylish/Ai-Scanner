from __future__ import annotations

import pandas as pd
import pytest

from ai_screener.market_data.providers import (
    MarketDataProvider,
    ProviderRegistry,
)


class DummyProvider(MarketDataProvider):

    @property
    def provider_name(self) -> str:
        return "dummy"

    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        return pd.DataFrame()

    def validate_symbol(self, symbol: str) -> bool:
        return True

    def health_check(self) -> bool:
        return True


def test_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(ProviderRegistry._providers, "equity", DummyProvider())

    provider = ProviderRegistry.get("equity")

    assert provider.provider_name == "dummy"
