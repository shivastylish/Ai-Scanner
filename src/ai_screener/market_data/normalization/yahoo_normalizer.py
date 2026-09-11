import pandas as pd

from ai_screener.market_data.models.schema import (
    STANDARD_COLUMNS,
    AssetType,
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

        # Yahoo Finance returns exchange-local, timezone-aware timestamps.
        # SQLite's DateTime column silently drops tzinfo on storage, so
        # normalize to naive (exchange wall-clock) here, at the normalizer
        # layer, to keep stored and filtered values consistent.
        datetime_series = pd.to_datetime(data["datetime"])
        if datetime_series.dt.tz is not None:
            datetime_series = datetime_series.dt.tz_localize(None)
        data["datetime"] = datetime_series

        data["symbol"] = symbol
        data["asset_type"] = AssetType.EQUITY.value
        data["provider"] = "yahoo"
        data["exchange"] = "NSE"
        data["currency"] = "INR"

        return data[STANDARD_COLUMNS]
