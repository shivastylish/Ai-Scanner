import pandas as pd

from ai_screener.market_data.models.schema import STANDARD_COLUMNS, AssetType

from .base import DataNormalizer


class CoinGeckoNormalizer(DataNormalizer):
    """Normalizes CoinGeckoProvider's raw OHLCV output into the standard
    schema. Unlike equities, CoinGecko timestamps are already UTC and
    tz-naive after ``pd.to_datetime(..., unit="ms")``, so no timezone
    stripping is needed here (contrast YahooNormalizer)."""

    def normalize(
        self,
        df: pd.DataFrame,
        symbol: str,
    ) -> pd.DataFrame:
        data = df.copy()

        data["symbol"] = symbol
        data["asset_type"] = AssetType.CRYPTO.value
        data["provider"] = "coingecko"
        data["exchange"] = "coingecko"
        data["currency"] = "USD"

        return data[STANDARD_COLUMNS]
