from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ai_screener.indicators.calculators.ema import EMACalculator


def test_ema_matches_hand_computed_values() -> None:
    closes = [10, 20, 30, 40, 50]
    df = pd.DataFrame(
        {
            "datetime": [datetime(2025, 1, 1) + timedelta(days=i) for i in range(5)],
            "close": closes,
        }
    )

    result = EMACalculator().compute(df, period=3)

    # alpha = 2 / (period + 1) = 0.5, adjust=False:
    # ema[0] = 10 (seed, masked below min_periods)
    # ema[1] = 0.5*20 + 0.5*10 = 15 (masked below min_periods)
    # ema[2] = 0.5*30 + 0.5*15 = 22.5
    # ema[3] = 0.5*40 + 0.5*22.5 = 31.25
    # ema[4] = 0.5*50 + 0.5*31.25 = 40.625
    assert result["ema_3"].isna().iloc[0]
    assert result["ema_3"].isna().iloc[1]
    assert result["ema_3"].iloc[2] == pytest.approx(22.5)
    assert result["ema_3"].iloc[3] == pytest.approx(31.25)
    assert result["ema_3"].iloc[4] == pytest.approx(40.625)


def test_ema_column_name_includes_period() -> None:
    df = pd.DataFrame({"datetime": [datetime(2025, 1, 1)], "close": [100.0]})

    result = EMACalculator().compute(df, period=9)

    assert "ema_9" in result.columns
