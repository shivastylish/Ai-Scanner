from datetime import datetime as dt_datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MarketData(Base):
    __tablename__ = "market_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    symbol: Mapped[str] = mapped_column(String(30), index=True)

    datetime: Mapped[dt_datetime] = mapped_column(DateTime, index=True)

    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)

    volume: Mapped[float] = mapped_column(Float)

    asset_type: Mapped[str] = mapped_column(String(20))
    provider: Mapped[str] = mapped_column(String(30))
    exchange: Mapped[str] = mapped_column(String(20))
    currency: Mapped[str] = mapped_column(String(10))

    created_at: Mapped[dt_datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=dt_datetime.utcnow,
    )
    updated_at: Mapped[dt_datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        default=dt_datetime.utcnow,
    )
