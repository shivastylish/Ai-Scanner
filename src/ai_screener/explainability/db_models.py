from __future__ import annotations

from datetime import datetime as dt_datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ai_screener.database.base import Base


class ExplanationRecord(Base):
    """Persisted "why selected" evidence for one symbol.

    Kept independent of scan_result's row id (rather than a foreign key)
    to avoid retrofitting id-plumbing into the Sprint 3 domain model;
    revisit if stronger scan-to-explanation traceability is needed later.
    """

    __tablename__ = "explanation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    symbol: Mapped[str] = mapped_column(String(30), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    reasons: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    generated_at: Mapped[dt_datetime] = mapped_column(DateTime, index=True)
