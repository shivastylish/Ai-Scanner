from ai_screener.market_data.providers import ProviderRegistry
from ai_screener.market_data.providers.equities import YahooFinanceProvider


def register_default_providers() -> None:
    ProviderRegistry.register(
        "equity",
        YahooFinanceProvider(),
    )