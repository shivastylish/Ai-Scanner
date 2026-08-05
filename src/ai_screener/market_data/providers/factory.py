from ai_screener.market_data.providers.registry import ProviderRegistry


class ProviderFactory:
    """Factory class for resolving providers."""

    @staticmethod
    def get_provider(asset_type: str):
        return ProviderRegistry.get(asset_type)