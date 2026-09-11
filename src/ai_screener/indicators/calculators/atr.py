from __future__ import annotations

import pandas as pd

from ai_screener.indicators.base import Indicator


class ATRCalculator(Indicator):
    """Average True Range, using Wilder's smoothing.

    true_range = max(high - low, |high - prev_close|, |low - prev_close|)
    atr        = Wilder-smoothed average of true_range
    """

    name = "atr"

    def compute(  # type: ignore[override]
        self, df: pd.DataFrame, period: int = 14
    ) -> pd.DataFrame:
        prev_close = df["close"].shift(1)

        true_range = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - prev_close).abs(),
                (df["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr = true_range.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

        return pd.DataFrame(
            {
                "datetime": df["datetime"],
                f"atr_{period}": atr,
            }
        )
