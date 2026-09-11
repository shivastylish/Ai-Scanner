from __future__ import annotations

from datetime import datetime as dt_datetime

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_screener.database.models import MarketData
from ai_screener.database.session import SessionLocal, engine, initialize_database
from ai_screener.market_data.models.market_data_mapper import MarketDataMapper
from ai_screener.market_data.models.schema import STANDARD_COLUMNS

# Columns that identify a unique market data row and must never be
# overwritten by an upsert's "on conflict" update.
_CONFLICT_KEY_COLUMNS = ("symbol", "datetime", "asset_type", "provider")


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
        """Persist normalized market data rows, upserting on conflict.

        Re-downloading an already-stored (symbol, datetime, asset_type,
        provider) combination updates the existing row's OHLCV values
        instead of inserting a duplicate.
        """

        records = MarketDataMapper.from_dataframe(df)

        if not records:
            return 0

        payloads = [record.model_dump(mode="python") for record in records]

        statement = sqlite_insert(MarketData).values(payloads)
        update_columns = {
            column: getattr(statement.excluded, column)
            for column in payloads[0]
            if column not in _CONFLICT_KEY_COLUMNS
        }
        statement = statement.on_conflict_do_update(
            index_elements=list(_CONFLICT_KEY_COLUMNS),
            set_=update_columns,
        )

        with self._session_factory() as session:
            session.execute(statement)
            session.commit()

        return len(payloads)

    def count(self) -> int:
        """Return the total number of persisted market data rows."""

        with self._session_factory() as session:
            statement = select(func.count()).select_from(MarketData)
            return session.execute(statement).scalar_one()

    def get_latest_datetime(
        self,
        symbol: str,
        asset_type: str,
        provider: str | None = None,
    ) -> dt_datetime | None:
        """Return the most recent stored bar's datetime for a symbol, if any.

        Pass ``provider`` when more than one provider can write the same
        (symbol, asset_type) - e.g. two crypto exchanges both using
        "BTCUSDT" - so an incremental fetch for one provider isn't
        resolved against another provider's latest bar.
        """

        with self._session_factory() as session:
            statement = select(func.max(MarketData.datetime)).where(
                MarketData.symbol == symbol,
                MarketData.asset_type == asset_type,
            )
            if provider is not None:
                statement = statement.where(MarketData.provider == provider)
            return session.execute(statement).scalar_one_or_none()

    def get_history(
        self,
        symbol: str,
        asset_type: str,
        start_date: dt_datetime | None = None,
        end_date: dt_datetime | None = None,
        provider: str | None = None,
    ) -> pd.DataFrame:
        """Return persisted OHLCV history for a symbol, ordered by datetime.

        Pass ``provider`` to disambiguate when more than one provider
        might have written rows under the same (symbol, asset_type) -
        without it, rows from different providers would be merged into
        one series, which is only safe when a symbol is unique to one
        provider (true for equities today, not guaranteed once several
        crypto exchanges are registered).
        """

        with self._session_factory() as session:
            statement = select(MarketData).where(
                MarketData.symbol == symbol,
                MarketData.asset_type == asset_type,
            )

            if provider is not None:
                statement = statement.where(MarketData.provider == provider)

            if start_date is not None:
                statement = statement.where(MarketData.datetime >= start_date)

            if end_date is not None:
                statement = statement.where(MarketData.datetime <= end_date)

            statement = statement.order_by(MarketData.datetime.asc())

            rows = session.execute(statement).scalars().all()

        if not rows:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        return pd.DataFrame(
            [
                {column: getattr(row, column) for column in STANDARD_COLUMNS}
                for row in rows
            ]
        )
