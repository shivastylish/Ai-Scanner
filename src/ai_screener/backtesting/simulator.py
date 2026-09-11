from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from datetime import datetime

from ai_screener.backtesting.config import BacktestConfig


@dataclass(frozen=True)
class Trade:
    """One simulated position, open or closed.

    ``pnl``/``return_pct``/``exit_*`` are None while the trade is open.
    """

    symbol: str
    entry_date: datetime
    entry_price: float
    quantity: float
    exit_date: datetime | None = None
    exit_price: float | None = None
    exit_reason: str | None = None
    pnl: float | None = None
    return_pct: float | None = None

    @property
    def is_open(self) -> bool:
        return self.exit_date is None


class TradeSimulator:
    """Applies BacktestConfig's stated entry/exit rules to one symbol's
    trades. Stateless with respect to any particular trade - callers
    (BacktestEngine) hold the "is a trade currently open for this
    symbol" state themselves.
    """

    def __init__(self, config: BacktestConfig | None = None) -> None:
        self._config = config or BacktestConfig()

    def open_trade(
        self, symbol: str, entry_date: datetime, entry_price: float
    ) -> Trade:
        quantity = self._config.capital_per_trade / entry_price
        return Trade(
            symbol=symbol,
            entry_date=entry_date,
            entry_price=entry_price,
            quantity=quantity,
        )

    def check_exit(
        self,
        trade: Trade,
        current_date: datetime,
        current_high: float,
        current_low: float,
        current_close: float,
        days_held: int,
    ) -> Trade | None:
        """Return a closed Trade if an exit condition triggers today,
        else None (the trade stays open)."""

        stop_price = trade.entry_price * (1 - self._config.stop_loss_pct)
        target_price = trade.entry_price * (1 + self._config.take_profit_pct)

        # Stop-loss checked first: the conservative assumption when both
        # the stop and the target fall within the same day's high/low
        # range and there's no way to know which was actually hit first.
        if current_low <= stop_price:
            return self._close(trade, current_date, stop_price, "stop_loss")

        if current_high >= target_price:
            return self._close(trade, current_date, target_price, "take_profit")

        if days_held >= self._config.max_holding_days:
            return self._close(trade, current_date, current_close, "max_holding_period")

        return None

    def force_close(
        self, trade: Trade, current_date: datetime, current_close: float
    ) -> Trade:
        """Close a trade still open at the end of the backtest window."""

        return self._close(trade, current_date, current_close, "end_of_backtest")

    @staticmethod
    def _close(
        trade: Trade, exit_date: datetime, exit_price: float, reason: str
    ) -> Trade:
        pnl = (exit_price - trade.entry_price) * trade.quantity
        return_pct = (exit_price - trade.entry_price) / trade.entry_price * 100

        return dataclasses.replace(
            trade,
            exit_date=exit_date,
            exit_price=exit_price,
            exit_reason=reason,
            pnl=round(pnl, 2),
            return_pct=round(return_pct, 4),
        )
