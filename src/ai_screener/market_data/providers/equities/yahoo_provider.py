from __future__ import annotations

import pandas as pd
from sqlalchemy.util import symbol
import yfinance as yf

from ai_screener.market_data.normalization.yahoo_normalizer import YahooNormalizer
from ai_screener.market_data.providers import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance implementation."""

    @property
    def provider_name(self) -> str:
        return "yahoo"

    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:

        ticker = yf.Ticker(symbol)

        df = ticker.history(
            start=start_date,
            end=end_date,
            auto_adjust=False,
            actions=True,
        )

        if df.empty:
            raise ValueError(f"No market data found for '{symbol}'")

        df = df.reset_index()

        from ai_screener.market_data.normalization.yahoo_normalizer import (YahooNormalizer,)

        normalizer = YahooNormalizer()

        return normalizer.normalize(df, symbol)

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