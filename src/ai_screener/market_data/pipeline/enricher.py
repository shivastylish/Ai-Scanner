from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd


class MarketDataEnricher:
    """Add internal metadata."""

    @staticmethod
    def enrich(df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()

        df["created_at"] = datetime.now(UTC)
        df["updated_at"] = datetime.now(UTC)

        return df