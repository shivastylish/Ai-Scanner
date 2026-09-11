from ai_screener.core.exceptions import ProviderError
from ai_screener.market_data.providers.base import MarketDataProvider


class ProviderRegistry:
    """Registry for market data providers.

    Two lookup paths:
    - by asset_type ("equity", "crypto", ...): the *default* provider
      for that asset class, used when a caller doesn't care which
      exchange/source it comes from.
    - by provider name ("binance", "bybit", "kucoin", "coingecko",
      "coinmarketcap", ...): a specific provider, needed once more than
      one provider can serve the same asset_type - unlike equities
      (one canonical source, Yahoo Finance), crypto trades across many
      exchanges with genuinely different prices/pairs, so "crypto" alone
      isn't enough to pick a source once several are registered.
    """

    _providers: dict[str, MarketDataProvider] = {}
    _providers_by_name: dict[str, MarketDataProvider] = {}

    @classmethod
    def register(
        cls,
        asset_type: str,
        provider: MarketDataProvider,
    ) -> None:
        """Register `provider` as the default for `asset_type`, and
        (always) make it addressable by its own provider_name too."""

        cls._providers[asset_type] = provider
        cls._providers_by_name[provider.provider_name] = provider

    @classmethod
    def register_named(cls, provider: MarketDataProvider) -> None:
        """Register `provider` by name only, without making it the
        default for any asset_type - for a provider that coexists
        alongside others of the same asset class (e.g. a second crypto
        exchange) rather than replacing the default."""

        cls._providers_by_name[provider.provider_name] = provider

    @classmethod
    def get(cls, asset_type: str) -> MarketDataProvider:
        if asset_type not in cls._providers:
            raise ProviderError(f"No provider registered for '{asset_type}'.")
        return cls._providers[asset_type]

    @classmethod
    def get_by_name(cls, provider_name: str) -> MarketDataProvider:
        if provider_name not in cls._providers_by_name:
            raise ProviderError(f"No provider registered with name '{provider_name}'.")
        return cls._providers_by_name[provider_name]

    @classmethod
    def registered_providers(cls) -> list[str]:
        return sorted(cls._providers.keys())

    @classmethod
    def registered_provider_names(cls) -> list[str]:
        return sorted(cls._providers_by_name.keys())
