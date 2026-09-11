from __future__ import annotations

from datetime import UTC, datetime

from ai_screener.indicators.service import IndicatorService
from ai_screener.market_data.services import MarketDataService
from ai_screener.scanner.context import ScanContext
from ai_screener.scanner.results import ScanResult
from ai_screener.scanner.rules import ScanStrategy


def evaluate_symbol(
    symbol: str,
    strategy: ScanStrategy,
    market_data_service: MarketDataService,
    indicator_service: IndicatorService,
    asset_type: str = "equity",
    as_of_date: str | None = None,
) -> ScanResult | None:
    """Evaluate one symbol against a strategy, as of a given date.

    The single evaluation path shared by ScannerEngine (as_of_date=None,
    i.e. "as of today") and BacktestEngine (as_of_date=a historical day).
    Both call through MarketDataService.get_history()/IndicatorService's
    end_date parameter, so a backtest never sees a bar or an indicator
    value that would not actually have been available on that historical
    day - centralizing this here is what keeps that guarantee in one
    place instead of two.

    Returns None if there is no market data for the symbol as of that
    date (nothing to evaluate).
    """

    history = market_data_service.get_history(symbol, asset_type, end_date=as_of_date)

    if history.empty:
        return None

    indicators = indicator_service.latest(symbol, asset_type, end_date=as_of_date)
    context = ScanContext(symbol=symbol, history=history, indicators=indicators)

    strategy_result = strategy.rule.evaluate(context)

    return ScanResult(
        symbol=symbol,
        passed=strategy_result.passed,
        condition_results=strategy_result.condition_results,
        scanned_at=datetime.now(UTC),
    )
