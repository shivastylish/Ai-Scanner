from enum import StrEnum


class AssetType(StrEnum):
    EQUITY = "equity"
    MUTUAL_FUND = "mutual_fund"
    CRYPTO = "crypto"
    ETF = "etf"


STANDARD_COLUMNS = [
    "symbol",
    "datetime",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "asset_type",
    "provider",
    "exchange",
    "currency",
]