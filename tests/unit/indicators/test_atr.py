from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ai_screener.indicators.calculators.atr import ATRCalculator


def test_atr_matches_hand_computed_values() -> None:
    df = pd.DataFrame(
        {
            "datetime": [datetime(2025, 1, 1) + timedelta(days=i) for i in range(4)],
            "high": [102, 108, 106, 112],
            "low": [98, 100, 101, 104],
            "close": [100, 105, 102, 108],
        }
    )

    result = ATRCalculator().compute(df, period=3)

    # True range: [4, 8, 5, 10] (first bar has no prior close, so TR=H-L).
    # Wilder's smoothing (alpha=1/3, adjust=False), min_periods=3.
    assert result["atr_3"].isna().iloc[0]
    assert result["atr_3"].isna().iloc[1]
    assert result["atr_3"].iloc[2] == pytest.approx(47 / 9, abs=1e-6)
    assert result["atr_3"].iloc[3] == pytest.approx(184 / 27, abs=1e-6)
