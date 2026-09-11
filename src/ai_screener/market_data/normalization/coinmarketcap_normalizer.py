import pandas as pd

from ai_screener.market_data.models.schema import STANDARD_COLUMNS, AssetType

from .base import DataNormalizer


class CoinMarketCapNormalizer(DataNormalizer):
    """Normalizes CoinMarketCapProvider's raw OHLCV output into the
    standard schema. Currency is always "USD" - CoinMarketCapProvider
    always requests USD-converted quotes."""

    def normalize(
        self,
        df: pd.DataFrame,
        symbol: str,
    ) -> pd.DataFrame:
        data = df.copy()

        data["symbol"] = symbol
        data["asset_type"] = AssetType.CRYPTO.value
        data["provider"] = "coinmarketcap"
        data["exchange"] = "coinmarketcap"
        data["currency"] = "USD"

        return data[STANDARD_COLUMNS]
