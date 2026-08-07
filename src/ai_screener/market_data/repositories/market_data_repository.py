from __future__ import annotations

import pandas as pd  # type: ignore[import-untyped]
from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_screener.database.models import MarketData
from ai_screener.database.session import SessionLocal, engine, initialize_database
from ai_screener.market_data.models.market_data_mapper import MarketDataMapper
from ai_screener.market_data.models.market_data_record import MarketDataRecord


class MarketDataRepository:
    """Persistence adapter for normalized market data records."""

    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
        database_engine: Engine = engine,
    ) -> None:
        self._session_factory = session_factory
        initialize_database(database_engine)

    def save(self, df: pd.DataFrame) -> int:
        """Persist normalized market data rows and return the inserted count."""

        records = MarketDataMapper.from_dataframe(df)
        models = [self._to_model(record) for record in records]

        if not models:
            return 0

        with self._session_factory() as session:
            session.add_all(models)
            session.commit()

        return len(models)

    def count(self) -> int:
        """Return the total number of persisted market data rows."""

        with self._session_factory() as session:
            statement = select(func.count()).select_from(MarketData)
            return session.execute(statement).scalar_one()

    @staticmethod
    def _to_model(record: MarketDataRecord) -> MarketData:
        """Map a validated record into the SQLAlchemy ORM model."""

        payload = record.model_dump(mode="python")
        return MarketData(**payload)
