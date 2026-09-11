from enum import StrEnum


class EquityProvider(StrEnum):
    YAHOO = "yahoo"


class MutualFundProvider(StrEnum):
    MFAPI = "mfapi"


class CryptoProvider(StrEnum):
    COINGECKO = "coingecko"
    COINMARKETCAP = "coinmarketcap"
    BINANCE = "binance"
    BYBIT = "bybit"
    KUCOIN = "kucoin"
