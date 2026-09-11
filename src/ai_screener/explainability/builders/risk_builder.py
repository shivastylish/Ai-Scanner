from __future__ import annotations

from ai_screener.explainability.builders.base import ReasonBuilder
from ai_screener.explainability.models import Reason
from ai_screener.ranking.engine import RankedResult
from ai_screener.ranking.factors import find_condition
from ai_screener.scanner.results import ScanResult


class RiskReasonBuilder(ReasonBuilder):
    """Explains the risk framing implied by a narrow CPR.

    Scope note: no dedicated volatility/ATR-based risk condition exists
    in the scanner yet (Sprint 3 didn't add one), so this builder reuses
    the CPR-width evidence already captured, reframed as a
    support/resistance narrative, rather than re-fetching indicators
    directly (which would break the "explainability reads only from
    already-persisted scan output" rule). A dedicated ATR-based risk
    condition would be a natural, backward-compatible follow-up.
    """

    category = "risk"

    def build(
        self, scan_result: ScanResult, ranked_result: RankedResult | None
    ) -> Reason | None:
        condition = find_condition(scan_result, "narrow_cpr")

        if condition is None or condition.value is None:
            return None

        statement = (
            f"A narrow {condition.value:.2f}% CPR defines a tight "
            "support/resistance zone, giving a clearer risk boundary "
            "than a wider one."
        )

        return Reason(
            category=self.category,
            statement=statement,
            value=condition.value,
            evidence={"cpr_width_pct": condition.value},
        )
