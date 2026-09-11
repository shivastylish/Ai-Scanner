from __future__ import annotations

from abc import ABC, abstractmethod

from ai_screener.scanner.conditions.base import ConditionResult
from ai_screener.scanner.results import ScanResult


def find_condition(
    scan_result: ScanResult, condition_name: str
) -> ConditionResult | None:
    return next(
        (
            cr
            for cr in scan_result.condition_results
            if cr.condition_name == condition_name
        ),
        None,
    )


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


class ScoringFactor(ABC):
    """Scores one aspect of an already-scanned symbol.

    Reads only from ScanResult.condition_results (the evidence Sprint 3's
    conditions already captured) - no re-fetching indicators or market
    data - so ranking is a pure, deterministic function of persisted scan
    output (reproducible given fixed inputs, per the PRD's own success
    criterion for the scanner).
    """

    #: Registry key / weight lookup key. Subclasses must override.
    name: str

    @abstractmethod
    def score(self, scan_result: ScanResult) -> float:
        """Return a score in [0, 1]; higher is more favorable."""


class CPRWidthFactor(ScoringFactor):
    """Narrower CPR (relative to its threshold) scores higher."""

    name = "cpr_width"

    def score(self, scan_result: ScanResult) -> float:
        condition = find_condition(scan_result, "narrow_cpr")

        if condition is None or condition.value is None or not condition.threshold:
            return 0.0

        # Fully narrow (value=0) -> 1.0; right at the threshold -> 0.0.
        return _clip(1 - (condition.value / condition.threshold))


class TrendStrengthFactor(ScoringFactor):
    """How far the close is trading above its EMA, as a fraction of the
    EMA value, scores higher (capped at a generous +10% move)."""

    name = "trend_strength"
    _CAP_PCT = 10.0

    def score(self, scan_result: ScanResult) -> float:
        condition = find_condition(scan_result, "trend_above_ema")

        if condition is None or condition.value is None or not condition.threshold:
            return 0.0

        pct_above = (condition.value - condition.threshold) / condition.threshold * 100
        return _clip(pct_above / self._CAP_PCT)


class VolumeFactor(ScoringFactor):
    """How many multiples of the average volume today's volume reached,
    scores higher (capped at 3x the threshold)."""

    name = "volume"
    _CAP_MULTIPLE = 3.0

    def score(self, scan_result: ScanResult) -> float:
        condition = find_condition(scan_result, "volume_above_average")

        if condition is None or condition.value is None or not condition.threshold:
            return 0.0

        multiple = condition.value / condition.threshold
        return _clip(multiple / self._CAP_MULTIPLE)


class MomentumFactor(ScoringFactor):
    """RSI's distance above the neutral midpoint (50), scaled to [0, 1]."""

    name = "momentum"

    def score(self, scan_result: ScanResult) -> float:
        condition = find_condition(scan_result, "momentum_positive")

        if condition is None or condition.value is None:
            return 0.0

        return _clip((condition.value - 50.0) / 50.0)
