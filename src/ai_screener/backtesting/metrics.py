from __future__ import annotations

from dataclasses import dataclass

from ai_screener.backtesting.simulator import Trade


@dataclass(frozen=True)
class BacktestMetrics:
    total_trades: int
    win_rate_pct: float
    average_return_pct: float
    total_pnl: float
    max_drawdown_pct: float


def compute_metrics(trades: list[Trade]) -> BacktestMetrics:
    closed = [t for t in trades if t.pnl is not None]

    if not closed:
        return BacktestMetrics(
            total_trades=0,
            win_rate_pct=0.0,
            average_return_pct=0.0,
            total_pnl=0.0,
            max_drawdown_pct=0.0,
        )

    wins = [t for t in closed if (t.pnl or 0) > 0]

    return BacktestMetrics(
        total_trades=len(closed),
        win_rate_pct=round(len(wins) / len(closed) * 100, 2),
        average_return_pct=round(
            sum(t.return_pct or 0.0 for t in closed) / len(closed), 4
        ),
        total_pnl=round(sum(t.pnl or 0.0 for t in closed), 2),
        max_drawdown_pct=round(_max_drawdown_pct(closed), 2),
    )


def _max_drawdown_pct(closed_trades: list[Trade]) -> float:
    """Max drawdown of the cumulative-PnL curve built from trades in
    exit order, as a percentage of the running peak.

    A simplification: this tracks cumulative realized PnL across trades,
    not a continuous equity curve against total deployed capital -
    reasonable for a V1 backtester, revisit if a true equity-curve
    drawdown is needed later.
    """

    ordered = sorted(closed_trades, key=lambda t: t.exit_date or t.entry_date)

    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0

    for trade in ordered:
        equity += trade.pnl or 0.0
        peak = max(peak, equity)

        if peak > 0:
            drawdown_pct = (peak - equity) / peak * 100
            max_drawdown = max(max_drawdown, drawdown_pct)

    return max_drawdown
