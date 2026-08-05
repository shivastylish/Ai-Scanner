from ai_screener.market_data.providers.base import MarketDataProvider


class ProviderRegistry:
    """Registry for market data providers."""

    _providers: dict[str, MarketDataProvider] = {}

    @classmethod
    def register(
        cls,
        asset_type: str,
        provider: MarketDataProvider,
    ) -> None:
        cls._providers[asset_type] = provider

    @classmethod
    def get(cls, asset_type: str) -> MarketDataProvider:
        if asset_type not in cls._providers:
            raise ValueError(
                f"No provider registered for '{asset_type}'."
            )
        return cls._providers[asset_type]

    @classmethod
    def registered_providers(cls) -> list[str]:
        return sorted(cls._providers.keys())