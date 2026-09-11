from __future__ import annotations

from datetime import UTC, datetime

from ai_screener.explainability.builders.cpr_builder import CPRReasonBuilder
from ai_screener.explainability.builders.historical_performance_builder import (
    HistoricalPerformanceReasonBuilder,
)
from ai_screener.explainability.builders.momentum_builder import (
    MomentumReasonBuilder,
)
from ai_screener.explainability.builders.risk_builder import RiskReasonBuilder
from ai_screener.explainability.builders.trend_builder import TrendReasonBuilder
from ai_screener.explainability.builders.volume_builder import VolumeReasonBuilder
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
        passed=value is not None,
        value=value,
        threshold=threshold,
        description=f"{name} description",
    )


class TestCPRReasonBuilder:
    def test_builds_reason_from_narrow_cpr_condition(self) -> None:
        scan_result = _scan_result(_condition("narrow_cpr", 0.3, 0.5))

        reason = CPRReasonBuilder().build(scan_result, None)

        assert reason is not None
        assert reason.category == "cpr"
        assert reason.value == 0.3
        assert reason.evidence == {"width_pct": 0.3, "threshold_pct": 0.5}

    def test_returns_none_when_condition_missing(self) -> None:
        assert CPRReasonBuilder().build(_scan_result(), None) is None

    def test_returns_none_when_evidence_missing(self) -> None:
        scan_result = _scan_result(_condition("narrow_cpr", None, 0.5))
        assert CPRReasonBuilder().build(scan_result, None) is None


class TestTrendReasonBuilder:
    def test_builds_reason_from_trend_condition(self) -> None:
        scan_result = _scan_result(_condition("trend_above_ema", 110.0, 100.0))

        reason = TrendReasonBuilder().build(scan_result, None)

        assert reason is not None
        assert reason.category == "trend"
        assert reason.evidence == {"close": 110.0, "ema": 100.0}


class TestVolumeReasonBuilder:
    def test_builds_reason_from_volume_condition(self) -> None:
        scan_result = _scan_result(_condition("volume_above_average", 3000.0, 1000.0))

        reason = VolumeReasonBuilder().build(scan_result, None)

        assert reason is not None
        assert reason.category == "volume"
        assert reason.evidence == {"volume": 3000.0, "average_volume": 1000.0}


class TestMomentumReasonBuilder:
    def test_builds_reason_from_momentum_condition(self) -> None:
        scan_result = _scan_result(_condition("momentum_positive", 65.0, 50.0))

        reason = MomentumReasonBuilder().build(scan_result, None)

        assert reason is not None
        assert reason.category == "momentum"
        assert reason.evidence == {"rsi": 65.0, "threshold": 50.0}


class TestRiskReasonBuilder:
    def test_builds_reason_from_cpr_width(self) -> None:
        scan_result = _scan_result(_condition("narrow_cpr", 0.25, 0.5))

        reason = RiskReasonBuilder().build(scan_result, None)

        assert reason is not None
        assert reason.category == "risk"
        assert "0.25" in reason.statement
        assert reason.evidence == {"cpr_width_pct": 0.25}


class TestHistoricalPerformanceReasonBuilder:
    def test_always_returns_none_until_backtesting_exists(self) -> None:
        scan_result = _scan_result(_condition("narrow_cpr", 0.25, 0.5))

        assert HistoricalPerformanceReasonBuilder().build(scan_result, None) is None
