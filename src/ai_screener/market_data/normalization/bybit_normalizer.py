import pandas as pd

from ai_screener.market_data.models.schema import STANDARD_COLUMNS, AssetType
from ai_screener.market_data.normalization.currency_utils import infer_quote_currency

from .base import DataNormalizer


class BybitNormalizer(DataNormalizer):
    """Normalizes BybitProvider's raw OHLCV output into the standard
    schema."""

    def normalize(
        self,
        df: pd.DataFrame,
        symbol: str,
    ) -> pd.DataFrame:
        data = df.copy()

        data["symbol"] = symbol
        data["asset_type"] = AssetType.CRYPTO.value
        data["provider"] = "bybit"
        data["exchange"] = "bybit"
        data["currency"] = infer_quote_currency(symbol)

        return data[STANDARD_COLUMNS]
