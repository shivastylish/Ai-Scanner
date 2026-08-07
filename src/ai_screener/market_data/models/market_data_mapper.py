import pandas as pd  # type: ignore[import-untyped]

from .market_data_record import MarketDataRecord


class MarketDataMapper:

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> list[MarketDataRecord]:

        return [
            MarketDataRecord(**row)
            for row in df.to_dict("records")
        ]
