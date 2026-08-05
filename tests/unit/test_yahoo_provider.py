from ai_screener.market_data.providers.bootstrap import (
    register_default_providers,
)
from ai_screener.market_data.providers import ProviderRegistry


def test_provider_registration():
    register_default_providers()

    provider = ProviderRegistry.get("equity")

    assert provider.provider_name == "yahoo"


def test_health_check():
    register_default_providers()

    provider = ProviderRegistry.get("equity")

    assert provider.health_check() is True