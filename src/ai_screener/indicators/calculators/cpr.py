from __future__ import annotations

import pandas as pd

from ai_screener.indicators.base import Indicator
from ai_screener.indicators.timeframe import assign_period, resample_ohlcv


class CPRCalculator(Indicator):
    """Central Pivot Range.

    For a trading period (day/week/month), the CPR that applies *during*
    that period is derived from the *previous* period's own high, low,
    and close:

        pivot = (H + L + C) / 3
        bc    = (H + L) / 2            (bottom central)
        tc    = 2 * pivot - bc         (top central)
        width = |tc - bc|
        width_pct = width / pivot * 100

    A CPR is "virgin" if price during the period it applies to never
    traded inside the [bc, tc] band - i.e. the period's own [low, high]
    range does not overlap the CPR zone that was projected for it.

    ``timeframe`` selects which period's OHLC the CPR is derived from:
    "daily" (yesterday's bar -> today's CPR), "weekly", or "monthly".
    For "weekly"/"monthly", the resulting period-level CPR is broadcast
    onto every daily row within that calendar period, so the output is
    always aligned to the input's daily "datetime" index.
    """

    name = "cpr"

    def compute(  # type: ignore[override]
        self, df: pd.DataFrame, timeframe: str = "daily"
    ) -> pd.DataFrame:
        period_df = resample_ohlcv(df, timeframe)
        period_cpr = self._compute_period_cpr(period_df)

        if timeframe == "daily":
            return period_cpr

        return self._broadcast_to_daily(df, period_cpr, timeframe)

    @staticmethod
    def _compute_period_cpr(period_df: pd.DataFrame) -> pd.DataFrame:
        high = period_df["high"]
        low = period_df["low"]
        close = period_df["close"]

        raw_pivot = (high + low + close) / 3
        raw_bc = (high + low) / 2
        raw_tc = 2 * raw_pivot - raw_bc

        # The CPR applicable *to* period i comes from period i-1's own bar.
        applicable_pivot = raw_pivot.shift(1)
        applicable_bc = raw_bc.shift(1)
        applicable_tc = raw_tc.shift(1)

        width = (applicable_tc - applicable_bc).abs()
        width_pct = width / applicable_pivot * 100

        # TC is not guaranteed to be >= BC (it can invert when the close
        # sits near the low), so compare against the band's actual
        # low/high bounds rather than assuming tc is always the top.
        band_low = pd.concat([applicable_bc, applicable_tc], axis=1).min(axis=1)
        band_high = pd.concat([applicable_bc, applicable_tc], axis=1).max(axis=1)
        overlaps_cpr_band = (low <= band_high) & (high >= band_low)
        # The first period has no prior bar to derive a CPR from; leave
        # "virgin" undefined (NaN) there instead of a misleading True/False.
        virgin = (~overlaps_cpr_band).where(applicable_pivot.notna())

        return pd.DataFrame(
            {
                "datetime": period_df["datetime"],
                "pivot": applicable_pivot,
                "bc": applicable_bc,
                "tc": applicable_tc,
                "width": width,
                "width_pct": width_pct,
                "virgin": virgin,
            }
        )

    @staticmethod
    def _broadcast_to_daily(
        daily_df: pd.DataFrame,
        period_cpr: pd.DataFrame,
        timeframe: str,
    ) -> pd.DataFrame:
        daily = pd.DataFrame({"datetime": daily_df["datetime"]})
        daily["_period"] = assign_period(daily_df, timeframe)

        period_cpr = period_cpr.copy()
        period_cpr["_period"] = assign_period(period_cpr, timeframe)

        merged = daily.merge(
            period_cpr.drop(columns=["datetime"]), on="_period", how="left"
        )

        return merged.drop(columns=["_period"])
