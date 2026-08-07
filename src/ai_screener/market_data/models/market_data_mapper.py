import pandas as pd

from .market_data_record import MarketDataRecord


class MarketDataMapper:

    @staticmethod
    def from_dataframe(df: pd.DataFrame):

        return [
            MarketDataRecord(**row)
            for row in df.to_dict("records")
        ]