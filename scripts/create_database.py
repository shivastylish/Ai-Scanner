"""Convenience script for local/dev database bootstrap.

Schema changes should be made through Alembic migrations
(``alembic revision --autogenerate`` + ``alembic upgrade head``), which is
the source of truth for the database schema. This script remains as a
quick way to stand up a throwaway database (e.g. for manual smoke checks)
without running migrations, but it will not apply future schema changes
tracked only as Alembic revisions.
"""

import ai_screener.database.models  # noqa: F401
from ai_screener.database.base import Base
from ai_screener.database.session import engine

Base.metadata.create_all(engine)

print("Database created successfully.")
