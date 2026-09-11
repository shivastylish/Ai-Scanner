from __future__ import annotations

import dataclasses

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_screener.database.session import SessionLocal, engine, initialize_database
from ai_screener.explainability.db_models import ExplanationRecord
from ai_screener.explainability.models import Explanation, Reason


class ExplanationRepository:
    """Persistence adapter for generated explanations."""

    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
        database_engine: Engine = engine,
    ) -> None:
        self._session_factory = session_factory
        initialize_database(database_engine)

    def save(self, explanation: Explanation) -> int:
        """Persist an explanation. Returns the new row id."""

        record = ExplanationRecord(
            symbol=explanation.symbol,
            confidence=explanation.confidence,
            reasons=[dataclasses.asdict(reason) for reason in explanation.reasons],
            generated_at=explanation.generated_at,
        )

        with self._session_factory() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record.id

    def get_latest(self, symbol: str) -> Explanation | None:
        """Return the most recently generated explanation for a symbol."""

        with self._session_factory() as session:
            record = session.execute(
                select(ExplanationRecord)
                .where(ExplanationRecord.symbol == symbol)
                .order_by(ExplanationRecord.generated_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if record is None:
                return None

            return _to_explanation(record)


def _to_explanation(record: ExplanationRecord) -> Explanation:
    return Explanation(
        symbol=record.symbol,
        reasons=[Reason(**reason) for reason in record.reasons],
        confidence=record.confidence,
        generated_at=record.generated_at,
    )
