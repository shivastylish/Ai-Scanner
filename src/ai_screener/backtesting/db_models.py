from __future__ import annotations

from datetime import datetime as dt_datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_screener.database.base import Base


class BacktestRun(Base):
    """One execution of a strategy backtest over a date range/universe."""

    __tablename__ = "backtest_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    strategy_name: Mapped[str] = mapped_column(String(100), index=True)
    asset_type: Mapped[str] = mapped_column(String(20))
    start_date: Mapped[str] = mapped_column(String(10))
    end_date: Mapped[str] = mapped_column(String(10))

    total_trades: Mapped[int] = mapped_column(Integer)
    win_rate_pct: Mapped[float] = mapped_column(Float)
    average_return_pct: Mapped[float] = mapped_column(Float)
    total_pnl: Mapped[float] = mapped_column(Float)
    max_drawdown_pct: Mapped[float] = mapped_column(Float)

    run_at: Mapped[dt_datetime] = mapped_column(DateTime, index=True)

    trades: Mapped[list[BacktestTrade]] = relationship(
        back_populates="backtest_run", cascade="all, delete-orphan"
    )


class BacktestTrade(Base):
    """One simulated trade within a BacktestRun."""

    __tablename__ = "backtest_trade"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    backtest_run_id: Mapped[int] = mapped_column(
        ForeignKey("backtest_run.id"), index=True
    )

    symbol: Mapped[str] = mapped_column(String(30), index=True)
    entry_date: Mapped[dt_datetime] = mapped_column(DateTime)
    entry_price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[float] = mapped_column(Float)
    exit_date: Mapped[dt_datetime] = mapped_column(DateTime)
    exit_price: Mapped[float] = mapped_column(Float)
    exit_reason: Mapped[str] = mapped_column(String(30))
    pnl: Mapped[float] = mapped_column(Float)
    return_pct: Mapped[float] = mapped_column(Float)

    backtest_run: Mapped[BacktestRun] = relationship(back_populates="trades")
