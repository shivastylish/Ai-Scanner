from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ai_screener.indicators.calculators.macd import MACDCalculator


def test_macd_matches_hand_computed_values() -> None:
    closes = [10, 12, 15, 14, 18]
    df = pd.DataFrame(
        {
            "datetime": [datetime(2025, 1, 1) + timedelta(days=i) for i in range(5)],
            "close": closes,
        }
    )

    result = MACDCalculator().compute(df, fast_period=2, slow_period=3, signal_period=2)

    # fast/slow EMAs (adjust=False) start seeded at close[0], so both
    # equal 10 there and macd_line/signal start at 0.
    assert result["macd_line"].iloc[0] == pytest.approx(0.0)
    assert result["macd_signal"].iloc[0] == pytest.approx(0.0)
    assert result["macd_histogram"].iloc[0] == pytest.approx(0.0)

    # Hand-computed via the fast=2/slow=3/signal=2 EWM recursions.
    assert result["macd_line"].iloc[-1] == pytest.approx(289 / 324, abs=1e-6)
    assert result["macd_signal"].iloc[-1] == pytest.approx(367 / 486, abs=1e-6)
    assert result["macd_histogram"].iloc[-1] == pytest.approx(133 / 972, abs=1e-6)


def test_macd_histogram_equals_line_minus_signal() -> None:
    closes = [10, 12, 15, 14, 18, 20, 19, 22]
    df = pd.DataFrame(
        {
            "datetime": [datetime(2025, 1, 1) + timedelta(days=i) for i in range(8)],
            "close": closes,
        }
    )

    result = MACDCalculator().compute(df)

    diff = result["macd_line"] - result["macd_signal"]
    pd.testing.assert_series_equal(result["macd_histogram"], diff, check_names=False)
