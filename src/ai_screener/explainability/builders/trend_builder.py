from __future__ import annotations

from ai_screener.explainability.builders.base import ReasonBuilder
from ai_screener.explainability.models import Reason
from ai_screener.ranking.engine import RankedResult
from ai_screener.ranking.factors import find_condition
from ai_screener.scanner.results import ScanResult


class TrendReasonBuilder(ReasonBuilder):
    """Explains the trend (close vs. EMA) evidence behind a recommendation."""

    category = "trend"

    def build(
        self, scan_result: ScanResult, ranked_result: RankedResult | None
    ) -> Reason | None:
        condition = find_condition(scan_result, "trend_above_ema")

        if condition is None or condition.value is None:
            return None

        return Reason(
            category=self.category,
            statement=condition.description,
            value=condition.value,
            evidence={"close": condition.value, "ema": condition.threshold},
        )
