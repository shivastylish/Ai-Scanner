from __future__ import annotations

from datetime import datetime as dt_datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from ai_screener.database.base import Base


class HoldingRecord(Base):
    """A currently open position: symbol, quantity, and weighted-average
    cost. One row per (symbol, asset_type) - closing a position entirely
    removes its row (see PortfolioRepository.record_sell)."""

    __tablename__ = "holding"

    id: Mapped[int] = mapped_column(primary_key=True)

    symbol: Mapped[str] = mapped_column(String(30), index=True)
    asset_type: Mapped[str] = mapped_column(String(20))

    quantity: Mapped[float] = mapped_column(Float)
    average_cost: Mapped[float] = mapped_column(Float)

    opened_at: Mapped[dt_datetime] = mapped_column(DateTime)
    updated_at: Mapped[dt_datetime] = mapped_column(DateTime)


class TransactionRecord(Base):
    """Audit trail of every buy/sell behind a holding's quantity and
    average cost - and the source of realized P&L, recorded on "sell"
    transactions."""

    __tablename__ = "portfolio_transaction"

    id: Mapped[int] = mapped_column(primary_key=True)

    symbol: Mapped[str] = mapped_column(String(30), index=True)
    asset_type: Mapped[str] = mapped_column(String(20))
    transaction_type: Mapped[str] = mapped_column(String(10))  # "buy" | "sell"

    quantity: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    realized_pnl: Mapped[float | None] = mapped_column(Float, nullable=True)

    transacted_at: Mapped[dt_datetime] = mapped_column(DateTime, index=True)
