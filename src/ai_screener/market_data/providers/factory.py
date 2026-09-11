from ai_screener.market_data.providers.base import MarketDataProvider
from ai_screener.market_data.providers.registry import ProviderRegistry


class ProviderFactory:
    """Factory class for resolving providers."""

    @staticmethod
    def get_provider(
        asset_type: str, provider_name: str | None = None
    ) -> MarketDataProvider:
        """Resolve a provider. Pass `provider_name` to address a specific
        provider (e.g. "binance") instead of the asset_type's default."""

        if provider_name is not None:
            return ProviderRegistry.get_by_name(provider_name)
        return ProviderRegistry.get(asset_type)
