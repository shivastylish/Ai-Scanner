import pandas as pd

from ai_screener.database.models import MarketData
from ai_screener.database.session import SessionLocal


class MarketDataRepository:

    def save(self, df: pd.DataFrame):

        with SessionLocal() as session:

            for row in df.to_dict("records"):

                session.add(
                    MarketData(**row)
                )

            session.commit()

    def count(self):

        with SessionLocal() as session:

            return session.query(MarketData).count()