from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import requests

from ai_screener.core.exceptions import ProviderError
from ai_screener.market_data.providers import MarketDataProvider

_BASE_URL = "https://api.bybit.com/v5"
_TIMEOUT_SECONDS = 15
_MAX_CANDLES = 1000  # Bybit's per-request limit; no pagination in V1.


class BybitProvider(MarketDataProvider):
    """Bybit implementation.

    ``symbol`` is a Bybit spot trading pair (e.g. "BTCUSDT").
    """

    @property
    def provider_name(self) -> str:
        return "bybit"

    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        params: dict[str, str | int] = {
            "category": "spot",
            "symbol": symbol,
            "interval": "D",
            "limit": _MAX_CANDLES,
        }
        if start_date is not None:
            params["start"] = _to_ms(start_date)
        if end_date is not None:
            params["end"] = _to_ms(end_date, end_of_day=True)

        try:
            response = requests.get(
                f"{_BASE_URL}/market/kline", params=params, timeout=_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise ProviderError(
                f"Failed to download klines for '{symbol}' from Bybit."
            ) from exc

        if payload.get("retCode") != 0:
            raise ProviderError(
                f"Bybit API error for '{symbol}': {payload.get('retMsg')}"
            )

        candles = payload.get("result", {}).get("list", [])

        if not candles:
            raise ProviderError(f"No market data found for '{symbol}'.")

        df = pd.DataFrame(
            candles,
            columns=[
                "timestamp_ms",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover",
            ],
        )
        df["datetime"] = pd.to_datetime(df["timestamp_ms"].astype("int64"), unit="ms")
        for column in ("open", "high", "low", "close", "volume"):
            df[column] = df[column].astype(float)

        # Bybit returns most-recent-first.
        df = df.sort_values("datetime").reset_index(drop=True)

        return df[["datetime", "open", "high", "low", "close", "volume"]]

    def validate_symbol(self, symbol: str) -> bool:
        try:
            response = requests.get(
                f"{_BASE_URL}/market/instruments-info",
                params={"category": "spot", "symbol": symbol},
                timeout=_TIMEOUT_SECONDS,
            )
            payload = response.json()
            return bool(payload.get("result", {}).get("list"))
        except requests.RequestException:
            return False

    def health_check(self) -> bool:
        try:
            response = requests.get(
                f"{_BASE_URL}/market/time", timeout=_TIMEOUT_SECONDS
            )
            return response.status_code == 200
        except requests.RequestException:
            return False


def _to_ms(date_str: str, *, end_of_day: bool = False) -> int:
    parsed = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
    if end_of_day:
        parsed = parsed.replace(hour=23, minute=59, second=59)
    return int(parsed.timestamp() * 1000)
