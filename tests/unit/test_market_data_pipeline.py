from ai_screener.market_data.providers.equities import (
    YahooFinanceProvider,
)


def test_pipeline():

    provider = YahooFinanceProvider()

    df = provider.download_history(
        "RELIANCE.NS",
        "2025-01-01",
        "2025-01-10",
    )

    assert "created_at" in df.columns
    assert "updated_at" in df.columns

    assert len(df) > 0