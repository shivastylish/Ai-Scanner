from datetime import datetime

import pandas as pd

from ai_screener.database.session import create_session_factory
from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)


def build_market_data_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": "RELIANCE.NS",
                "datetime": datetime(2025, 1, 1, 9, 15, 0),
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 108.0,
                "volume": 1200.0,
                "asset_type": "equity",
                "provider": "yahoo",
                "exchange": "NSE",
                "currency": "INR",
                "created_at": datetime(2025, 1, 1, 9, 15, 0),
                "updated_at": datetime(2025, 1, 1, 9, 15, 0),
            }
        ]
    )


def test_save_and_count_market_data() -> None:
    database_engine, session_factory = create_session_factory("sqlite:///:memory:")
    repository = MarketDataRepository(
        session_factory=session_factory,
        database_engine=database_engine,
    )

    inserted_count = repository.save(build_market_data_frame())

    assert inserted_count == 1
    assert repository.count() == 1


def test_save_empty_dataframe_returns_zero() -> None:
    database_engine, session_factory = create_session_factory("sqlite:///:memory:")
    repository = MarketDataRepository(
        session_factory=session_factory,
        database_engine=database_engine,
    )

    inserted_count = repository.save(build_market_data_frame().iloc[0:0])

    assert inserted_count == 0
    assert repository.count() == 0
