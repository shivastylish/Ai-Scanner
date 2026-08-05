import pandas as pd

from ai_screener.market_data.models.schema import (
    AssetType,
    STANDARD_COLUMNS,
)
from .base import DataNormalizer


class YahooNormalizer(DataNormalizer):

    def normalize(
        self,
        df: pd.DataFrame,
        symbol: str,
    ) -> pd.DataFrame:

        data = df.rename(
            columns={
                "Date": "datetime",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )

        data["symbol"] = symbol
        data["asset_type"] = AssetType.EQUITY.value
        data["provider"] = "yahoo"
        data["exchange"] = "NSE"
        data["currency"] = "INR"

        return data[STANDARD_COLUMNS]