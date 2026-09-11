from __future__ import annotations

from typing import Any

import pandas as pd
import requests

from ai_screener.config.settings import settings
from ai_screener.core.exceptions import ProviderError
from ai_screener.market_data.providers import MarketDataProvider

_BASE_URL = "https://pro-api.coinmarketcap.com/v2"
_TIMEOUT_SECONDS = 15


class CoinMarketCapProvider(MarketDataProvider):
    """CoinMarketCap implementation.

    ``symbol`` is a CoinMarketCap ticker symbol (e.g. "BTC").

    Verification note: unlike every other provider in this codebase,
    this one is implemented against CoinMarketCap's *documented* OHLCV
    historical endpoint contract but has not been exercised against the
    live API - the free tier requires an API key
    (``COINMARKETCAP_API_KEY`` in ``.env``) that wasn't available while
    building this. The hermetic unit test asserts against the documented
    response shape; the live test (``@pytest.mark.live``) is skipped
    automatically when no key is configured and will genuinely validate
    (or reveal a wrong assumption about) this implementation the first
    time it runs with a real key.
    """

    @property
    def provider_name(self) -> str:
        return "coinmarketcap"

    def download_history(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        api_key = settings.COINMARKETCAP_API_KEY

        if not api_key:
            raise ProviderError(
                "COINMARKETCAP_API_KEY is not configured. Set it in .env to "
                "use the CoinMarketCap provider."
            )

        params: dict[str, str] = {"symbol": symbol, "interval": "daily"}
        if start_date is not None:
            params["time_start"] = start_date
        if end_date is not None:
            params["time_end"] = end_date

        try:
            response = requests.get(
                f"{_BASE_URL}/cryptocurrency/ohlcv/historical",
                params=params,
                headers={
                    "X-CMC_PRO_API_KEY": api_key,
                    "Accept": "application/json",
                },
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise ProviderError(
                f"Failed to download OHLCV history for '{symbol}' from "
                "CoinMarketCap."
            ) from exc

        quotes = _extract_quotes(payload, symbol)

        if not quotes:
            raise ProviderError(f"No market data found for '{symbol}'.")

        rows = [
            {
                "datetime": quote["time_open"],
                "open": quote["quote"]["USD"]["open"],
                "high": quote["quote"]["USD"]["high"],
                "low": quote["quote"]["USD"]["low"],
                "close": quote["quote"]["USD"]["close"],
                "volume": quote["quote"]["USD"]["volume"],
            }
            for quote in quotes
        ]

        df = pd.DataFrame(rows)
        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)

        return df.sort_values("datetime").reset_index(drop=True)

    def validate_symbol(self, symbol: str) -> bool:
        if not settings.COINMARKETCAP_API_KEY:
            return False

        try:
            response = requests.get(
                f"{_BASE_URL}/cryptocurrency/info",
                params={"symbol": symbol},
                headers={"X-CMC_PRO_API_KEY": settings.COINMARKETCAP_API_KEY},
                timeout=_TIMEOUT_SECONDS,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def health_check(self) -> bool:
        if not settings.COINMARKETCAP_API_KEY:
            return False

        try:
            response = requests.get(
                f"{_BASE_URL.replace('/v2', '/v1')}/key/info",
                headers={"X-CMC_PRO_API_KEY": settings.COINMARKETCAP_API_KEY},
                timeout=_TIMEOUT_SECONDS,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False


def _extract_quotes(payload: dict[str, Any], symbol: str) -> list[dict[str, Any]]:
    """CoinMarketCap's v2 response nests `data[symbol]` as a list (a
    symbol can map to more than one coin id); take the first entry's
    quotes, the documented shape for an unambiguous ticker."""

    entries = payload.get("data", {}).get(symbol, [])

    if not entries:
        return []

    first_entry = entries[0] if isinstance(entries, list) else entries
    quotes = first_entry.get("quotes", [])
    return list(quotes)
