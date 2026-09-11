from __future__ import annotations

from typing import Any

import pandas as pd

from ai_screener.indicators.registry import IndicatorRegistry
from ai_screener.market_data.services import MarketDataService

#: Default indicator selection when a caller doesn't specify one.
# CPR is computed at all three product-relevant timeframes; the rest use
# their calculators' own defaults.
DEFAULT_INDICATORS: dict[str, dict[str, Any]] = {
    "cpr_daily": {"name": "cpr", "params": {"timeframe": "daily"}},
    "cpr_weekly": {"name": "cpr", "params": {"timeframe": "weekly"}},
    "cpr_monthly": {"name": "cpr", "params": {"timeframe": "monthly"}},
    "ema": {"name": "ema", "params": {}},
    "rsi": {"name": "rsi", "params": {}},
    "atr": {"name": "atr", "params": {}},
    "macd": {"name": "macd", "params": {}},
}


class IndicatorService:
    """Computes indicator snapshots for a symbol from persisted market data.

    Reads through MarketDataService.get_history() - never the repository
    directly - so it shares the same public read path as every other
    downstream module (scanner, dashboard, backtesting).

    Indicator values are computed on demand rather than persisted; this
    keeps Sprint 2 simple and can be revisited if scanning performance
    over many symbols later requires caching.
    """

    def __init__(
        self,
        market_data_service: MarketDataService,
        registry: type[IndicatorRegistry] = IndicatorRegistry,
    ) -> None:
        self._market_data_service = market_data_service
        self._registry = registry

    def compute(
        self,
        symbol: str,
        asset_type: str = "equity",
        indicators: dict[str, dict[str, Any]] | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """Return a daily-aligned DataFrame of computed indicator values.

        ``indicators`` maps an output-column-prefix to
        ``{"name": <registered indicator name>, "params": {...}}``. Pass
        ``None`` to compute the product's default indicator set
        (DEFAULT_INDICATORS).

        ``end_date`` ("YYYY-MM-DD") restricts the history used to compute
        indicators to that date and earlier - point-in-time computation,
        so backtesting (Sprint 6) can ask "what would this indicator have
        read as of this historical day" without any look-ahead into
        future bars.
        """

        history = self._market_data_service.get_history(
            symbol, asset_type, end_date=end_date
        )

        if history.empty:
            return pd.DataFrame(columns=["datetime"])

        selection = indicators if indicators is not None else DEFAULT_INDICATORS

        result = history[["datetime"]].copy()

        for prefix, spec in selection.items():
            calculator = self._registry.get(spec["name"])
            computed = calculator.compute(history, **spec.get("params", {}))
            computed = computed.rename(
                columns={
                    column: f"{prefix}_{column}"
                    for column in computed.columns
                    if column != "datetime"
                }
            )
            result = result.merge(computed, on="datetime", how="left")

        return result

    def latest(
        self,
        symbol: str,
        asset_type: str = "equity",
        indicators: dict[str, dict[str, Any]] | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Return the most recent row of compute() as a flat dict."""

        snapshot = self.compute(symbol, asset_type, indicators, end_date=end_date)

        if snapshot.empty:
            return {}

        return {str(key): value for key, value in snapshot.iloc[-1].to_dict().items()}
