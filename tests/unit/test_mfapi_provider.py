from __future__ import annotations

import pytest

from ai_screener.market_data.mutual_funds.provider import MFAPIProvider


def test_provider_name_is_mfapi() -> None:
    assert MFAPIProvider().provider_name == "mfapi"


@pytest.mark.live
def test_download_history_reaches_live_mfapi_api() -> None:
    provider = MFAPIProvider()

    df = provider.download_history("119551")

    assert len(df) > 0
    assert set(["date", "nav", "scheme_name", "fund_house"]).issubset(df.columns)
    # Ascending by date, per the provider's documented contract.
    assert df["date"].is_monotonic_increasing


@pytest.mark.live
def test_health_check_reaches_live_mfapi_api() -> None:
    assert MFAPIProvider().health_check() is True
