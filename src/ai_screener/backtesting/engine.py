from __future__ import annotations

from ai_screener.backtesting.config import BacktestConfig
from ai_screener.backtesting.metrics import compute_metrics
from ai_screener.backtesting.repositories.backtest_repository import (
    BacktestRepository,
)
from ai_screener.backtesting.results import BacktestResult
from ai_screener.backtesting.simulator import Trade, TradeSimulator
from ai_screener.core import get_logger
from ai_screener.indicators.service import IndicatorService
from ai_screener.market_data.services import MarketDataService
from ai_screener.scanner.evaluation import evaluate_symbol
from ai_screener.scanner.rules import ScanStrategy

logger = get_logger(__name__)

_DATE_FORMAT = "%Y-%m-%d"


class BacktestEngine:
    """Replays a ScanStrategy bar-by-bar over historical data to see how
    it would have performed, before it's trusted with a live
    recommendation (ADR-005's hard gate, honored by sequencing this
    sprint before the Dashboard).

    Reuses Sprint 3's evaluate_symbol() for signal generation - the same
    look-ahead-safe evaluation path the live scanner uses, called here
    with each historical day as ``as_of_date`` instead of "today" - and
    Sprint 4/5's condition/factor objects are read unchanged from the
    resulting ScanResults. Nothing about a strategy's *decision* logic is
    duplicated; only trade simulation (entry/exit/sizing) is new here.
    """

    def __init__(
        self,
        market_data_service: MarketDataService,
        indicator_service: IndicatorService,
        config: BacktestConfig | None = None,
        repository: BacktestRepository | None = None,
    ) -> None:
        self._market_data_service = market_data_service
        self._indicator_service = indicator_service
        self._config = config or BacktestConfig()
        self._repository = repository

    def run(
        self,
        universe: list[str],
        strategy: ScanStrategy,
        start_date: str,
        end_date: str,
        asset_type: str = "equity",
        persist: bool = True,
    ) -> BacktestResult:
        simulator = TradeSimulator(self._config)
        all_trades: list[Trade] = []

        for symbol in universe:
            all_trades.extend(
                self._run_symbol(
                    symbol, strategy, asset_type, start_date, end_date, simulator
                )
            )

        metrics = compute_metrics(all_trades)

        logger.info(
            "Backtest '%s' over %s..%s: %d trades, %.1f%% win rate.",
            strategy.name,
            start_date,
            end_date,
            metrics.total_trades,
            metrics.win_rate_pct,
        )

        result = BacktestResult(
            strategy_name=strategy.name,
            asset_type=asset_type,
            start_date=start_date,
            end_date=end_date,
            trades=all_trades,
            metrics=metrics,
        )

        if persist and self._repository is not None:
            self._repository.save(result)

        return result

    def get_latest_result(
        self, strategy_name: str, asset_type: str = "equity"
    ) -> BacktestResult | None:
        """Read-only lookup of a strategy's most recent backtest, if any.

        Lets callers (the dashboard, in particular) ask "has this
        strategy been backtested" through the engine rather than calling
        BacktestRepository directly, per "repositories should never be
        called directly from UI" in copilot-instructions.md.
        """

        if self._repository is None:
            return None

        return self._repository.get_latest(strategy_name, asset_type)

    def _run_symbol(
        self,
        symbol: str,
        strategy: ScanStrategy,
        asset_type: str,
        start_date: str,
        end_date: str,
        simulator: TradeSimulator,
    ) -> list[Trade]:
        history = self._market_data_service.get_history(
            symbol, asset_type, start_date=start_date, end_date=end_date
        )

        if history.empty or len(history) < 2:
            return []

        trades: list[Trade] = []
        open_trade: Trade | None = None
        open_trade_entry_index: int | None = None

        for i in range(len(history)):
            row = history.iloc[i]

            if open_trade is not None and open_trade_entry_index is not None:
                days_held = i - open_trade_entry_index
                closed = simulator.check_exit(
                    open_trade,
                    row["datetime"],
                    row["high"],
                    row["low"],
                    row["close"],
                    days_held,
                )
                if closed is not None:
                    trades.append(closed)
                    open_trade = None
                    open_trade_entry_index = None
                    continue

            if open_trade is None and i + 1 < len(history):
                as_of_date = row["datetime"].strftime(_DATE_FORMAT)
                scan_result = evaluate_symbol(
                    symbol,
                    strategy,
                    self._market_data_service,
                    self._indicator_service,
                    asset_type,
                    as_of_date=as_of_date,
                )

                if scan_result is not None and scan_result.passed:
                    entry_row = history.iloc[i + 1]
                    open_trade = simulator.open_trade(
                        symbol, entry_row["datetime"], entry_row["open"]
                    )
                    open_trade_entry_index = i + 1

        if open_trade is not None:
            last_row = history.iloc[-1]
            trades.append(
                simulator.force_close(
                    open_trade, last_row["datetime"], last_row["close"]
                )
            )

        return trades
