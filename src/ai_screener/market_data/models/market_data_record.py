from datetime import datetime as dt_datetime

from pydantic import BaseModel

from .schema import AssetType


class MarketDataRecord(BaseModel):
    symbol: str

    datetime: dt_datetime

    open: float
    high: float
    low: float
    close: float

    volume: float

    asset_type: AssetType

    provider: str
    exchange: str
    currency: str

    created_at: dt_datetime
    updated_at: dt_datetime
