from __future__ import annotations

import pandas as pd

from ai_screener.indicators.base import Indicator


class RSICalculator(Indicator):
    """Relative Strength Index, using Wilder's smoothing.

    rs  = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    """

    name = "rsi"

    def compute(  # type: ignore[override]
        self, df: pd.DataFrame, period: int = 14
    ) -> pd.DataFrame:
        delta = df["close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        # Wilder's smoothing is an EWM with alpha = 1 / period.
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Zero average loss means no down moves in the window: RSI should
        # be maximally bullish (100), not undefined/NaN from a 0/0 or x/0
        # division. A fully flat window (no gains or losses at all) is
        # neutral (50) rather than bullish.
        flat = (avg_gain == 0) & (avg_loss == 0)
        gains_only = (avg_loss == 0) & ~flat

        rsi = rsi.where(~flat, 50.0)
        rsi = rsi.where(~gains_only, 100.0)

        return pd.DataFrame(
            {
                "datetime": df["datetime"],
                f"rsi_{period}": rsi,
            }
        )
