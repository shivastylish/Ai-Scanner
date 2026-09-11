from __future__ import annotations

from ai_screener.market_data.services import MarketDataService


def test_pipeline_enriches_and_validates_downloaded_data(
    service: MarketDataService,
) -> None:
    df = service.download_history(
        symbol="RELIANCE.NS",
        start_date="2025-01-01",
        end_date="2025-01-10",
        save=False,
    )

    assert "created_at" in df.columns
    assert "updated_at" in df.columns

    assert len(df) > 0
