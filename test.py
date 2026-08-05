from ai_screener.market_data.providers.equities import YahooFinanceProvider

provider = YahooFinanceProvider()

df = provider.download_history(
    "RELIANCE.NS",
    "2025-01-01",
    "2025-02-01",
)

print(df.head())
print(df.columns.tolist())