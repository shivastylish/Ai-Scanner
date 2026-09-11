from __future__ import annotations

from ai_screener.explainability.builders.base import ReasonBuilder
from ai_screener.explainability.models import Reason
from ai_screener.ranking.engine import RankedResult
from ai_screener.ranking.factors import find_condition
from ai_screener.scanner.results import ScanResult


class CPRReasonBuilder(ReasonBuilder):
    """Explains the CPR-width evidence behind a recommendation."""

    category = "cpr"

    def build(
        self, scan_result: ScanResult, ranked_result: RankedResult | None
    ) -> Reason | None:
        condition = find_condition(scan_result, "narrow_cpr")

        if condition is None or condition.value is None:
            return None

        return Reason(
            category=self.category,
            statement=condition.description,
            value=condition.value,
            evidence={
                "width_pct": condition.value,
                "threshold_pct": condition.threshold,
            },
        )
