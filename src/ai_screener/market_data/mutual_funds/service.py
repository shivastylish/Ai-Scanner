from __future__ import annotations

from datetime import datetime, time, timedelta

import pandas as pd

from ai_screener.core import get_logger
from ai_screener.market_data.mutual_funds.normalizer import FundNavNormalizer
from ai_screener.market_data.mutual_funds.provider import MFAPIProvider
from ai_screener.market_data.mutual_funds.repositories.fund_nav_repository import (
    FundNavRepository,
)

logger = get_logger(__name__)

_DATE_FORMAT = "%Y-%m-%d"


class MutualFundService:
    """Public entry point for mutual fund NAV data - the sibling to
    MarketDataService, over the sibling fund_nav schema.

    Orchestrates provider -> normalizer -> repository the same way
    MarketDataService does; there is only one provider (mfapi.in) so far,
    so it's injected directly rather than resolved through a
    registry/factory (no dispatch need yet - that machinery can be added
    if/when a second mutual fund provider shows up).
    """

    def __init__(
        self,
        provider: MFAPIProvider | None = None,
        normalizer: FundNavNormalizer | None = None,
        repository: FundNavRepository | None = None,
    ) -> None:
        self._provider = provider or MFAPIProvider()
        self._normalizer = normalizer or FundNavNormalizer()
        self._repository = repository or FundNavRepository()

    def download_history(
        self,
        scheme_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        save: bool = True,
    ) -> pd.DataFrame:
        resolved_start_date = start_date or self._resolve_incremental_start_date(
            scheme_code
        )

        logger.info(
            "Downloading NAV history for scheme %s (start=%s, end=%s)",
            scheme_code,
            resolved_start_date,
            end_date,
        )

        raw = self._provider.download_history(
            scheme_code, resolved_start_date, end_date
        )
        normalized = self._normalizer.normalize(raw, scheme_code)

        if save:
            inserted_count = self._repository.save(normalized)
            logger.info(
                "Persisted %d NAV rows for scheme %s", inserted_count, scheme_code
            )

        return normalized

    def get_history(
        self,
        scheme_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        return self._repository.get_history(
            scheme_code=scheme_code,
            start_date=_parse_date(start_date),
            end_date=_parse_date(end_date, end_of_day=True),
        )

    def get_row_count(self) -> int:
        return self._repository.count()

    def _resolve_incremental_start_date(self, scheme_code: str) -> str | None:
        latest = self._repository.get_latest_date(scheme_code)

        if latest is None:
            return None

        return (latest + timedelta(days=1)).strftime(_DATE_FORMAT)


def _parse_date(value: str | None, *, end_of_day: bool = False) -> datetime | None:
    if value is None:
        return None

    parsed = datetime.strptime(value, _DATE_FORMAT)

    if end_of_day:
        parsed = datetime.combine(parsed.date(), time(23, 59, 59))

    return parsed
