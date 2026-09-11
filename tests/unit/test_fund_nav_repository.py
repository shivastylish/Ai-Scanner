from __future__ import annotations

from datetime import datetime

import pandas as pd

from ai_screener.market_data.mutual_funds.repositories.fund_nav_repository import (
    FundNavRepository,
)


def _nav_frame(*, day: int = 1, nav: float = 100.0) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scheme_code": "119551",
                "scheme_name": "Fake Fund - Direct Plan - Growth",
                "fund_house": "Fake Mutual Fund",
                "date": datetime(2025, 1, day),
                "nav": nav,
                "provider": "mfapi",
            }
        ]
    )


def test_save_and_count(fund_nav_repository: FundNavRepository) -> None:
    inserted = fund_nav_repository.save(_nav_frame())

    assert inserted == 1
    assert fund_nav_repository.count() == 1


def test_save_empty_dataframe_returns_zero(
    fund_nav_repository: FundNavRepository,
) -> None:
    assert fund_nav_repository.save(_nav_frame().iloc[0:0]) == 0


def test_save_upserts_on_conflict(fund_nav_repository: FundNavRepository) -> None:
    fund_nav_repository.save(_nav_frame(nav=100.0))
    fund_nav_repository.save(_nav_frame(nav=105.5))

    assert fund_nav_repository.count() == 1

    history = fund_nav_repository.get_history("119551")
    assert history.iloc[0]["nav"] == 105.5


def test_get_latest_date(fund_nav_repository: FundNavRepository) -> None:
    fund_nav_repository.save(_nav_frame(day=1))
    fund_nav_repository.save(_nav_frame(day=5))
    fund_nav_repository.save(_nav_frame(day=3))

    assert fund_nav_repository.get_latest_date("119551") == datetime(2025, 1, 5)


def test_get_latest_date_returns_none_when_no_data(
    fund_nav_repository: FundNavRepository,
) -> None:
    assert fund_nav_repository.get_latest_date("119551") is None


def test_get_history_orders_by_date_and_filters_by_scheme(
    fund_nav_repository: FundNavRepository,
) -> None:
    fund_nav_repository.save(_nav_frame(day=3))
    fund_nav_repository.save(_nav_frame(day=1))
    fund_nav_repository.save(_nav_frame(day=2))

    history = fund_nav_repository.get_history("119551")

    assert history["date"].tolist() == [
        datetime(2025, 1, 1),
        datetime(2025, 1, 2),
        datetime(2025, 1, 3),
    ]


def test_get_history_returns_empty_frame_for_unknown_scheme(
    fund_nav_repository: FundNavRepository,
) -> None:
    assert fund_nav_repository.get_history("999999").empty
