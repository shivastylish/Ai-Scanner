import pandas as pd

from ai_screener.market_data.providers import (
    MarketDataProvider,
    ProviderRegistry,
)


class DummyProvider(MarketDataProvider):

    @property
    def provider_name(self) -> str:
        return "dummy"

    def download_history(self, symbol, start_date=None, end_date=None):
        return pd.DataFrame()

    def validate_symbol(self, symbol):
        return True

    def health_check(self):
        return True


def test_registry():

    ProviderRegistry.register(
        "equity",
        DummyProvider(),
    )

    provider = ProviderRegistry.get("equity")

    assert provider.provider_name == "dummy"