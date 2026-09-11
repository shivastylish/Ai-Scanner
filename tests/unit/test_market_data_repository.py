from __future__ import annotations

from datetime import datetime

import pandas as pd

from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)


def build_market_data_frame(*, day: int = 1, close: float = 108.0) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": "RELIANCE.NS",
                "datetime": datetime(2025, 1, day, 9, 15, 0),
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": close,
                "volume": 1200.0,
                "asset_type": "equity",
                "provider": "yahoo",
                "exchange": "NSE",
                "currency": "INR",
                "created_at": datetime(2025, 1, day, 9, 15, 0),
                "updated_at": datetime(2025, 1, day, 9, 15, 0),
            }
        ]
    )


def test_save_and_count_market_data(repository: MarketDataRepository) -> None:
    inserted_count = repository.save(build_market_data_frame())

    assert inserted_count == 1
    assert repository.count() == 1


def test_save_empty_dataframe_returns_zero(
    repository: MarketDataRepository,
) -> None:
    inserted_count = repository.save(build_market_data_frame().iloc[0:0])

    assert inserted_count == 0
    assert repository.count() == 0


def test_save_upserts_on_conflict_instead_of_duplicating(
    repository: MarketDataRepository,
) -> None:
    """Re-saving the same (symbol, datetime, asset_type, provider) updates
    the existing row's values instead of inserting a duplicate."""

    repository.save(build_market_data_frame(close=108.0))
    repository.save(build_market_data_frame(close=250.0))

    assert repository.count() == 1

    history = repository.get_history(symbol="RELIANCE.NS", asset_type="equity")
    assert history.iloc[0]["close"] == 250.0


def test_get_latest_datetime_returns_none_when_no_data(
    repository: MarketDataRepository,
) -> None:
    assert repository.get_latest_datetime("RELIANCE.NS", "equity") is None


def test_get_latest_datetime_returns_most_recent_bar(
    repository: MarketDataRepository,
) -> None:
    repository.save(build_market_data_frame(day=1))
    repository.save(build_market_data_frame(day=5))
    repository.save(build_market_data_frame(day=3))

    latest = repository.get_latest_datetime("RELIANCE.NS", "equity")

    assert latest == datetime(2025, 1, 5, 9, 15, 0)


def test_get_history_returns_rows_ordered_by_datetime(
    repository: MarketDataRepository,
) -> None:
    repository.save(build_market_data_frame(day=3))
    repository.save(build_market_data_frame(day=1))
    repository.save(build_market_data_frame(day=2))

    history = repository.get_history(symbol="RELIANCE.NS", asset_type="equity")

    assert history["datetime"].tolist() == [
        datetime(2025, 1, 1, 9, 15, 0),
        datetime(2025, 1, 2, 9, 15, 0),
        datetime(2025, 1, 3, 9, 15, 0),
    ]


def test_get_history_respects_date_range(
    repository: MarketDataRepository,
) -> None:
    for day in (1, 2, 3, 4, 5):
        repository.save(build_market_data_frame(day=day))

    history = repository.get_history(
        symbol="RELIANCE.NS",
        asset_type="equity",
        start_date=datetime(2025, 1, 2),
        end_date=datetime(2025, 1, 4, 23, 59, 59),
    )

    assert history["datetime"].tolist() == [
        datetime(2025, 1, 2, 9, 15, 0),
        datetime(2025, 1, 3, 9, 15, 0),
        datetime(2025, 1, 4, 9, 15, 0),
    ]


def test_get_history_returns_empty_frame_for_unknown_symbol(
    repository: MarketDataRepository,
) -> None:
    history = repository.get_history(symbol="UNKNOWN.NS", asset_type="equity")

    assert history.empty
