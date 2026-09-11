from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ai_screener.indicators.calculators.rsi import RSICalculator


def test_rsi_matches_hand_computed_values() -> None:
    closes = [100, 102, 101, 105, 103, 108]
    df = pd.DataFrame(
        {
            "datetime": [datetime(2025, 1, 1) + timedelta(days=i) for i in range(6)],
            "close": closes,
        }
    )

    result = RSICalculator().compute(df, period=3)

    # Wilder's smoothing (alpha=1/3, adjust=False) over
    # gain=[_,2,0,4,0,5], loss=[_,0,1,0,2,0], min_periods=3.
    assert result["rsi_3"].isna().iloc[0]
    assert result["rsi_3"].isna().iloc[1]
    assert result["rsi_3"].isna().iloc[2]
    assert result["rsi_3"].iloc[3] == pytest.approx(90.909091, abs=1e-4)
    assert result["rsi_3"].iloc[4] == pytest.approx(64.516129, abs=1e-4)
    assert result["rsi_3"].iloc[5] == pytest.approx(83.011583, abs=1e-4)


def test_rsi_is_100_when_all_moves_are_gains() -> None:
    closes = [100, 101, 102, 103, 104]
    df = pd.DataFrame(
        {
            "datetime": [datetime(2025, 1, 1) + timedelta(days=i) for i in range(5)],
            "close": closes,
        }
    )

    result = RSICalculator().compute(df, period=3)

    assert result["rsi_3"].iloc[-1] == pytest.approx(100.0)


def test_rsi_is_neutral_when_price_is_perfectly_flat() -> None:
    closes = [100, 100, 100, 100, 100]
    df = pd.DataFrame(
        {
            "datetime": [datetime(2025, 1, 1) + timedelta(days=i) for i in range(5)],
            "close": closes,
        }
    )

    result = RSICalculator().compute(df, period=3)

    assert result["rsi_3"].iloc[-1] == pytest.approx(50.0)
