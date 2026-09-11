from __future__ import annotations

from ai_screener.backtesting.engine import BacktestEngine
from ai_screener.backtesting.repositories.backtest_repository import (
    BacktestRepository,
)
from ai_screener.dashboard.controller import DashboardController
from ai_screener.explainability.repositories.explanation_repository import (
    ExplanationRepository,
)
from ai_screener.explainability.service import ExplainabilityService
from ai_screener.indicators.bootstrap import register_default_indicators
from ai_screener.indicators.service import IndicatorService
from ai_screener.market_data.providers.bootstrap import register_default_providers
from ai_screener.market_data.services import MarketDataService
from ai_screener.ranking.engine import RankingEngine
from ai_screener.scanner.engine import ScannerEngine
from ai_screener.scanner.repositories.scan_result_repository import (
    ScanResultRepository,
)


def build_dashboard_controller() -> DashboardController:
    """Composition root: wires every service the dashboard needs.

    The only place in the dashboard package allowed to construct
    repositories directly - everything downstream of this (the
    controller, the widgets) only ever sees services.
    """

    register_default_providers()
    register_default_indicators()

    market_data_service = MarketDataService()
    indicator_service = IndicatorService(market_data_service=market_data_service)

    scanner_engine = ScannerEngine(
        market_data_service=market_data_service,
        indicator_service=indicator_service,
        repository=ScanResultRepository(),
    )
    ranking_engine = RankingEngine()
    explainability_service = ExplainabilityService(repository=ExplanationRepository())
    backtest_engine = BacktestEngine(
        market_data_service=market_data_service,
        indicator_service=indicator_service,
        repository=BacktestRepository(),
    )

    return DashboardController(
        scanner_engine=scanner_engine,
        ranking_engine=ranking_engine,
        explainability_service=explainability_service,
        backtest_engine=backtest_engine,
    )
