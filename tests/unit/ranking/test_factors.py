from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ai_screener.ranking.factors import (
    CPRWidthFactor,
    MomentumFactor,
    TrendStrengthFactor,
    VolumeFactor,
)
from ai_screener.scanner.conditions.base import ConditionResult
from ai_screener.scanner.results import ScanResult


def _scan_result(*condition_results: ConditionResult) -> ScanResult:
    return ScanResult(
        symbol="TEST.NS",
        passed=True,
        condition_results=list(condition_results),
        scanned_at=datetime.now(UTC),
    )


def _condition(
    name: str, value: float | None, threshold: float | None
) -> ConditionResult:
    return ConditionResult(
        condition_name=name,
        passed=True,
        value=value,
        threshold=threshold,
        description="",
    )


class TestCPRWidthFactor:
    @pytest.mark.parametrize(
        "value,threshold,expected",
        [
            (0.0, 0.5, 1.0),  # fully narrow
            (0.2, 0.5, 0.6),
            (0.5, 0.5, 0.0),  # exactly at threshold
            (1.0, 0.5, 0.0),  # clipped, not negative
        ],
    )
    def test_score(self, value: float, threshold: float, expected: float) -> None:
        result = _scan_result(_condition("narrow_cpr", value, threshold))

        assert CPRWidthFactor().score(result) == pytest.approx(expected)

    def test_score_is_zero_when_condition_missing(self) -> None:
        assert CPRWidthFactor().score(_scan_result()) == 0.0


class TestTrendStrengthFactor:
    @pytest.mark.parametrize(
        "value,threshold,expected",
        [
            (110.0, 100.0, 1.0),  # +10%, at the cap
            (105.0, 100.0, 0.5),  # +5%
            (100.0, 100.0, 0.0),  # at the EMA
            (95.0, 100.0, 0.0),  # below EMA, clipped not negative
        ],
    )
    def test_score(self, value: float, threshold: float, expected: float) -> None:
        result = _scan_result(_condition("trend_above_ema", value, threshold))

        assert TrendStrengthFactor().score(result) == pytest.approx(expected)


class TestVolumeFactor:
    @pytest.mark.parametrize(
        "value,threshold,expected",
        [
            (3000.0, 1000.0, 1.0),  # 3x, at the cap
            (1500.0, 1000.0, 0.5),
            (500.0, 1000.0, pytest.approx(0.5 / 3)),
        ],
    )
    def test_score(self, value: float, threshold: float, expected: float) -> None:
        result = _scan_result(_condition("volume_above_average", value, threshold))

        assert VolumeFactor().score(result) == pytest.approx(expected)


class TestMomentumFactor:
    @pytest.mark.parametrize(
        "value,expected",
        [(75.0, 0.5), (100.0, 1.0), (50.0, 0.0), (25.0, 0.0)],
    )
    def test_score(self, value: float, expected: float) -> None:
        result = _scan_result(_condition("momentum_positive", value, 50.0))

        assert MomentumFactor().score(result) == pytest.approx(expected)
