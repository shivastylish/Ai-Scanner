from __future__ import annotations

import pandas as pd

# Resample rules for turning daily bars into higher timeframes.
# "W-FRI": weeks ending Friday (NSE's last trading day of the week).
# "ME": calendar month-end (pandas' modern month-end alias).
TIMEFRAME_RESAMPLE_RULES: dict[str, str] = {
    "weekly": "W-FRI",
    "monthly": "ME",
}

# Rules for bucketing individual daily rows into the same higher-timeframe
# period as a resampled period-end row, via Series.dt.to_period(). Using
# pandas' calendar week/month periods here (rather than the resample
# anchor above) keeps bucketing robust regardless of which weekday the
# resampled period label falls on.
TIMEFRAME_PERIOD_RULES: dict[str, str] = {
    "weekly": "W",
    "monthly": "M",
}

_AGGREGATION = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
}


def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Resample daily OHLCV bars into a higher timeframe.

    Returns a DataFrame with a "datetime" column (the period end) plus
    open/high/low/close/volume aggregated over that period. Periods with
    no trading data are dropped.
    """

    if timeframe == "daily":
        return df.copy()

    if timeframe not in TIMEFRAME_RESAMPLE_RULES:
        raise ValueError(f"Unsupported timeframe: '{timeframe}'.")

    indexed = df.set_index(pd.to_datetime(df["datetime"]))

    resampled = indexed.resample(TIMEFRAME_RESAMPLE_RULES[timeframe]).agg(
        _AGGREGATION  # type: ignore[arg-type]
    )
    resampled = resampled.dropna(subset=["open", "high", "low", "close"])

    return resampled.reset_index()


def assign_period(df: pd.DataFrame, timeframe: str) -> pd.Series:
    """Return the pandas Period each row's "datetime" falls into.

    Used to broadcast a higher-timeframe indicator value (e.g. weekly
    CPR) onto every daily row within that same calendar period.
    """

    if timeframe not in TIMEFRAME_PERIOD_RULES:
        raise ValueError(f"Unsupported timeframe: '{timeframe}'.")

    return pd.to_datetime(df["datetime"]).dt.to_period(
        TIMEFRAME_PERIOD_RULES[timeframe]
    )
