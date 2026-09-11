from __future__ import annotations

import pandas as pd

from ai_screener.indicators.base import Indicator


class MACDCalculator(Indicator):
    """Moving Average Convergence Divergence.

    macd_line   = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    histogram   = macd_line - signal_line
    """

    name = "macd"

    def compute(  # type: ignore[override]
        self,
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> pd.DataFrame:
        fast_ema = df["close"].ewm(span=fast_period, adjust=False).mean()
        slow_ema = df["close"].ewm(span=slow_period, adjust=False).mean()

        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        return pd.DataFrame(
            {
                "datetime": df["datetime"],
                "macd_line": macd_line,
                "macd_signal": signal_line,
                "macd_histogram": histogram,
            }
        )
