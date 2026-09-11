from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_screener.database.session import SessionLocal, engine, initialize_database
from ai_screener.journal.db_models import JournalEntryRecord
from ai_screener.journal.models import JournalEntry


class JournalRepository:
    """Persistence adapter for trade journal entries."""

    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
        database_engine: Engine = engine,
    ) -> None:
        self._session_factory = session_factory
        initialize_database(database_engine)

    def create_entry(
        self,
        symbol: str,
        asset_type: str,
        entry_date: datetime,
        entry_price: float,
        rationale: str | None = None,
        notes: str | None = None,
    ) -> JournalEntry:
        with self._session_factory() as session:
            record = JournalEntryRecord(
                symbol=symbol,
                asset_type=asset_type,
                entry_date=entry_date,
                entry_price=entry_price,
                rationale=rationale,
                notes=notes,
                created_at=datetime.now(UTC),
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return _to_journal_entry(record)

    def close_entry(
        self,
        entry_id: int,
        exit_date: datetime,
        exit_price: float,
        lessons_learned: str | None = None,
    ) -> JournalEntry | None:
        with self._session_factory() as session:
            record = session.get(JournalEntryRecord, entry_id)

            if record is None:
                return None

            record.exit_date = exit_date
            record.exit_price = exit_price
            if lessons_learned is not None:
                record.lessons_learned = lessons_learned

            session.commit()
            session.refresh(record)
            return _to_journal_entry(record)

    def update_notes(self, entry_id: int, notes: str) -> JournalEntry | None:
        with self._session_factory() as session:
            record = session.get(JournalEntryRecord, entry_id)

            if record is None:
                return None

            record.notes = notes
            session.commit()
            session.refresh(record)
            return _to_journal_entry(record)

    def attach_screenshot(
        self, entry_id: int, screenshot_path: str
    ) -> JournalEntry | None:
        with self._session_factory() as session:
            record = session.get(JournalEntryRecord, entry_id)

            if record is None:
                return None

            record.screenshot_path = screenshot_path
            session.commit()
            session.refresh(record)
            return _to_journal_entry(record)

    def get_entry(self, entry_id: int) -> JournalEntry | None:
        with self._session_factory() as session:
            record = session.get(JournalEntryRecord, entry_id)
            return None if record is None else _to_journal_entry(record)

    def list_entries(self, symbol: str | None = None) -> list[JournalEntry]:
        with self._session_factory() as session:
            statement = select(JournalEntryRecord).order_by(
                JournalEntryRecord.entry_date.desc()
            )
            if symbol is not None:
                statement = statement.where(JournalEntryRecord.symbol == symbol)
            records = session.execute(statement).scalars().all()
            return [_to_journal_entry(record) for record in records]

    def delete_entry(self, entry_id: int) -> bool:
        with self._session_factory() as session:
            record = session.get(JournalEntryRecord, entry_id)

            if record is None:
                return False

            session.delete(record)
            session.commit()
            return True


def _to_journal_entry(record: JournalEntryRecord) -> JournalEntry:
    return JournalEntry(
        id=record.id,
        symbol=record.symbol,
        asset_type=record.asset_type,
        entry_date=record.entry_date,
        entry_price=record.entry_price,
        exit_date=record.exit_date,
        exit_price=record.exit_price,
        notes=record.notes,
        rationale=record.rationale,
        lessons_learned=record.lessons_learned,
        screenshot_path=record.screenshot_path,
        created_at=record.created_at,
    )
