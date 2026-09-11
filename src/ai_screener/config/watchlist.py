from __future__ import annotations

import json
from pathlib import Path

#: The scanner's V1 symbol universe: a configured watchlist rather than a
#: full NSE symbol-master feed (deferred to a later ticket - see the
#: roadmap doc). A representative slice of large, liquid NSE equities.
DEFAULT_WATCHLIST: list[str] = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "HINDUNILVR.NS",
    "ITC.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "KOTAKBANK.NS",
]

#: Optional override: a JSON file containing a flat list of symbols,
#: e.g. ["RELIANCE.NS", "TCS.NS", ...]. Lets the watchlist be edited
#: without a code change.
WATCHLIST_OVERRIDE_PATH = Path("config") / "watchlist.json"


def get_watchlist() -> list[str]:
    """Return the configured scan universe.

    Reads config/watchlist.json when present, otherwise falls back to
    DEFAULT_WATCHLIST.
    """

    if WATCHLIST_OVERRIDE_PATH.exists():
        symbols = json.loads(WATCHLIST_OVERRIDE_PATH.read_text(encoding="utf-8"))
        return list(symbols)

    return list(DEFAULT_WATCHLIST)
