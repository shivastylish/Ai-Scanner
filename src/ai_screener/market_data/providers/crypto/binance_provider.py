from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import requests

from ai_screener.core.exceptions import ProviderError
from ai_screener.market_data.providers import MarketDataProvider

_BASE_URL = "https://api.binance.com/api/v3"
_TIMEOUT_SECONDS = 15
_MAX_CANDLES = 1000  # Binance's per-request limit; no pagination in V1.


class BinanceProvider(MarketDataProvider):
    """Binance implementation.

    ``symbol`` is a Binance trading pair (e.g. "BTCUSDT") - no
    separators, matching Binance's own convention.
    """

    @property
    def provider_name(self) -> str:
        return "binance"

    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        params: dict[str, str | int] = {
            "symbol": symbol,
            "interval": "1d",
            "limit": _MAX_CANDLES,
        }
        if start_date is not None:
            params["startTime"] = _to_ms(start_date)
        if end_date is not None:
            params["endTime"] = _to_ms(end_date, end_of_day=True)

        try:
            response = requests.get(
                f"{_BASE_URL}/klines", params=params, timeout=_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            candles = response.json()
        except requests.RequestException as exc:
            raise ProviderError(
                f"Failed to download klines for '{symbol}' from Binance."
            ) from exc

        if not candles:
            raise ProviderError(f"No market data found for '{symbol}'.")

        df = pd.DataFrame(
            [row[:6] for row in candles],
            columns=["timestamp_ms", "open", "high", "low", "close", "volume"],
        )
        df["datetime"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
        for column in ("open", "high", "low", "close", "volume"):
            df[column] = df[column].astype(float)

        return df[["datetime", "open", "high", "low", "close", "volume"]]

    def validate_symbol(self, symbol: str) -> bool:
        try:
            response = requests.get(
                f"{_BASE_URL}/exchangeInfo",
                params={"symbol": symbol},
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


def _to_ms(date_str: str, *, end_of_day: bool = False) -> int:
    parsed = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
    if end_of_day:
        parsed = parsed.replace(hour=23, minute=59, second=59)
    return int(parsed.timestamp() * 1000)
