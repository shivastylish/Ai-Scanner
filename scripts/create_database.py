from ai_screener.database.base import Base
from ai_screener.database.session import engine

import ai_screener.database.models

Base.metadata.create_all(engine)

print("Database created successfully.")