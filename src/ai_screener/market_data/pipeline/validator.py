from __future__ import annotations

import pandas as pd

from ai_screener.core.exceptions import ValidationError
from ai_screener.market_data.models.schema import STANDARD_COLUMNS


class MarketDataValidator:
    """Validate normalized market data."""

    @staticmethod
    def validate(df: pd.DataFrame) -> pd.DataFrame:

        missing = set(STANDARD_COLUMNS) - set(df.columns)

        if missing:
            raise ValidationError(f"Missing required columns: {sorted(missing)}")

        if df.empty:
            raise ValidationError("Market data is empty.")

        if df["datetime"].isnull().any():
            raise ValidationError("datetime contains null values.")

        if df["close"].isnull().any():
            raise ValidationError("close contains null values.")

        return df
