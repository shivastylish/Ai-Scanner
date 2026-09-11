"""Manual smoke check: full market data flow against the live Yahoo Finance API.

Not a pytest test (hits the network) - run directly:

    uv run python scripts/verify_yahoo_provider.py
"""

from ai_screener.market_data.providers.bootstrap import register_default_providers
from ai_screener.market_data.services import MarketDataService

register_default_providers()

service = MarketDataService()

df = service.download_history(
    symbol="RELIANCE.NS",
    asset_type="equity",
    start_date="2025-01-01",
    end_date="2025-02-01",
    save=False,
)

print(df.head())
print(df.columns.tolist())
