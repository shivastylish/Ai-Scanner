from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

from ai_screener.indicators.calculators.cpr import CPRCalculator


def _ohlcv(rows: list[dict[str, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def test_daily_cpr_uses_previous_days_ohlc() -> None:
    df = _ohlcv(
        [
            {
                "datetime": datetime(2025, 1, 1),
                "open": 100,
                "high": 110,
                "low": 90,
                "close": 105,
                "volume": 1000,
            },
            {
                "datetime": datetime(2025, 1, 2),
                "open": 105,
                "high": 120,
                "low": 100,
                "close": 108,
                "volume": 1000,
            },
            {
                "datetime": datetime(2025, 1, 3),
                "open": 108,
                "high": 200,
                "low": 180,
                "close": 190,
                "volume": 1000,
            },
        ]
    )

    result = CPRCalculator().compute(df, timeframe="daily")

    # Day 1 has no prior bar to derive a CPR from.
    assert result.iloc[0][["pivot", "bc", "tc", "width", "width_pct"]].isna().all()
    assert pd.isna(result.iloc[0]["virgin"])

    # Day 2's CPR is derived from day 1's own H/L/C: (110+90+105)/3, etc.
    day2 = result.iloc[1]
    assert day2["pivot"] == pytest.approx(101.666667, abs=1e-6)
    assert day2["bc"] == pytest.approx(100.0)
    assert day2["tc"] == pytest.approx(103.333333, abs=1e-6)
    assert day2["width"] == pytest.approx(3.333333, abs=1e-6)
    assert day2["width_pct"] == pytest.approx(3.278689, abs=1e-6)
    # Day 2's own range [100, 120] overlaps that band [100, 103.33].
    assert day2["virgin"] == False  # noqa: E712

    # Day 3's CPR is derived from day 2's own H/L/C: (120+100+108)/3, etc.
    day3 = result.iloc[2]
    assert day3["pivot"] == pytest.approx(109.333333, abs=1e-6)
    assert day3["bc"] == pytest.approx(110.0)
    assert day3["tc"] == pytest.approx(108.666667, abs=1e-6)
    assert day3["width"] == pytest.approx(1.333333, abs=1e-6)
    assert day3["width_pct"] == pytest.approx(1.219512, abs=1e-6)
    # Day 3 gapped up to [180, 200], nowhere near that [108.67, 110] band.
    assert day3["virgin"] == True  # noqa: E712


def test_narrower_cpr_has_smaller_width_pct() -> None:
    """Sanity check for the scanner's "narrow CPR" use case: a period with
    high close to low relative to price level produces a tighter band."""

    tight = _ohlcv(
        [
            {
                "datetime": datetime(2025, 1, 1),
                "open": 100,
                "high": 101,
                "low": 99,
                "close": 100.5,
                "volume": 1000,
            },
            {
                "datetime": datetime(2025, 1, 2),
                "open": 100,
                "high": 101,
                "low": 99,
                "close": 100,
                "volume": 1000,
            },
        ]
    )
    wide = _ohlcv(
        [
            {
                "datetime": datetime(2025, 1, 1),
                "open": 100,
                "high": 150,
                "low": 50,
                "close": 90,
                "volume": 1000,
            },
            {
                "datetime": datetime(2025, 1, 2),
                "open": 100,
                "high": 101,
                "low": 99,
                "close": 100,
                "volume": 1000,
            },
        ]
    )

    tight_width_pct = (
        CPRCalculator().compute(tight, timeframe="daily").iloc[1]["width_pct"]
    )
    wide_width_pct = (
        CPRCalculator().compute(wide, timeframe="daily").iloc[1]["width_pct"]
    )

    assert tight_width_pct < wide_width_pct


def test_weekly_cpr_is_broadcast_to_every_day_in_the_week() -> None:
    # Two full trading weeks (Mon-Fri), Jan 6-10 and Jan 13-17, 2025.
    rows = []
    for day in range(6, 11):
        rows.append(
            {
                "datetime": datetime(2025, 1, day),
                "open": 100 + day,
                "high": 105 + day,
                "low": 95 + day,
                "close": 102 + day,
                "volume": 1000,
            }
        )
    for day in range(13, 18):
        rows.append(
            {
                "datetime": datetime(2025, 1, day),
                "open": 200 + day,
                "high": 205 + day,
                "low": 195 + day,
                "close": 202 + day,
                "volume": 1000,
            }
        )

    df = _ohlcv(rows)

    result = CPRCalculator().compute(df, timeframe="weekly")

    assert len(result) == len(df)

    first_week = result.iloc[0:5]
    second_week = result.iloc[5:10]

    # Every day within a week shares that week's CPR values.
    assert first_week["pivot"].nunique(dropna=False) == 1
    assert second_week["pivot"].nunique(dropna=False) == 1

    # The two weeks used very different underlying prices, so their CPR
    # values (derived from the *previous* week) should differ.
    assert first_week["pivot"].iloc[0] != second_week["pivot"].iloc[0] or pd.isna(
        first_week["pivot"].iloc[0]
    )
