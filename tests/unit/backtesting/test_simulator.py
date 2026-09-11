from __future__ import annotations

from datetime import datetime

import pytest

from ai_screener.backtesting.config import BacktestConfig
from ai_screener.backtesting.simulator import TradeSimulator

# Defaults: capital_per_trade=100_000, stop_loss_pct=0.05,
# take_profit_pct=0.10, max_holding_days=20.
_CONFIG = BacktestConfig()


def _simulator() -> TradeSimulator:
    return TradeSimulator(_CONFIG)


def test_open_trade_sizes_quantity_from_fixed_capital() -> None:
    trade = _simulator().open_trade("RELIANCE.NS", datetime(2025, 1, 1), 100.0)

    assert trade.quantity == pytest.approx(1000.0)  # 100_000 / 100
    assert trade.is_open


def test_check_exit_triggers_stop_loss() -> None:
    simulator = _simulator()
    trade = simulator.open_trade("X.NS", datetime(2025, 1, 1), 100.0)

    closed = simulator.check_exit(
        trade,
        current_date=datetime(2025, 1, 2),
        current_high=101.0,
        current_low=94.0,  # <= stop price of 95
        current_close=96.0,
        days_held=1,
    )

    assert closed is not None
    assert closed.exit_reason == "stop_loss"
    assert closed.exit_price == pytest.approx(95.0)
    assert closed.pnl == pytest.approx(-5000.0)
    assert closed.return_pct == pytest.approx(-5.0)
    assert not closed.is_open


def test_check_exit_triggers_take_profit() -> None:
    simulator = _simulator()
    trade = simulator.open_trade("X.NS", datetime(2025, 1, 1), 100.0)

    closed = simulator.check_exit(
        trade,
        current_date=datetime(2025, 1, 2),
        current_high=112.0,  # >= target price of 110
        current_low=98.0,
        current_close=109.0,
        days_held=1,
    )

    assert closed is not None
    assert closed.exit_reason == "take_profit"
    assert closed.exit_price == pytest.approx(110.0)
    assert closed.pnl == pytest.approx(10000.0)
    assert closed.return_pct == pytest.approx(10.0)


def test_check_exit_prefers_stop_loss_when_both_hit_same_day() -> None:
    """The stated, conservative tie-break assumption (see BacktestConfig's
    docstring): if a single day's range spans both the stop and the
    target, assume the worst case."""

    simulator = _simulator()
    trade = simulator.open_trade("X.NS", datetime(2025, 1, 1), 100.0)

    closed = simulator.check_exit(
        trade,
        current_date=datetime(2025, 1, 2),
        current_high=115.0,  # would also hit take-profit
        current_low=90.0,  # hits stop-loss
        current_close=105.0,
        days_held=1,
    )

    assert closed is not None
    assert closed.exit_reason == "stop_loss"


def test_check_exit_triggers_max_holding_period() -> None:
    simulator = _simulator()
    trade = simulator.open_trade("X.NS", datetime(2025, 1, 1), 100.0)

    closed = simulator.check_exit(
        trade,
        current_date=datetime(2025, 2, 1),
        current_high=104.0,
        current_low=101.0,
        current_close=103.0,
        days_held=20,
    )

    assert closed is not None
    assert closed.exit_reason == "max_holding_period"
    assert closed.exit_price == pytest.approx(103.0)
    assert closed.pnl == pytest.approx(3000.0)


def test_check_exit_returns_none_when_no_condition_met() -> None:
    simulator = _simulator()
    trade = simulator.open_trade("X.NS", datetime(2025, 1, 1), 100.0)

    result = simulator.check_exit(
        trade,
        current_date=datetime(2025, 1, 2),
        current_high=108.0,
        current_low=96.0,
        current_close=102.0,
        days_held=5,
    )

    assert result is None


def test_force_close_marks_end_of_backtest() -> None:
    simulator = _simulator()
    trade = simulator.open_trade("X.NS", datetime(2025, 1, 1), 100.0)

    closed = simulator.force_close(trade, datetime(2025, 3, 1), 103.0)

    assert closed.exit_reason == "end_of_backtest"
    assert closed.pnl == pytest.approx(3000.0)
    assert closed.return_pct == pytest.approx(3.0)
