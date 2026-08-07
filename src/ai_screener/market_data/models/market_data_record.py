from datetime import datetime

from pydantic import BaseModel

from .schema import AssetType


class MarketDataRecord(BaseModel):
    symbol: str

    datetime: datetime

    open: float
    high: float
    low: float
    close: float

    volume: float

    asset_type: AssetType

    provider: str
    exchange: str
    currency: str

    created_at: datetime
    updated_at: datetime