from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ai_screener.market_data.models.schema import STANDARD_COLUMNS, AssetType
from ai_screener.market_data.normalization.base import DataNormalizer
from ai_screener.market_data.normalization.registry import NormalizerRegistry
from ai_screener.market_data.providers import MarketDataProvider, ProviderRegistry
from ai_screener.market_data.providers.factory import ProviderFactory
from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)
from ai_screener.market_data.services import MarketDataService


class _FakeExchangeProvider(MarketDataProvider):
    """Two instances of this, under different names, simulate two crypto
    exchanges that both use the "BTCUSDT" symbol convention - the
    scenario that would have silently mixed data together before
    ProviderRegistry/MarketDataService learned to address providers by
    name (see registry.py's docstring)."""

    def __init__(self, name: str, base_price: float, num_days: int = 5) -> None:
        self._name = name
        self._base_price = base_price
        self._num_days = num_days

    @property
    def provider_name(self) -> str:
        return self._name

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
        rows = [
            {
                "datetime": start + timedelta(days=i),
                "open": self._base_price + i,
                "high": self._base_price + i + 5,
                "low": self._base_price + i - 5,
                "close": self._base_price + i + 2,
                "volume": 10.0,
            }
            for i in range(self._num_days)
        ]
        return pd.DataFrame(rows)

    def validate_symbol(self, symbol: str) -> bool:
        return True

    def health_check(self) -> bool:
        return True


class _FakeExchangeNormalizer(DataNormalizer):
    def __init__(self, provider_name: str) -> None:
        self._provider_name = provider_name

    def normalize(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        data = df.copy()
        data["symbol"] = symbol
        data["asset_type"] = AssetType.CRYPTO.value
        data["provider"] = self._provider_name
        data["exchange"] = self._provider_name
        data["currency"] = "USDT"
        return data[STANDARD_COLUMNS]


@pytest.fixture
def two_fake_exchanges(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[_FakeExchangeProvider, _FakeExchangeProvider]:
    provider_a = _FakeExchangeProvider("fake_exchange_a", base_price=100.0)
    provider_b = _FakeExchangeProvider("fake_exchange_b", base_price=900.0)

    monkeypatch.setitem(
        NormalizerRegistry._normalizers,
        "fake_exchange_a",
        _FakeExchangeNormalizer("fake_exchange_a"),
    )
    monkeypatch.setitem(
        NormalizerRegistry._normalizers,
        "fake_exchange_b",
        _FakeExchangeNormalizer("fake_exchange_b"),
    )
    monkeypatch.setitem(
        ProviderRegistry._providers_by_name, "fake_exchange_a", provider_a
    )
    monkeypatch.setitem(
        ProviderRegistry._providers_by_name, "fake_exchange_b", provider_b
    )

    return provider_a, provider_b


def test_provider_factory_resolves_a_specific_provider_by_name(
    two_fake_exchanges: tuple[_FakeExchangeProvider, _FakeExchangeProvider],
) -> None:
    provider = ProviderFactory.get_provider("crypto", provider_name="fake_exchange_a")

    assert provider.provider_name == "fake_exchange_a"


def test_two_providers_writing_the_same_symbol_do_not_collide(
    repository: MarketDataRepository,
    two_fake_exchanges: tuple[_FakeExchangeProvider, _FakeExchangeProvider],
) -> None:
    service = MarketDataService(repository=repository)

    df_a = service.download_history(
        symbol="BTCUSDT",
        asset_type="crypto",
        start_date="2025-01-01",
        provider_name="fake_exchange_a",
    )
    df_b = service.download_history(
        symbol="BTCUSDT",
        asset_type="crypto",
        start_date="2025-01-01",
        provider_name="fake_exchange_b",
    )

    assert len(df_a) == 5
    assert len(df_b) == 5
    assert repository.count() == 10  # both persisted, no upsert collision

    history_a = service.get_history(
        symbol="BTCUSDT", asset_type="crypto", provider_name="fake_exchange_a"
    )
    history_b = service.get_history(
        symbol="BTCUSDT", asset_type="crypto", provider_name="fake_exchange_b"
    )

    assert len(history_a) == 5
    assert len(history_b) == 5
    assert history_a["close"].iloc[0] != history_b["close"].iloc[0]


def test_incremental_fetch_is_isolated_per_provider(
    repository: MarketDataRepository,
    two_fake_exchanges: tuple[_FakeExchangeProvider, _FakeExchangeProvider],
) -> None:
    service = MarketDataService(repository=repository)

    service.download_history(
        symbol="BTCUSDT",
        asset_type="crypto",
        start_date="2025-01-01",
        provider_name="fake_exchange_a",
    )

    # No start_date given for exchange B: if incremental resolution
    # incorrectly used exchange A's latest bar (the bug this test
    # guards against), this would skip ahead instead of correctly
    # starting fresh for a provider that has never been fetched before.
    df_b = service.download_history(
        symbol="BTCUSDT", asset_type="crypto", provider_name="fake_exchange_b"
    )

    assert df_b.iloc[0]["datetime"] == datetime(2025, 1, 1)
