from __future__ import annotations

import pandas as pd
import requests

from ai_screener.core.exceptions import ProviderError

_BASE_URL = "https://api.mfapi.in/mf"
_TIMEOUT_SECONDS = 15

# A large, long-running scheme used only as a stable health-check target
# (mfapi.in has no dedicated ping/status endpoint) - mirrors
# YahooFinanceProvider's use of "^NSEI" for the same purpose.
_HEALTH_CHECK_SCHEME_CODE = "119551"


class MFAPIProvider:
    """Raw fetch layer for mfapi.in mutual fund NAV history.

    Deliberately not a MarketDataProvider: NAV data doesn't fit the
    OHLCV schema (see market_data/models/fund_nav_schema.py), so this is
    its own small stack, not a variant of the equity/crypto one.
    """

    @property
    def provider_name(self) -> str:
        return "mfapi"

    def download_history(
        self,
        scheme_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        try:
            response = requests.get(
                f"{_BASE_URL}/{scheme_code}", timeout=_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise ProviderError(
                f"Failed to download NAV history for scheme '{scheme_code}' "
                "from mfapi.in."
            ) from exc

        records = payload.get("data") or []

        if not records:
            raise ProviderError(f"No NAV data found for scheme '{scheme_code}'.")

        meta = payload.get("meta", {})

        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        df["nav"] = df["nav"].astype(float)
        df["scheme_name"] = meta.get("scheme_name", "")
        df["fund_house"] = meta.get("fund_house", "")

        # mfapi.in returns most-recent-first; the rest of the codebase
        # expects ascending-by-date history.
        df = df.sort_values("date").reset_index(drop=True)

        if start_date is not None:
            df = df[df["date"] >= pd.to_datetime(start_date)]
        if end_date is not None:
            df = df[df["date"] <= pd.to_datetime(end_date)]

        return df.reset_index(drop=True)

    def health_check(self) -> bool:
        try:
            response = requests.get(
                f"{_BASE_URL}/{_HEALTH_CHECK_SCHEME_CODE}", timeout=_TIMEOUT_SECONDS
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
