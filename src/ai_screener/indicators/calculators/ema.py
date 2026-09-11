from __future__ import annotations

import pandas as pd

from ai_screener.indicators.base import Indicator


class EMACalculator(Indicator):
    """Exponential Moving Average of the close price."""

    name = "ema"

    def compute(  # type: ignore[override]
        self, df: pd.DataFrame, period: int = 20
    ) -> pd.DataFrame:
        ema = df["close"].ewm(span=period, adjust=False, min_periods=period).mean()

        return pd.DataFrame(
            {
                "datetime": df["datetime"],
                f"ema_{period}": ema,
            }
        )
