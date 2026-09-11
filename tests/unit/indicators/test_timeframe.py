from __future__ import annotations

from datetime import datetime

import pandas as pd

from ai_screener.indicators.timeframe import assign_period, resample_ohlcv


def test_resample_ohlcv_daily_is_a_passthrough_copy() -> None:
    df = pd.DataFrame(
        [
            {
                "datetime": datetime(2025, 1, 1),
                "open": 1,
                "high": 2,
                "low": 0,
                "close": 1.5,
                "volume": 10,
            }
        ]
    )

    result = resample_ohlcv(df, "daily")

    pd.testing.assert_frame_equal(result, df)
    assert result is not df


def test_resample_ohlcv_weekly_aggregates_ohlcv_correctly() -> None:
    # One full trading week, Monday Jan 6 through Friday Jan 10, 2025.
    df = pd.DataFrame(
        [
            {
                "datetime": datetime(2025, 1, 6),
                "open": 100,
                "high": 105,
                "low": 95,
                "close": 102,
                "volume": 1000,
            },
            {
                "datetime": datetime(2025, 1, 7),
                "open": 102,
                "high": 110,
                "low": 101,
                "close": 108,
                "volume": 1200,
            },
            {
                "datetime": datetime(2025, 1, 8),
                "open": 108,
                "high": 112,
                "low": 90,
                "close": 95,
                "volume": 1500,
            },
            {
                "datetime": datetime(2025, 1, 9),
                "open": 95,
                "high": 100,
                "low": 92,
                "close": 99,
                "volume": 900,
            },
            {
                "datetime": datetime(2025, 1, 10),
                "open": 99,
                "high": 115,
                "low": 98,
                "close": 111,
                "volume": 2000,
            },
        ]
    )

    result = resample_ohlcv(df, "weekly")

    assert len(result) == 1
    week = result.iloc[0]
    assert week["open"] == 100  # first day's open
    assert week["high"] == 115  # max high across the week
    assert week["low"] == 90  # min low across the week
    assert week["close"] == 111  # last day's close
    assert week["volume"] == 1000 + 1200 + 1500 + 900 + 2000


def test_assign_period_groups_a_trading_week_together() -> None:
    df = pd.DataFrame(
        {
            "datetime": [
                datetime(2025, 1, 6),
                datetime(2025, 1, 7),
                datetime(2025, 1, 10),
                datetime(2025, 1, 13),
            ]
        }
    )

    periods = assign_period(df, "weekly")

    assert periods.iloc[0] == periods.iloc[1] == periods.iloc[2]
    assert periods.iloc[3] != periods.iloc[0]
