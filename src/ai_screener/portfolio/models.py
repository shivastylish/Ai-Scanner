from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Holding:
    symbol: str
    asset_type: str
    quantity: float
    average_cost: float
    opened_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Transaction:
    symbol: str
    asset_type: str
    transaction_type: str  # "buy" | "sell"
    quantity: float
    price: float
    realized_pnl: float | None
    transacted_at: datetime


@dataclass(frozen=True)
class HoldingValuation:
    """A Holding priced against the latest known market data."""

    symbol: str
    asset_type: str
    quantity: float
    average_cost: float
    current_price: float | None
    market_value: float | None
    unrealized_pnl: float | None
    unrealized_pnl_pct: float | None
