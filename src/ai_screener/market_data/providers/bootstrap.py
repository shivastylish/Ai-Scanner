from ai_screener.config.settings import settings
from ai_screener.market_data.normalization import (
    BinanceNormalizer,
    BybitNormalizer,
    CoinGeckoNormalizer,
    CoinMarketCapNormalizer,
    DataNormalizer,
    KuCoinNormalizer,
    NormalizerRegistry,
    YahooNormalizer,
)
from ai_screener.market_data.providers import MarketDataProvider, ProviderRegistry
from ai_screener.market_data.providers.crypto import (
    BinanceProvider,
    BybitProvider,
    CoinGeckoProvider,
    CoinMarketCapProvider,
    KuCoinProvider,
)
from ai_screener.market_data.providers.equities import YahooFinanceProvider


def register_default_providers() -> None:
    """Register the default provider and matching normalizer for each
    enabled asset type/exchange (see Settings.ENABLE_* flags).

    Crypto is different from equities: several exchanges can all serve
    "crypto" at once, each addressable by its own provider_name
    (ProviderFactory.get_provider("crypto", provider_name="binance")).
    Settings.DEFAULT_CRYPTO_PROVIDER picks which one "crypto" alone
    resolves to.
    """

    if settings.ENABLE_YAHOO:
        yahoo_provider = YahooFinanceProvider()
        ProviderRegistry.register("equity", yahoo_provider)
        NormalizerRegistry.register(yahoo_provider.provider_name, YahooNormalizer())

    crypto_providers: list[tuple[MarketDataProvider, DataNormalizer]] = []

    if settings.ENABLE_COINGECKO:
        crypto_providers.append((CoinGeckoProvider(), CoinGeckoNormalizer()))
    if settings.ENABLE_BINANCE:
        crypto_providers.append((BinanceProvider(), BinanceNormalizer()))
    if settings.ENABLE_BYBIT:
        crypto_providers.append((BybitProvider(), BybitNormalizer()))
    if settings.ENABLE_KUCOIN:
        crypto_providers.append((KuCoinProvider(), KuCoinNormalizer()))
    if settings.ENABLE_COINMARKETCAP:
        crypto_providers.append((CoinMarketCapProvider(), CoinMarketCapNormalizer()))

    for provider, normalizer in crypto_providers:
        NormalizerRegistry.register(provider.provider_name, normalizer)

        if provider.provider_name == settings.DEFAULT_CRYPTO_PROVIDER:
            ProviderRegistry.register("crypto", provider)
        else:
            ProviderRegistry.register_named(provider)
