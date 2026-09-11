from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ScanContext:
    """Everything a Condition needs to evaluate one symbol.

    ``history`` is the full persisted OHLCV history (ascending by
    datetime); ``indicators`` is that symbol's latest indicator snapshot
    (see IndicatorService.latest()) keyed by output column name, e.g.
    "cpr_monthly_width_pct", "ema_ema_20", "rsi_rsi_14".
    """

    symbol: str
    history: pd.DataFrame
    indicators: dict[str, Any]
