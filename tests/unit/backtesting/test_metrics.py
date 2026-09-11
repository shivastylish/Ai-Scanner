from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from ai_screener.backtesting.metrics import compute_metrics
from ai_screener.backtesting.simulator import Trade


def _closed_trade(
    day: int, pnl: float, return_pct: float, entry_price: float = 100.0
) -> Trade:
    exit_date = datetime(2025, 1, 1) + timedelta(days=day - 1)

    return Trade(
        symbol="X.NS",
        entry_date=exit_date - timedelta(days=1),
        entry_price=entry_price,
        quantity=100.0,
        exit_date=exit_date,
        exit_price=entry_price + return_pct,
        exit_reason="take_profit" if pnl > 0 else "stop_loss",
        pnl=pnl,
        return_pct=return_pct,
    )


def test_compute_metrics_on_empty_trades() -> None:
    metrics = compute_metrics([])

    assert metrics.total_trades == 0
    assert metrics.win_rate_pct == 0.0
    assert metrics.average_return_pct == 0.0
    assert metrics.total_pnl == 0.0
    assert metrics.max_drawdown_pct == 0.0


def test_compute_metrics_hand_verified() -> None:
    trades = [
        _closed_trade(1, 1000.0, 5.0),
        _closed_trade(2, -500.0, -2.0),
        _closed_trade(3, 2000.0, 8.0),
        _closed_trade(4, -1000.0, -3.0),
    ]

    metrics = compute_metrics(trades)

    assert metrics.total_trades == 4
    assert metrics.win_rate_pct == pytest.approx(50.0)
    assert metrics.average_return_pct == pytest.approx(2.0)
    assert metrics.total_pnl == pytest.approx(1500.0)
    # Equity curve: 1000 -> 500 (peak 1000, dd 50%) -> 2500 -> 1500 (peak
    # 2500, dd 40%). Worst drawdown is the 50% dip after trade 2.
    assert metrics.max_drawdown_pct == pytest.approx(50.0)


def test_compute_metrics_excludes_open_trades() -> None:
    open_trade = Trade(
        symbol="Y.NS",
        entry_date=datetime(2025, 1, 1),
        entry_price=100.0,
        quantity=10.0,
    )
    closed = _closed_trade(2, 500.0, 5.0)

    metrics = compute_metrics([open_trade, closed])

    assert metrics.total_trades == 1
    assert metrics.total_pnl == pytest.approx(500.0)
