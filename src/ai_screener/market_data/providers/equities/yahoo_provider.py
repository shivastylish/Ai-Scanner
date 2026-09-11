from __future__ import annotations

import pandas as pd
import yfinance as yf

from ai_screener.core.exceptions import ProviderError
from ai_screener.market_data.providers import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance implementation.

    Responsible only for fetching raw historical data from Yahoo Finance.
    Normalization, validation, and enrichment are handled by the
    Normalizer and Pipeline layers, orchestrated by the MarketDataService.
    """

    @property
    def provider_name(self) -> str:
        return "yahoo"

    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        try:
            ticker = yf.Ticker(symbol)

            df: pd.DataFrame = ticker.history(
                start=start_date,
                end=end_date,
                auto_adjust=False,
                actions=True,
            )
        except Exception as exc:  # pragma: no cover - network/library errors
            raise ProviderError(
                f"Failed to download history for '{symbol}' from Yahoo Finance."
            ) from exc

        if df.empty:
            raise ProviderError(f"No market data found for '{symbol}'.")

        return df.reset_index()

    def validate_symbol(self, symbol: str) -> bool:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            return bool(info)
        except Exception:
            return False

    def health_check(self) -> bool:
        try:
            ticker = yf.Ticker("^NSEI")
            df = ticker.history(period="5d")
            return not df.empty
        except Exception:
            return False
