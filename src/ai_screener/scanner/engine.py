from __future__ import annotations

from ai_screener.core import get_logger
from ai_screener.indicators.service import IndicatorService
from ai_screener.market_data.services import MarketDataService
from ai_screener.scanner.evaluation import evaluate_symbol
from ai_screener.scanner.repositories.scan_result_repository import (
    ScanResultRepository,
)
from ai_screener.scanner.results import ScanResult
from ai_screener.scanner.rules import ScanStrategy

logger = get_logger(__name__)


class ScannerEngine:
    """Finds opportunities in a universe of symbols by evaluating a
    ScanStrategy against each symbol's latest market data and indicators.

    Reads only through MarketDataService and IndicatorService - never a
    repository directly - and persists through ScanResultRepository, so
    the flow matches the rest of the codebase's
    Service -> Repository -> Database discipline. Per-symbol evaluation
    itself lives in scanner.evaluation.evaluate_symbol(), shared with
    BacktestEngine (Sprint 6) so both use the exact same, look-ahead-safe
    logic.
    """

    def __init__(
        self,
        market_data_service: MarketDataService,
        indicator_service: IndicatorService,
        repository: ScanResultRepository | None = None,
    ) -> None:
        self._market_data_service = market_data_service
        self._indicator_service = indicator_service
        self._repository = repository

    def scan(
        self,
        universe: list[str],
        strategy: ScanStrategy,
        asset_type: str = "equity",
        persist: bool = True,
    ) -> list[ScanResult]:
        results: list[ScanResult] = []

        for symbol in universe:
            result = evaluate_symbol(
                symbol,
                strategy,
                self._market_data_service,
                self._indicator_service,
                asset_type,
            )

            if result is None:
                logger.info("Skipping %s: no market data available.", symbol)
                continue

            results.append(result)

        logger.info(
            "Scan '%s' evaluated %d/%d symbols, %d passed.",
            strategy.name,
            len(results),
            len(universe),
            sum(1 for r in results if r.passed),
        )

        if persist and self._repository is not None:
            self._repository.save_scan(
                strategy_name=strategy.name,
                asset_type=asset_type,
                results=results,
            )

        return results
