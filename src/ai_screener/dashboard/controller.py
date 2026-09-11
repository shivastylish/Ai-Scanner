from __future__ import annotations

from dataclasses import dataclass

from ai_screener.backtesting.engine import BacktestEngine
from ai_screener.explainability.models import Explanation
from ai_screener.explainability.service import ExplainabilityService
from ai_screener.ranking.engine import RankedResult, RankingEngine
from ai_screener.scanner.engine import ScannerEngine
from ai_screener.scanner.rules import ScanStrategy


@dataclass(frozen=True)
class DashboardRow:
    """One row of the dashboard's ranked-results table, with everything
    the view needs to render it and its "why selected" panel."""

    ranked_result: RankedResult
    explanation: Explanation
    is_backtested: bool


class DashboardController:
    """Orchestrates the read-only service calls behind one dashboard scan.

    Contains no Qt imports at all, so it's fully unit-testable without a
    QApplication - only the widgets that render DashboardRows need Qt.
    Calls only services (ScannerEngine, RankingEngine,
    ExplainabilityService, BacktestEngine) - never a repository directly
    - per "repositories should never be called directly from UI" in
    copilot-instructions.md and the LLD's "Not Allowed: UI -> Database".
    """

    def __init__(
        self,
        scanner_engine: ScannerEngine,
        ranking_engine: RankingEngine,
        explainability_service: ExplainabilityService,
        backtest_engine: BacktestEngine | None = None,
    ) -> None:
        self._scanner_engine = scanner_engine
        self._ranking_engine = ranking_engine
        self._explainability_service = explainability_service
        self._backtest_engine = backtest_engine

    def run_scan(
        self,
        universe: list[str],
        strategy: ScanStrategy,
        asset_type: str = "equity",
    ) -> list[DashboardRow]:
        scan_results = self._scanner_engine.scan(universe, strategy, asset_type)
        ranked_results = self._ranking_engine.rank(scan_results)

        is_backtested = self._is_backtested(strategy.name, asset_type)

        return [
            DashboardRow(
                ranked_result=ranked,
                explanation=self._explainability_service.explain(
                    ranked.scan_result, ranked
                ),
                is_backtested=is_backtested,
            )
            for ranked in ranked_results
        ]

    def _is_backtested(self, strategy_name: str, asset_type: str) -> bool:
        if self._backtest_engine is None:
            return False

        return (
            self._backtest_engine.get_latest_result(strategy_name, asset_type)
            is not None
        )
