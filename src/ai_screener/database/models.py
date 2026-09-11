from datetime import UTC
from datetime import datetime as dt_datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MarketData(Base):
    __tablename__ = "market_data"
    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "datetime",
            "asset_type",
            "provider",
            name="uq_market_data_symbol_datetime_asset_type_provider",
        ),
    )

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
        default=lambda: dt_datetime.now(UTC),
    )
    updated_at: Mapped[dt_datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: dt_datetime.now(UTC),
    )


class FundNav(Base):
    """A mutual fund scheme's NAV on one day - the sibling schema to
    MarketData (see market_data/models/fund_nav_schema.py for why NAV
    doesn't fit the OHLCV shape)."""

    __tablename__ = "fund_nav"
    __table_args__ = (
        UniqueConstraint(
            "scheme_code",
            "date",
            "provider",
            name="uq_fund_nav_scheme_code_date_provider",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    scheme_code: Mapped[str] = mapped_column(String(20), index=True)
    scheme_name: Mapped[str] = mapped_column(String(255))
    fund_house: Mapped[str] = mapped_column(String(255))

    date: Mapped[dt_datetime] = mapped_column(DateTime, index=True)
    nav: Mapped[float] = mapped_column(Float)
    provider: Mapped[str] = mapped_column(String(30))

    # Not available from mfapi.in's free API; kept nullable so a future
    # provider/enrichment source can populate them without a schema
    # change.
    expense_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    aum: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[dt_datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=lambda: dt_datetime.now(UTC),
    )
    updated_at: Mapped[dt_datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: dt_datetime.now(UTC),
    )
