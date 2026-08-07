from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_screener.config import settings
from ai_screener.database.base import Base

db_url = settings.DATABASE_URL

if db_url.startswith("sqlite:///"):
    db_path = Path(db_url.replace("sqlite:///", ""))

    db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    db_url,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker[Session](
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def create_session_factory(database_url: str) -> tuple[Engine, sessionmaker[Session]]:
    """Create an engine and typed session factory for a database URL."""

    if database_url.startswith("sqlite:///"):
        db_path = Path(database_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    database_engine = create_engine(
        database_url,
        echo=False,
        future=True,
    )

    factory = sessionmaker[Session](
        bind=database_engine,
        class_=Session,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    return database_engine, factory


def initialize_database(database_engine: Engine) -> None:
    """Create all configured tables for the provided engine."""

    Base.metadata.create_all(bind=database_engine)
