from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class JournalEntry:
    id: int
    symbol: str
    asset_type: str
    entry_date: datetime
    entry_price: float
    exit_date: datetime | None
    exit_price: float | None
    notes: str | None
    rationale: str | None
    lessons_learned: str | None
    screenshot_path: str | None
    created_at: datetime

    @property
    def is_closed(self) -> bool:
        return self.exit_date is not None
