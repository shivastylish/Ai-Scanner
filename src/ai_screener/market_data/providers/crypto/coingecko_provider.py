from __future__ import annotations

from datetime import UTC, date, datetime

import pandas as pd
import requests

from ai_screener.core.exceptions import ProviderError
from ai_screener.market_data.providers import MarketDataProvider

_BASE_URL = "https://api.coingecko.com/api/v3"
_TIMEOUT_SECONDS = 15

# CoinGecko's free OHLC endpoint takes a lookback window ("days back
# from now"), not an arbitrary date range, and only accepts specific
# values. Pick the smallest one that covers the requested start_date.
_ALLOWED_DAYS = (1, 7, 14, 30, 90, 180, 365)


class CoinGeckoProvider(MarketDataProvider):
    """CoinGecko implementation.

    ``symbol`` is a CoinGecko coin id (e.g. "bitcoin", "ethereum") - the
    convention this provider expects, the same way YahooFinanceProvider
    expects NSE-suffixed tickers like "RELIANCE.NS".

    Scope note: CoinGecko's free OHLC endpoint does not return volume,
    only open/high/low/close. Rather than make an extra API call to a
    differently-bucketed endpoint and approximately align it by
    timestamp, volume is reported as 0.0 - a stated limitation, not a
    bug: any scanner condition that depends on volume (e.g.
    VolumeAboveAverageCondition) will not be meaningful for crypto data
    from this provider until a volume-capable provider is added.
    """

    @property
    def provider_name(self) -> str:
        return "coingecko"

    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        days = _resolve_days(start_date)

        try:
            response = requests.get(
                f"{_BASE_URL}/coins/{symbol}/ohlc",
                params={"vs_currency": "usd", "days": str(days)},
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            candles = response.json()
        except requests.RequestException as exc:
            raise ProviderError(
                f"Failed to download OHLC history for '{symbol}' from CoinGecko."
            ) from exc

        if not candles:
            raise ProviderError(f"No market data found for '{symbol}'.")

        df = pd.DataFrame(
            candles, columns=["timestamp_ms", "open", "high", "low", "close"]
        )
        df["datetime"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
        df["volume"] = 0.0

        return df[["datetime", "open", "high", "low", "close", "volume"]]

    def validate_symbol(self, symbol: str) -> bool:
        try:
            response = requests.get(
                f"{_BASE_URL}/coins/{symbol}",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "false",
                },
                timeout=_TIMEOUT_SECONDS,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{_BASE_URL}/ping", timeout=_TIMEOUT_SECONDS)
            return response.status_code == 200
        except requests.RequestException:
            return False


def _resolve_days(start_date: str | None) -> int:
    if start_date is None:
        return 30

    requested = (datetime.now(UTC).date() - _parse_date(start_date)).days

    for allowed in _ALLOWED_DAYS:
        if requested <= allowed:
            return allowed

    return _ALLOWED_DAYS[-1]


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()
