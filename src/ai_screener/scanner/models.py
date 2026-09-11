from __future__ import annotations

from datetime import datetime as dt_datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_screener.database.base import Base


class ScanRun(Base):
    """One execution of a scan strategy over a universe of symbols."""

    __tablename__ = "scan_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    strategy_name: Mapped[str] = mapped_column(String(100), index=True)
    asset_type: Mapped[str] = mapped_column(String(20))
    universe_size: Mapped[int] = mapped_column(Integer)

    started_at: Mapped[dt_datetime] = mapped_column(DateTime, index=True)
    completed_at: Mapped[dt_datetime] = mapped_column(DateTime)

    results: Mapped[list[ScanResultRecord]] = relationship(
        back_populates="scan_run", cascade="all, delete-orphan"
    )


class ScanResultRecord(Base):
    """One symbol's outcome within a ScanRun.

    ``condition_results`` stores the full list of structured
    ConditionResult evidence (not just pass/fail) as JSON, so downstream
    consumers (ranking, explainability, dashboard) have the full "why"
    without re-running the scan.
    """

    __tablename__ = "scan_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    scan_run_id: Mapped[int] = mapped_column(ForeignKey("scan_run.id"), index=True)

    symbol: Mapped[str] = mapped_column(String(30), index=True)
    passed: Mapped[bool] = mapped_column(Boolean, index=True)
    condition_results: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    scanned_at: Mapped[dt_datetime] = mapped_column(DateTime)

    scan_run: Mapped[ScanRun] = relationship(back_populates="results")
