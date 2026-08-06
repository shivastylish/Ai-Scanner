from ai_screener.market_data.providers.equities import YahooFinanceProvider
from ai_screener.market_data.repositories.market_data_repository import (
    MarketDataRepository,
)


def test_save_market_data():

    provider = YahooFinanceProvider()

    repo = MarketDataRepository()

    df = provider.download_history(
        "RELIANCE.NS",
        "2025-01-01",
        "2025-01-05",
    )

    repo.save(df)

    assert repo.count() > 0