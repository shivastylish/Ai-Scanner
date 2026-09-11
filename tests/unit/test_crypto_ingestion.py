from __future__ import annotations

import pytest
from fakes.fake_crypto_provider import FakeCryptoProvider

from ai_screener.market_data.normalization import (
    CoinGeckoNormalizer,
    NormalizerRegistry,
)
from ai_screener.market_data.providers import ProviderRegistry
from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)
from ai_screener.market_data.services import MarketDataService


@pytest.fixture
def registered_fake_crypto_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Registers a fake CoinGecko-shaped provider plus the real
    CoinGeckoNormalizer - proves the crypto path flows through the same
    Provider -> Normalizer -> Pipeline -> Repository architecture as
    equities, reusing the existing MarketData schema/repository."""

    monkeypatch.setitem(
        NormalizerRegistry._normalizers, "coingecko", CoinGeckoNormalizer()
    )
    monkeypatch.setitem(ProviderRegistry._providers, "crypto", FakeCryptoProvider())


def test_crypto_download_history_flows_through_the_full_stack(
    repository: MarketDataRepository,
    registered_fake_crypto_provider: None,
) -> None:
    service = MarketDataService(repository=repository)

    df = service.download_history(
        symbol="bitcoin", asset_type="crypto", start_date="2025-01-01"
    )

    assert len(df) > 0
    assert (df["asset_type"] == "crypto").all()
    assert (df["provider"] == "coingecko").all()
    assert service.get_row_count() == len(df)


def test_crypto_history_is_readable_via_get_history(
    repository: MarketDataRepository,
    registered_fake_crypto_provider: None,
) -> None:
    service = MarketDataService(repository=repository)
    service.download_history(
        symbol="bitcoin", asset_type="crypto", start_date="2025-01-01"
    )

    history = service.get_history(symbol="bitcoin", asset_type="crypto")

    assert len(history) > 0
    assert history["symbol"].unique().tolist() == ["bitcoin"]
