from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_screener.scanner.conditions.base import ConditionResult


@dataclass(frozen=True)
class ScanResult:
    """One symbol's outcome from a scan - the audit trail entry that
    ranking, explainability, the dashboard, and backtesting all consume.
    """

    symbol: str
    passed: bool
    condition_results: list[ConditionResult]
    scanned_at: datetime

    def evidence_completeness(self) -> float:
        """Fraction (0-100) of this scan's conditions that had real
        underlying data, rather than "no data yet". Shared by ranking's
        and explainability's "confidence" calculations so the two stay
        consistent."""

        if not self.condition_results:
            return 0.0

        with_data = sum(1 for cr in self.condition_results if cr.value is not None)
        return round(with_data / len(self.condition_results) * 100, 2)
