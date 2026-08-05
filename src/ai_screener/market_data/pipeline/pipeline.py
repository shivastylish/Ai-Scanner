from __future__ import annotations

import pandas as pd

from .enricher import MarketDataEnricher
from .validator import MarketDataValidator


class MarketDataPipeline:

    @staticmethod
    def process(df: pd.DataFrame) -> pd.DataFrame:

        df = MarketDataValidator.validate(df)

        df = MarketDataEnricher.enrich(df)

        return df