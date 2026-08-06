from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ai_screener.config import settings

db_url = settings.DATABASE_URL

if db_url.startswith("sqlite:///"):
    db_path = Path(db_url.replace("sqlite:///", ""))

    db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    db_url,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)