import pandas as pd

from .market_data_record import MarketDataRecord


class MarketDataMapper:

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> list[MarketDataRecord]:

        return [MarketDataRecord.model_validate(row) for row in df.to_dict("records")]
