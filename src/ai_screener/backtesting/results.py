from __future__ import annotations

from dataclasses import dataclass

from ai_screener.backtesting.metrics import BacktestMetrics
from ai_screener.backtesting.simulator import Trade


@dataclass(frozen=True)
class BacktestResult:
    strategy_name: str
    asset_type: str
    start_date: str
    end_date: str
    trades: list[Trade]
    metrics: BacktestMetrics
