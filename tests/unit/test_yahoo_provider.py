from __future__ import annotations

import pytest

from ai_screener.market_data.providers import ProviderRegistry
from ai_screener.market_data.providers.bootstrap import (
    register_default_providers,
)


def test_provider_registration() -> None:
    register_default_providers()

    provider = ProviderRegistry.get("equity")

    assert provider.provider_name == "yahoo"


@pytest.mark.live
def test_health_check_reaches_live_yahoo_finance() -> None:
    register_default_providers()

    provider = ProviderRegistry.get("equity")

    assert provider.health_check() is True
