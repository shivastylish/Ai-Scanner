from __future__ import annotations

from dataclasses import dataclass


#: Trade-simulation rules. None of this is specified anywhere in the
#: product docs (PRD/HLD/LLD/ADRs) - these are stated, documented
#: defaults so backtesting can actually run, not a settled product
#: decision. Revisit with the user before treating any of this as final:
#:
#: - Long-only, one position per symbol at a time (no pyramiding).
#: - Entry: the day *after* a passing scan, at that day's open - never
#:   the scan day's own close, which would be look-ahead (you can't
#:   actually trade at a price you only knew after the bar closed).
#: - Position size: a fixed notional amount per trade (not a shared,
#:   compounding capital pool across symbols/trades) - the simplest
#:   sizing model, deliberately not modeling portfolio-level capital
#:   allocation or trade ordering across symbols yet.
#: - Exit: stop-loss OR take-profit (whichever is hit first intraday;
#:   stop-loss wins on an ambiguous same-bar hit of both, the
#:   conservative assumption) OR a maximum holding period, whichever
#:   comes first.
#: - No commissions or slippage modeled.
@dataclass(frozen=True)
class BacktestConfig:
    capital_per_trade: float = 100_000.0
    stop_loss_pct: float = 0.05
    take_profit_pct: float = 0.10
    max_holding_days: int = 20
