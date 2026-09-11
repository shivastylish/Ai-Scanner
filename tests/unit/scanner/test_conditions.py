from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ai_screener.scanner.conditions.cpr_conditions import NarrowCPRCondition
from ai_screener.scanner.conditions.momentum_conditions import (
    MomentumPositiveCondition,
)
from ai_screener.scanner.conditions.trend_conditions import TrendAboveEMACondition
from ai_screener.scanner.conditions.volume_conditions import (
    VolumeAboveAverageCondition,
)
from ai_screener.scanner.context import ScanContext


def _context(indicators: dict, history: pd.DataFrame | None = None) -> ScanContext:
    return ScanContext(
        symbol="TEST.NS",
        history=history if history is not None else pd.DataFrame(),
        indicators=indicators,
    )


class TestNarrowCPRCondition:
    def test_passes_when_width_under_threshold(self) -> None:
        condition = NarrowCPRCondition(max_width_pct=0.5, timeframe="monthly")
        result = condition.evaluate(_context({"cpr_monthly_width_pct": 0.3}))

        assert result.passed is True
        assert result.value == 0.3

    def test_fails_when_width_over_threshold(self) -> None:
        condition = NarrowCPRCondition(max_width_pct=0.5, timeframe="monthly")
        result = condition.evaluate(_context({"cpr_monthly_width_pct": 2.0}))

        assert result.passed is False

    def test_fails_gracefully_when_data_missing(self) -> None:
        condition = NarrowCPRCondition(max_width_pct=0.5, timeframe="monthly")
        result = condition.evaluate(_context({}))

        assert result.passed is False
        assert result.value is None
        assert "No monthly CPR data" in result.description


class TestTrendAboveEMACondition:
    def test_passes_when_close_above_ema(self) -> None:
        history = pd.DataFrame({"close": [100.0, 105.0, 110.0]})
        condition = TrendAboveEMACondition(period=20)

        result = condition.evaluate(_context({"ema_ema_20": 100.0}, history))

        assert result.passed is True
        assert result.value == 110.0

    def test_fails_when_close_below_ema(self) -> None:
        history = pd.DataFrame({"close": [100.0, 95.0, 90.0]})
        condition = TrendAboveEMACondition(period=20)

        result = condition.evaluate(_context({"ema_ema_20": 100.0}, history))

        assert result.passed is False

    def test_fails_gracefully_when_history_empty(self) -> None:
        condition = TrendAboveEMACondition(period=20)

        result = condition.evaluate(_context({"ema_ema_20": 100.0}))

        assert result.passed is False


class TestVolumeAboveAverageCondition:
    def _history(self, volumes: list[float]) -> pd.DataFrame:
        start = datetime(2025, 1, 1)
        return pd.DataFrame(
            {
                "datetime": [start + timedelta(days=i) for i in range(len(volumes))],
                "volume": volumes,
            }
        )

    def test_passes_when_volume_above_average(self) -> None:
        volumes = [1000.0] * 20 + [5000.0]
        condition = VolumeAboveAverageCondition(lookback=20, multiplier=1.0)

        result = condition.evaluate(_context({}, self._history(volumes)))

        assert result.passed is True
        assert result.value == 5000.0
        assert result.threshold == 1000.0

    def test_fails_when_volume_below_average(self) -> None:
        volumes = [1000.0] * 20 + [500.0]
        condition = VolumeAboveAverageCondition(lookback=20, multiplier=1.0)

        result = condition.evaluate(_context({}, self._history(volumes)))

        assert result.passed is False

    def test_fails_gracefully_with_insufficient_history(self) -> None:
        condition = VolumeAboveAverageCondition(lookback=20, multiplier=1.0)

        result = condition.evaluate(_context({}, self._history([1000.0] * 5)))

        assert result.passed is False
        assert "Not enough history" in result.description


class TestMomentumPositiveCondition:
    @pytest.mark.parametrize(
        "rsi_value,expected",
        [(60.0, True), (40.0, False), (50.0, False)],
    )
    def test_passes_above_threshold(self, rsi_value: float, expected: bool) -> None:
        condition = MomentumPositiveCondition(rsi_period=14, rsi_threshold=50.0)

        result = condition.evaluate(_context({"rsi_rsi_14": rsi_value}))

        assert result.passed is expected

    def test_fails_gracefully_when_data_missing(self) -> None:
        condition = MomentumPositiveCondition()

        result = condition.evaluate(_context({}))

        assert result.passed is False
        assert "No RSI" in result.description
