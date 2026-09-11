from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd


class FakeMFAPIProvider:
    """Deterministic, network-free stand-in for MFAPIProvider.

    Returns data shaped exactly like MFAPIProvider.download_history()'s
    output ("date"/"nav"/"scheme_name"/"fund_house" columns, ascending by
    date), so it can flow through the real FundNavNormalizer ->
    Repository in tests without touching the network.
    """

    def __init__(self, num_days: int = 5) -> None:
        self._num_days = num_days

    def download_history(
        self,
        scheme_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        start = (
            datetime.strptime(start_date, "%Y-%m-%d")
            if start_date
            else datetime(2025, 1, 1)
        )

        rows = [
            {
                "date": start + timedelta(days=i),
                "nav": 100.0 + i,
                "scheme_name": "Fake Fund - Direct Plan - Growth",
                "fund_house": "Fake Mutual Fund",
            }
            for i in range(self._num_days)
        ]

        return pd.DataFrame(rows)

    def health_check(self) -> bool:
        return True
