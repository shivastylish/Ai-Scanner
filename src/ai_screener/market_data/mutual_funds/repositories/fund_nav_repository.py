from __future__ import annotations

from datetime import datetime as dt_datetime

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_screener.database.models import FundNav
from ai_screener.database.session import SessionLocal, engine, initialize_database
from ai_screener.market_data.models.fund_nav_schema import FUND_NAV_STANDARD_COLUMNS

_CONFLICT_KEY_COLUMNS = ("scheme_code", "date", "provider")


class FundNavRepository:
    """Persistence adapter for mutual fund NAV history.

    Mirrors MarketDataRepository's upsert-on-conflict pattern (same
    duplicate-row problem, same fix), against the sibling fund_nav table
    instead of market_data.
    """

    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
        database_engine: Engine = engine,
    ) -> None:
        self._session_factory = session_factory
        initialize_database(database_engine)

    def save(self, df: pd.DataFrame) -> int:
        if df.empty:
            return 0

        payloads = df.to_dict("records")

        statement = sqlite_insert(FundNav).values(payloads)
        update_columns = {
            column: getattr(statement.excluded, column)
            for column in FUND_NAV_STANDARD_COLUMNS
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
        with self._session_factory() as session:
            statement = select(func.count()).select_from(FundNav)
            return session.execute(statement).scalar_one()

    def get_latest_date(self, scheme_code: str) -> dt_datetime | None:
        with self._session_factory() as session:
            statement = select(func.max(FundNav.date)).where(
                FundNav.scheme_code == scheme_code
            )
            return session.execute(statement).scalar_one_or_none()

    def get_history(
        self,
        scheme_code: str,
        start_date: dt_datetime | None = None,
        end_date: dt_datetime | None = None,
    ) -> pd.DataFrame:
        with self._session_factory() as session:
            statement = select(FundNav).where(FundNav.scheme_code == scheme_code)

            if start_date is not None:
                statement = statement.where(FundNav.date >= start_date)
            if end_date is not None:
                statement = statement.where(FundNav.date <= end_date)

            statement = statement.order_by(FundNav.date.asc())

            rows = session.execute(statement).scalars().all()

        if not rows:
            return pd.DataFrame(columns=FUND_NAV_STANDARD_COLUMNS)

        return pd.DataFrame(
            [
                {column: getattr(row, column) for column in FUND_NAV_STANDARD_COLUMNS}
                for row in rows
            ]
        )
