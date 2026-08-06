from ai_screener.market_data.providers.bootstrap import (
    register_default_providers,
)
from ai_screener.market_data.services import (
    MarketDataService,
)


def test_download_and_save():

    register_default_providers()

    service = MarketDataService()

    df = service.download(
        symbol="RELIANCE.NS",
        start_date="2025-01-01",
        end_date="2025-01-10",
    )

    assert len(df) > 0

    assert service.get_row_count() > 0