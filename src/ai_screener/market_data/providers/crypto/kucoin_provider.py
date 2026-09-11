from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import requests

from ai_screener.core.exceptions import ProviderError
from ai_screener.market_data.providers import MarketDataProvider

_BASE_URL = "https://api.kucoin.com/api/v1"
_TIMEOUT_SECONDS = 15


class KuCoinProvider(MarketDataProvider):
    """KuCoin implementation.

    ``symbol`` is a KuCoin spot trading pair (e.g. "BTC-USDT", hyphenated
    - unlike Binance/Bybit's unseparated convention).

    KuCoin's candle array order is
    ``[time, open, close, high, low, volume, turnover]`` - close comes
    *before* high/low, unlike the OHLC order every other provider here
    uses. Get this column mapping wrong and every bar's close and high
    silently swap - the values still look plausible, so this is worth
    flagging explicitly rather than trusting the visual column order in
    the raw response.
    """

    @property
    def provider_name(self) -> str:
        return "kucoin"

    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        params: dict[str, str | int] = {"type": "1day", "symbol": symbol}
        if start_date is not None:
            params["startAt"] = _to_seconds(start_date)
        if end_date is not None:
            params["endAt"] = _to_seconds(end_date, end_of_day=True)

        try:
            response = requests.get(
                f"{_BASE_URL}/market/candles", params=params, timeout=_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise ProviderError(
                f"Failed to download candles for '{symbol}' from KuCoin."
            ) from exc

        if payload.get("code") != "200000":
            raise ProviderError(
                f"KuCoin API error for '{symbol}': {payload.get('msg')}"
            )

        candles = payload.get("data", [])

        if not candles:
            raise ProviderError(f"No market data found for '{symbol}'.")

        df = pd.DataFrame(
            candles,
            columns=[
                "timestamp_s",
                "open",
                "close",
                "high",
                "low",
                "volume",
                "turnover",
            ],
        )
        df["datetime"] = pd.to_datetime(df["timestamp_s"].astype("int64"), unit="s")
        for column in ("open", "high", "low", "close", "volume"):
            df[column] = df[column].astype(float)

        # KuCoin returns most-recent-first.
        df = df.sort_values("datetime").reset_index(drop=True)

        return df[["datetime", "open", "high", "low", "close", "volume"]]

    def validate_symbol(self, symbol: str) -> bool:
        try:
            response = requests.get(f"{_BASE_URL}/symbols", timeout=_TIMEOUT_SECONDS)
            payload = response.json()
            symbols = {item.get("symbol") for item in payload.get("data", [])}
            return symbol in symbols
        except requests.RequestException:
            return False

    def health_check(self) -> bool:
        try:
            response = requests.get(
                "https://api.kucoin.com/api/v1/timestamp", timeout=_TIMEOUT_SECONDS
            )
            return response.status_code == 200
        except requests.RequestException:
            return False


def _to_seconds(date_str: str, *, end_of_day: bool = False) -> int:
    parsed = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
    if end_of_day:
        parsed = parsed.replace(hour=23, minute=59, second=59)
    return int(parsed.timestamp())
