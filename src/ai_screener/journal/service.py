from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from ai_screener.config.settings import settings
from ai_screener.core.exceptions import ValidationError
from ai_screener.journal.models import JournalEntry
from ai_screener.journal.repositories.journal_repository import JournalRepository


class JournalService:
    """Orchestrates trade-journal CRUD (via JournalRepository) plus the
    one piece of extra behavior that doesn't belong in the repository:
    copying a screenshot file into the configured storage directory
    (settings.JOURNAL_SCREENSHOTS_DIR) before recording its path."""

    def __init__(self, repository: JournalRepository | None = None) -> None:
        self._repository = repository or JournalRepository()

    def add_entry(
        self,
        symbol: str,
        entry_price: float,
        asset_type: str = "equity",
        entry_date: datetime | None = None,
        rationale: str | None = None,
        notes: str | None = None,
    ) -> JournalEntry:
        return self._repository.create_entry(
            symbol=symbol,
            asset_type=asset_type,
            entry_date=entry_date or datetime.now(UTC),
            entry_price=entry_price,
            rationale=rationale,
            notes=notes,
        )

    def close_entry(
        self,
        entry_id: int,
        exit_price: float,
        exit_date: datetime | None = None,
        lessons_learned: str | None = None,
    ) -> JournalEntry | None:
        return self._repository.close_entry(
            entry_id=entry_id,
            exit_date=exit_date or datetime.now(UTC),
            exit_price=exit_price,
            lessons_learned=lessons_learned,
        )

    def update_notes(self, entry_id: int, notes: str) -> JournalEntry | None:
        return self._repository.update_notes(entry_id, notes)

    def attach_screenshot(self, entry_id: int, source_path: str) -> JournalEntry:
        """Copy a screenshot file into JOURNAL_SCREENSHOTS_DIR and record
        its stored path against the entry."""

        source = Path(source_path)

        if not source.is_file():
            raise ValidationError(f"Screenshot file not found: '{source_path}'.")

        destination_dir = Path(settings.JOURNAL_SCREENSHOTS_DIR)
        destination_dir.mkdir(parents=True, exist_ok=True)

        destination = destination_dir / f"entry_{entry_id}_{source.name}"
        shutil.copyfile(source, destination)

        entry = self._repository.attach_screenshot(entry_id, str(destination))

        if entry is None:
            raise ValidationError(f"No journal entry with id {entry_id}.")

        return entry

    def get_entry(self, entry_id: int) -> JournalEntry | None:
        return self._repository.get_entry(entry_id)

    def list_entries(self, symbol: str | None = None) -> list[JournalEntry]:
        return self._repository.list_entries(symbol)

    def delete_entry(self, entry_id: int) -> bool:
        return self._repository.delete_entry(entry_id)
