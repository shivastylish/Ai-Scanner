from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ai_screener.backtesting.engine import BacktestEngine
from ai_screener.backtesting.repositories.backtest_repository import (
    BacktestRepository,
)
from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)
from ai_screener.scanner.conditions.base import Condition, ConditionResult
from ai_screener.scanner.context import ScanContext
from ai_screener.scanner.rules import AllOf, ScanStrategy


class AlwaysPassCondition(Condition):
    """A condition that always passes, regardless of context.

    Isolates the backtest ENGINE's trade-simulation/look-ahead behavior
    from the scanner CONDITIONS' own logic (already covered by
    tests/unit/scanner/test_conditions.py) - here we only care about when
    the engine enters/exits trades relative to the data it was given.
    """

    name = "always_pass"

    def evaluate(self, context: ScanContext) -> ConditionResult:
        return ConditionResult("always_pass", True, None, None, "always passes")


def _always_pass_strategy() -> ScanStrategy:
    return ScanStrategy(
        name="always_pass_strategy", rule=AllOf([AlwaysPassCondition()])
    )


def _seed_history(repository: MarketDataRepository, bars: list[dict]) -> None:
    rows = [
        {
            "symbol": "STUB.NS",
            "datetime": datetime(2025, 1, 1) + timedelta(days=i),
            "open": bar["open"],
            "high": bar["high"],
            "low": bar["low"],
            "close": bar["close"],
            "volume": 1000.0,
            "asset_type": "equity",
            "provider": "yahoo",
            "exchange": "NSE",
            "currency": "INR",
            "created_at": datetime(2025, 1, 1),
            "updated_at": datetime(2025, 1, 1),
        }
        for i, bar in enumerate(bars)
    ]
    repository.save(pd.DataFrame(rows))


# Day 1: signal (always-pass) fires -> entry planned for day 2's open.
# Day 2: entry at open=105.
# Day 4: high=116 hits the 10% take-profit target of 115.5 -> exit there.
# Day 5: signal fires again (position just closed) -> entry for day 6.
# Day 6: entry at open=120. Never hits its stop (114) or target (132)
#        through day 10 -> force-closed at day 10's close (123).
_BARS = [
    {"open": 100, "high": 102, "low": 99, "close": 101},  # day 1
    {"open": 105, "high": 106, "low": 104, "close": 105},  # day 2 (entry 1)
    {"open": 105, "high": 107, "low": 103, "close": 106},  # day 3
    {"open": 110, "high": 116, "low": 109, "close": 114},  # day 4 (take-profit)
    {"open": 114, "high": 117, "low": 112, "close": 115},  # day 5
    {"open": 120, "high": 121, "low": 118, "close": 119},  # day 6 (entry 2)
    {"open": 119, "high": 122, "low": 117, "close": 120},  # day 7
    {"open": 120, "high": 123, "low": 118, "close": 121},  # day 8
    {"open": 121, "high": 124, "low": 119, "close": 122},  # day 9
    {"open": 122, "high": 125, "low": 120, "close": 123},  # day 10 (forced close)
]


def test_backtest_enters_the_day_after_a_signal_at_the_open(
    repository: MarketDataRepository,
    backtest_engine: BacktestEngine,
) -> None:
    _seed_history(repository, _BARS)

    result = backtest_engine.run(
        universe=["STUB.NS"],
        strategy=_always_pass_strategy(),
        start_date="2025-01-01",
        end_date="2025-01-10",
    )

    assert len(result.trades) == 2

    first_trade = result.trades[0]
    assert first_trade.entry_date == datetime(2025, 1, 2)  # day after the signal
    assert first_trade.entry_price == pytest.approx(105.0)


def test_backtest_exits_at_take_profit_and_reenters_after(
    repository: MarketDataRepository,
    backtest_engine: BacktestEngine,
) -> None:
    _seed_history(repository, _BARS)

    result = backtest_engine.run(
        universe=["STUB.NS"],
        strategy=_always_pass_strategy(),
        start_date="2025-01-01",
        end_date="2025-01-10",
    )

    first_trade, second_trade = result.trades

    assert first_trade.exit_reason == "take_profit"
    assert first_trade.exit_price == pytest.approx(115.5)  # 105 * 1.10
    assert first_trade.pnl == pytest.approx(10000.0)  # 10% of 100_000 notional
    assert first_trade.exit_date == datetime(2025, 1, 4)

    assert second_trade.entry_date == datetime(2025, 1, 6)
    assert second_trade.entry_price == pytest.approx(120.0)


def test_backtest_force_closes_open_trades_at_window_end(
    repository: MarketDataRepository,
    backtest_engine: BacktestEngine,
) -> None:
    _seed_history(repository, _BARS)

    result = backtest_engine.run(
        universe=["STUB.NS"],
        strategy=_always_pass_strategy(),
        start_date="2025-01-01",
        end_date="2025-01-10",
    )

    second_trade = result.trades[1]

    assert second_trade.exit_reason == "end_of_backtest"
    assert second_trade.exit_date == datetime(2025, 1, 10)
    assert second_trade.exit_price == pytest.approx(123.0)


def test_backtest_metrics_are_computed_from_the_trades(
    repository: MarketDataRepository,
    backtest_engine: BacktestEngine,
) -> None:
    _seed_history(repository, _BARS)

    result = backtest_engine.run(
        universe=["STUB.NS"],
        strategy=_always_pass_strategy(),
        start_date="2025-01-01",
        end_date="2025-01-10",
    )

    assert result.metrics.total_trades == 2
    assert result.metrics.win_rate_pct == pytest.approx(100.0)
    assert result.metrics.total_pnl == pytest.approx(10000.0 + 2500.0)


def test_backtest_persists_by_default(
    repository: MarketDataRepository,
    backtest_engine: BacktestEngine,
    backtest_repository: BacktestRepository,
) -> None:
    _seed_history(repository, _BARS)

    backtest_engine.run(
        universe=["STUB.NS"],
        strategy=_always_pass_strategy(),
        start_date="2025-01-01",
        end_date="2025-01-10",
    )

    persisted = backtest_repository.get_latest("always_pass_strategy")
    assert persisted is not None
    assert persisted.metrics.total_trades == 2
    assert len(persisted.trades) == 2


def test_backtest_does_not_persist_when_persist_is_false(
    repository: MarketDataRepository,
    backtest_engine: BacktestEngine,
    backtest_repository: BacktestRepository,
) -> None:
    _seed_history(repository, _BARS)

    backtest_engine.run(
        universe=["STUB.NS"],
        strategy=_always_pass_strategy(),
        start_date="2025-01-01",
        end_date="2025-01-10",
        persist=False,
    )

    assert backtest_repository.get_latest("always_pass_strategy") is None


def test_backtest_skips_symbols_with_no_data(
    backtest_engine: BacktestEngine,
) -> None:
    result = backtest_engine.run(
        universe=["UNKNOWN.NS"],
        strategy=_always_pass_strategy(),
        start_date="2025-01-01",
        end_date="2025-01-10",
    )

    assert result.trades == []
    assert result.metrics.total_trades == 0
