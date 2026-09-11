from __future__ import annotations

from datetime import datetime as dt_datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ai_screener.database.base import Base


class JournalEntryRecord(Base):
    """One trade journal entry: entry/exit, notes, rationale, lessons
    learned, and an optional screenshot (stored on the filesystem - only
    its path is persisted here, see JournalService.settings.
    JOURNAL_SCREENSHOTS_DIR)."""

    __tablename__ = "journal_entry"

    id: Mapped[int] = mapped_column(primary_key=True)

    symbol: Mapped[str] = mapped_column(String(30), index=True)
    asset_type: Mapped[str] = mapped_column(String(20))

    entry_date: Mapped[dt_datetime] = mapped_column(DateTime)
    entry_price: Mapped[float] = mapped_column(Float)
    exit_date: Mapped[dt_datetime | None] = mapped_column(DateTime, nullable=True)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[str | None] = mapped_column(Text, nullable=True)
    screenshot_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[dt_datetime] = mapped_column(DateTime, index=True)
