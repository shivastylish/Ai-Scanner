from __future__ import annotations

from fakes.fake_mfapi_provider import FakeMFAPIProvider

from ai_screener.market_data.mutual_funds.normalizer import FundNavNormalizer
from ai_screener.market_data.mutual_funds.repositories.fund_nav_repository import (
    FundNavRepository,
)
from ai_screener.market_data.mutual_funds.service import MutualFundService


def _service(repository: FundNavRepository) -> MutualFundService:
    return MutualFundService(
        provider=FakeMFAPIProvider(),
        normalizer=FundNavNormalizer(),
        repository=repository,
    )


def test_download_history_persists_when_save_enabled(
    fund_nav_repository: FundNavRepository,
) -> None:
    service = _service(fund_nav_repository)

    df = service.download_history(scheme_code="119551", start_date="2025-01-01")

    assert len(df) > 0
    assert fund_nav_repository.count() == len(df)
    assert (df["scheme_code"] == "119551").all()
    assert (df["provider"] == "mfapi").all()


def test_download_history_skips_persistence_when_save_disabled(
    fund_nav_repository: FundNavRepository,
) -> None:
    service = _service(fund_nav_repository)

    service.download_history(scheme_code="119551", start_date="2025-01-01", save=False)

    assert fund_nav_repository.count() == 0


def test_download_history_defaults_start_date_to_after_latest_stored_bar(
    fund_nav_repository: FundNavRepository,
) -> None:
    service = _service(fund_nav_repository)

    service.download_history(scheme_code="119551", start_date="2025-01-01")
    first_batch_count = fund_nav_repository.count()

    service.download_history(scheme_code="119551")

    history = service.get_history(scheme_code="119551")
    assert len(history) > first_batch_count


def test_get_history_returns_persisted_rows(
    fund_nav_repository: FundNavRepository,
) -> None:
    service = _service(fund_nav_repository)
    service.download_history(scheme_code="119551", start_date="2025-01-01")

    history = service.get_history(scheme_code="119551")

    assert len(history) > 0
    assert history["scheme_code"].unique().tolist() == ["119551"]
