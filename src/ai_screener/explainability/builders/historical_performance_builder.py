from __future__ import annotations

from ai_screener.explainability.builders.base import ReasonBuilder
from ai_screener.explainability.models import Reason
from ai_screener.ranking.engine import RankedResult
from ai_screener.scanner.results import ScanResult


class HistoricalPerformanceReasonBuilder(ReasonBuilder):
    """Explains how this strategy has historically performed.

    Ships without real data: backtesting doesn't exist until Sprint 6.
    The PRD already treats historical evidence as "when available," so
    this is a legitimate partial ship - it always returns None for now
    and should be filled in with real backtest statistics once Sprint 6
    lands, without needing to change the ExplainabilityService or any
    other builder.
    """

    category = "historical_performance"

    def build(
        self, scan_result: ScanResult, ranked_result: RankedResult | None
    ) -> Reason | None:
        return None
